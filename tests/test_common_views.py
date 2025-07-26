from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.response import Response
from unittest.mock import Mock, patch

# Functions under test live in common/views.py
from common.views import (
    process_serializer,
    add_user,
    user_login,
    resend_user_otp,
    log_user_out,
)

###############################################################################
# process_serializer
###############################################################################
class ProcessSerializerTests(TestCase):
    def setUp(self):
        self.mock_serializer_cls = Mock()
        self.data = {"field": "value"}
        self.instance = Mock()

    def _make_serializer(self, *, is_valid=True, data=None, save_side_effect=None):
        """Helper that fabricates and wires a fake serializer instance."""
        ser = Mock()
        ser.is_valid.return_value = is_valid
        ser.data = data or {"id": 1, "field": "value"}
        if save_side_effect:
            ser.save.side_effect = save_side_effect
        self.mock_serializer_cls.return_value = ser
        return ser

    def test_create_success(self):
        serializer = self._make_serializer()
        result, code = process_serializer(self.mock_serializer_cls, self.data)
        self.assertEqual(result, serializer.data)
        self.assertEqual(code, status.HTTP_201_CREATED)
        self.mock_serializer_cls.assert_called_once_with(data=self.data)
        serializer.save.assert_called_once()

    def test_update_success(self):
        self._make_serializer()
        result, code = process_serializer(
            self.mock_serializer_cls, self.data, instance=self.instance
        )
        self.assertEqual(code, status.HTTP_200_OK)
        self.mock_serializer_cls.assert_called_once_with(self.instance, data=self.data)

    def test_validation_error(self):
        serializer = self._make_serializer(is_valid=False)
        result, code = process_serializer(self.mock_serializer_cls, self.data)
        self.assertEqual(result, serializer.errors)
        self.assertEqual(code, status.HTTP_400_BAD_REQUEST)
        serializer.save.assert_not_called()

    def test_save_exception(self):
        self._make_serializer(save_side_effect=Exception("db error"))
        result, code = process_serializer(self.mock_serializer_cls, self.data)
        self.assertEqual(result, {"error": "db error"})
        self.assertEqual(code, status.HTTP_500_INTERNAL_SERVER_ERROR)


###############################################################################
# add_user (wrapper around process_serializer)
###############################################################################
class AddUserTests(TestCase):
    @patch("common.views.process_serializer")
    def test_add_user_forwards_response(self, mock_proc):
        mock_proc.return_value = ({"ok": True}, status.HTTP_201_CREATED)
        resp = add_user({"x": "y"}, Mock())
        self.assertIsInstance(resp, Response)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data, {"ok": True})
        mock_proc.assert_called_once()


###############################################################################
# user_login (the heaviest branchy helper)
###############################################################################
class UserLoginTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_cls = Mock()
        self.user_obj = Mock()
        self.user_obj.is_active = True
        self.user_obj.email = "u@example.com"
        self.user_obj.get_username.return_value = "u@example.com"

    def _request(self, data):
        r = self.factory.post("/login/", data)
        r.data = data
        return r

    def test_missing_password(self):
        resp = user_login(self._request({"username": "u"}), self.model_cls)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_credentials_lookup(self):
        self.model_cls.objects.get.side_effect = self.model_cls.DoesNotExist
        resp = user_login(
            self._request({"username": "none", "password": "pw"}), self.model_cls
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("common.views.authenticate")
    @patch("common.views.login")
    @patch("common.views.get_token")
    def test_buyer_happy_path(
        self, mock_token, mock_login_func, mock_authenticate
    ):
        self.model_cls.objects.get.return_value = self.user_obj
        self.user_obj.buyer = Mock(is_verified=True)
        mock_authenticate.return_value = self.user_obj
        mock_token.return_value = "csrf123"

        resp = user_login(
            self._request({"username": "u", "password": "pw"}), self.model_cls, "buyer"
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_login_func.assert_called_once_with(resp.wsgi_request, self.user_obj)
        self.assertEqual(resp.data["csrf_token"], "csrf123")

    def test_profile_not_verified(self):
        self.model_cls.objects.get.return_value = self.user_obj
        self.user_obj.buyer = Mock(is_verified=False)
        resp = user_login(
            self._request({"username": "u", "password": "pw"}), self.model_cls, "buyer"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


###############################################################################
# verify_user  (only a couple of critical branches)
###############################################################################
class VerifyUserTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_cls = Mock()
        self.email = "test@example.com"
        self.otp = "123456"

    def _req(self, data=None):
        data = data or {"otp": self.otp}
        r = self.factory.post("/verify/", data)
        r.data = data
        r.META["REMOTE_ADDR"] = "1.2.3.4"
        return r

    def test_missing_params(self):
        from common.views import verify_user
        resp = verify_user(self._req({}), None, self.model_cls)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("common.views.is_ip_throttled", return_value=True)
    def test_ip_throttled(self, _mock_throttle):
        from common.views import verify_user
        resp = verify_user(self._req(), self.email, self.model_cls)
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


###############################################################################
# resend_user_otp
###############################################################################
class ResendOtpTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_cls = Mock()
        self.email = "t@example.com"

    def _req(self):
        r = self.factory.get("/resend/")
        r.META["REMOTE_ADDR"] = "7.7.7.7"
        return r

    @patch("common.views.is_ip_throttled", return_value=True)
    def test_ip_blocked(self, _mock_thr):
        resp = resend_user_otp(self._req(), self.email, self.model_cls)
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    @patch("common.views.is_ip_throttled", return_value=False)
    @patch("common.views.can_resend_otp", return_value=True)
    @patch("common.views.send_otp")
    def test_happy_path(self, mock_send, *_):
        # model.objects.get returns a dummy user with a profile attribute
        dummy_user = Mock()
        dummy_user.user = Mock()
        self.model_cls.objects.get.return_value = dummy_user

        resp = resend_user_otp(self._req(), self.email, self.model_cls)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        mock_send.assert_called_once_with(self.email, is_resend=True)


###############################################################################
# log_user_out (simple wrapper around django.contrib.auth.logout)
###############################################################################
class LogoutTests(TestCase):
    @patch("common.views.logout")
    def test_logout_calls_django_and_returns_200(self, mock_logout):
        rf = RequestFactory()
        req = rf.post("/logout/")
        resp = log_user_out(req)
        mock_logout.assert_called_once_with(req)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)