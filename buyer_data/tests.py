from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers
from unittest.mock import Mock, patch
import io

# Import the serializer and models we're testing
from buyer_data.serializers import BuyerSerializer
import buyer_data.models as models
from common.serializer import BaseUserSerializer
from common.models import CustomUser


class TestBuyerSerializer(TestCase):
    """
    Comprehensive unit tests for BuyerSerializer.
    Testing framework: Django TestCase with focus on serializer validation and behavior.
    """
    
    def setUp(self):
        """Set up test data and mock objects."""
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe', 
            'email': 'john.doe@example.com',
            'username': 'johndoe',
            'password': 'securepassword123',
            'phone_number': 1234567890
        }
        
        self.verification_data = {
            'aadhaar_number': 123456789012,
            'pan_number': 'ABCDE1234F'
        }
        
        self.complete_data = {**self.user_data, **self.verification_data}
        
        # Create mock image files
        self.aadhaar_image = self._create_test_image('aadhaar.jpg')
        self.pan_image = self._create_test_image('pan.jpg')
        
        # Create mock user and buyer instances
        self.mock_user = Mock(spec=CustomUser)
        self.mock_user.first_name = 'John'
        self.mock_user.last_name = 'Doe'
        self.mock_user.email = 'john.doe@example.com'
        self.mock_user.username = 'johndoe'
        
        self.mock_buyer = Mock(spec=models.Buyer)
        self.mock_buyer.id = 1
        self.mock_buyer.user = self.mock_user
        self.mock_buyer.phone_number = 1234567890
        self.mock_buyer.profile_picture = None
        
    def _create_test_image(self, filename):
        """Helper method to create test image files."""
        try:
            from PIL import Image
            image = Image.new('RGB', (100, 100), color='red')
            image_io = io.BytesIO()
            image.save(image_io, format='JPEG')
            image_io.seek(0)
            return SimpleUploadedFile(filename, image_io.getvalue(), content_type='image/jpeg')
        except ImportError:
            # If PIL is not available, create a simple mock file
            return SimpleUploadedFile(filename, b'fake image content', content_type='image/jpeg')
    
    def test_serializer_fields_definition(self):
        """Test that all required fields are properly defined in the serializer."""
        serializer = BuyerSerializer()
        expected_fields = {
            'id', 'first_name', 'last_name', 'email', 'phone_number', 
            'username', 'password', 'aadhaar_number', 'pan_number', 
            'aadhaar_card', 'pan_card', 'profile_picture'
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)
        
    def test_field_properties_for_creation(self):
        """Test field properties when serializer is used for creation (no instance)."""
        serializer = BuyerSerializer()
        
        # Write-only fields
        self.assertTrue(serializer.fields['aadhaar_number'].write_only)
        self.assertTrue(serializer.fields['pan_number'].write_only)
        self.assertTrue(serializer.fields['aadhaar_card'].write_only)
        self.assertTrue(serializer.fields['pan_card'].write_only)
        
        # Source fields
        self.assertEqual(serializer.fields['first_name'].source, 'user.first_name')
        self.assertEqual(serializer.fields['last_name'].source, 'user.last_name')
        self.assertEqual(serializer.fields['email'].source, 'user.email')
        self.assertEqual(serializer.fields['username'].source, 'user.username')
        
        # Required fields for creation
        self.assertTrue(serializer.fields['aadhaar_number'].required)
        self.assertTrue(serializer.fields['pan_number'].required)
        
    def test_field_properties_for_update(self):
        """Test field properties when serializer is used for update (with instance)."""
        serializer = BuyerSerializer(instance=self.mock_buyer)
        
        # Fields should not be required for updates
        self.assertFalse(serializer.fields['aadhaar_number'].required)
        self.assertFalse(serializer.fields['pan_number'].required)
        
    def test_validate_success_with_required_fields(self):
        """Test successful validation when all required fields are provided for creation."""
        serializer = BuyerSerializer()
        attrs = self.complete_data.copy()
        
        validated_attrs = serializer.validate(attrs)
        self.assertEqual(validated_attrs, attrs)
        
    def test_validate_fails_missing_aadhaar_number(self):
        """Test validation failure when aadhaar_number is missing during creation."""
        serializer = BuyerSerializer()
        attrs = self.complete_data.copy()
        del attrs['aadhaar_number']
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(attrs)
        
        self.assertIn('aadhaar_number', context.exception.detail)
        self.assertEqual(
            context.exception.detail['aadhaar_number'], 
            'This field is required during creation.'
        )
        
    def test_validate_fails_missing_pan_number(self):
        """Test validation failure when pan_number is missing during creation."""
        serializer = BuyerSerializer()
        attrs = self.complete_data.copy()
        del attrs['pan_number']
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(attrs)
        
        self.assertIn('pan_number', context.exception.detail)
        self.assertEqual(
            context.exception.detail['pan_number'], 
            'This field is required during creation.'
        )
        
    def test_validate_fails_empty_aadhaar_number(self):
        """Test validation failure when aadhaar_number is empty during creation."""
        serializer = BuyerSerializer()
        attrs = self.complete_data.copy()
        attrs['aadhaar_number'] = None
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(attrs)
        
        self.assertIn('aadhaar_number', context.exception.detail)
        
    def test_validate_fails_empty_pan_number(self):
        """Test validation failure when pan_number is empty during creation."""
        serializer = BuyerSerializer()
        attrs = self.complete_data.copy()
        attrs['pan_number'] = ''
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(attrs)
        
        self.assertIn('pan_number', context.exception.detail)
        
    def test_validate_skips_validation_for_updates(self):
        """Test that validation is skipped when updating existing instance."""
        serializer = BuyerSerializer(instance=self.mock_buyer)
        attrs = {'first_name': 'Jane'}  # Missing aadhaar_number and pan_number
        
        # Should not raise validation error for updates
        validated_attrs = serializer.validate(attrs)
        self.assertEqual(validated_attrs, attrs)
        
    @patch.object(BaseUserSerializer, 'create_user')
    def test_create_success_with_all_fields(self, mock_create_user):
        """Test successful creation with all fields including image uploads."""
        mock_buyer = Mock()
        mock_create_user.return_value = mock_buyer
        
        validated_data = self.complete_data.copy()
        validated_data['aadhaar_card'] = self.aadhaar_image
        validated_data['pan_card'] = self.pan_image
        
        serializer = BuyerSerializer()
        result = serializer.create(validated_data)
        
        # Verify the result
        self.assertEqual(result, mock_buyer)
        
        # Verify create_user was called with correct parameters
        mock_create_user.assert_called_once()
        call_args = mock_create_user.call_args[0]
        
        # Check that verification data was extracted and added
        self.assertIn('buyerverification', call_args[0])
        verification_data = call_args[0]['buyerverification']
        
        self.assertEqual(verification_data['aadhaar_number'], 123456789012)
        self.assertEqual(verification_data['pan_number'], 'ABCDE1234F')
        self.assertEqual(verification_data['aadhaar_card'], self.aadhaar_image)
        self.assertEqual(verification_data['pan_card'], self.pan_image)
        
        # Check other parameters
        self.assertEqual(call_args[1], models.Buyer)
        self.assertEqual(call_args[2], models.BuyerVerification)
        self.assertEqual(call_args[3], 'buyerverification')
        
    @patch.object(BaseUserSerializer, 'create_user')
    def test_create_success_without_optional_images(self, mock_create_user):
        """Test successful creation without optional image fields."""
        mock_buyer = Mock()
        mock_create_user.return_value = mock_buyer
        
        validated_data = self.complete_data.copy()
        
        serializer = BuyerSerializer()
        result = serializer.create(validated_data)
        
        # Verify the result
        self.assertEqual(result, mock_buyer)
        
        # Verify create_user was called
        mock_create_user.assert_called_once()
        call_args = mock_create_user.call_args[0]
        
        # Check that verification data has None for optional fields
        verification_data = call_args[0]['buyerverification']
        self.assertIsNone(verification_data['aadhaar_card'])
        self.assertIsNone(verification_data['pan_card'])
        
    @patch.object(BaseUserSerializer, 'update_user')
    def test_update_success(self, mock_update_user):
        """Test successful update operation."""
        updated_buyer = Mock()
        mock_update_user.return_value = updated_buyer
        
        validated_data = {
            'first_name': 'Jane',
            'phone_number': 9876543210
        }
        
        serializer = BuyerSerializer(instance=self.mock_buyer)
        result = serializer.update(self.mock_buyer, validated_data)
        
        # Verify the result
        self.assertEqual(result, updated_buyer)
        
        # Verify update_user was called with correct parameters
        mock_update_user.assert_called_once_with(
            self.mock_buyer,
            validated_data,
            'buyerverification'
        )
        
    def test_field_types(self):
        """Test that fields have correct types and properties."""
        serializer = BuyerSerializer()
        
        # Integer field
        self.assertIsInstance(
            serializer.fields['aadhaar_number'], 
            serializers.IntegerField
        )
        
        # Character field
        self.assertIsInstance(
            serializer.fields['pan_number'], 
            serializers.CharField
        )
        
        # Email field
        self.assertIsInstance(
            serializer.fields['email'], 
            serializers.EmailField
        )
        
        # Image fields
        self.assertIsInstance(
            serializer.fields['aadhaar_card'], 
            serializers.ImageField
        )
        self.assertIsInstance(
            serializer.fields['pan_card'], 
            serializers.ImageField
        )
        self.assertIsInstance(
            serializer.fields['profile_picture'], 
            serializers.ImageField
        )
        
    def test_meta_class_inheritance(self):
        """Test that Meta class correctly inherits from BaseUserSerializer.Meta."""
        self.assertEqual(BuyerSerializer.Meta.model, models.Buyer)
        self.assertTrue(hasattr(BuyerSerializer.Meta, '__bases__'))
        
    def test_error_handling_in_validate(self):
        """Test error handling edge cases in validate method."""
        serializer = BuyerSerializer()
        
        # Test with various falsy values
        falsy_values = [None, '', 0, False, []]
        
        for value in falsy_values:
            attrs = self.complete_data.copy()
            attrs['aadhaar_number'] = value
            
            with self.assertRaises(serializers.ValidationError):
                serializer.validate(attrs)
                
    def test_validate_with_zero_aadhaar_number(self):
        """Test validation specifically with zero aadhaar_number."""
        serializer = BuyerSerializer()
        attrs = self.complete_data.copy()
        attrs['aadhaar_number'] = 0
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(attrs)
        
        self.assertIn('aadhaar_number', context.exception.detail)
        
    def test_create_data_extraction(self):
        """Test that create method correctly extracts and organizes data."""
        serializer = BuyerSerializer()
        
        original_data = self.complete_data.copy()
        original_data['aadhaar_card'] = self.aadhaar_image
        original_data['pan_card'] = self.pan_image
        original_data['extra_field'] = 'should_remain'
        
        # Mock the BaseUserSerializer.create_user to capture the call
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_create_user.return_value = Mock()
            
            serializer.create(original_data)
            
            # Verify that verification fields were removed from main data
            call_args = mock_create_user.call_args[0]
            main_data = call_args[0]
            
            # Verification fields should not be in main data
            self.assertNotIn('aadhaar_number', main_data)
            self.assertNotIn('pan_number', main_data)
            self.assertNotIn('aadhaar_card', main_data)
            self.assertNotIn('pan_card', main_data)
            
            # But other fields should remain
            self.assertIn('extra_field', main_data)
            self.assertEqual(main_data['extra_field'], 'should_remain')
            
            # Verification data should be properly structured
            verification_data = main_data['buyerverification']
            self.assertIn('aadhaar_number', verification_data)
            self.assertIn('pan_number', verification_data)
            self.assertIn('aadhaar_card', verification_data)
            self.assertIn('pan_card', verification_data)


class TestBuyerSerializerEdgeCases(TestCase):
    """
    Edge case tests for BuyerSerializer.
    Testing framework: Django TestCase with focus on boundary conditions and error scenarios.
    """
    
    def setUp(self):
        """Set up test data for edge case tests."""
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'username': 'johndoe',
            'password': 'securepassword123',
            'phone_number': 1234567890,
            'aadhaar_number': 123456789012,
            'pan_number': 'ABCDE1234F'
        }
    
    def test_large_aadhaar_number(self):
        """Test validation with maximum valid aadhaar number."""
        serializer = BuyerSerializer()
        attrs = {
            'aadhaar_number': 999999999999,  # 12 digits max
            'pan_number': 'ABCDE1234F',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Should not raise validation error
        result = serializer.validate(attrs)
        self.assertEqual(result, attrs)
        
    def test_invalid_pan_format_handling(self):
        """Test handling of various PAN number formats."""
        serializer = BuyerSerializer()
        
        # PAN validation might be handled at field level or model level
        # Test that serializer doesn't break with different formats
        pan_formats = ['ABCDE1234F', 'abcde1234f', 'ABC1234', '']
        
        for pan in pan_formats:
            attrs = {
                'aadhaar_number': 123456789012,
                'pan_number': pan,
                'first_name': 'Test',
                'last_name': 'User'
            }
            
            if pan:  # Non-empty PAN
                result = serializer.validate(attrs)
                self.assertEqual(result['pan_number'], pan)
            else:  # Empty PAN should fail validation
                with self.assertRaises(serializers.ValidationError):
                    serializer.validate(attrs)
                    
    @patch.object(BaseUserSerializer, 'create_user')
    def test_create_with_exception_handling(self, mock_create_user):
        """Test create method behavior when BaseUserSerializer raises exception."""
        mock_create_user.side_effect = Exception("Database error")
        
        validated_data = {
            'aadhaar_number': 123456789012,
            'pan_number': 'ABCDE1234F',
            'first_name': 'Test'
        }
        
        serializer = BuyerSerializer()
        
        with self.assertRaises(Exception) as context:
            serializer.create(validated_data)
        
        self.assertEqual(str(context.exception), "Database error")
        
    @patch.object(BaseUserSerializer, 'update_user')
    def test_update_with_exception_handling(self, mock_update_user):
        """Test update method behavior when BaseUserSerializer raises exception."""
        mock_update_user.side_effect = Exception("Update failed")
        
        mock_buyer = Mock()
        validated_data = {'first_name': 'Updated'}
        
        serializer = BuyerSerializer(instance=mock_buyer)
        
        with self.assertRaises(Exception) as context:
            serializer.update(mock_buyer, validated_data)
        
        self.assertEqual(str(context.exception), "Update failed")

    def test_validate_with_boolean_false_values(self):
        """Test validation with boolean False values which are falsy but might be valid."""
        serializer = BuyerSerializer()
        attrs = self.valid_data.copy()
        attrs['aadhaar_number'] = False  # Boolean False is falsy but not None
        
        with self.assertRaises(serializers.ValidationError):
            serializer.validate(attrs)
    
    def test_validate_with_empty_list_values(self):
        """Test validation with empty list values which are falsy."""
        serializer = BuyerSerializer()
        attrs = self.valid_data.copy()
        attrs['pan_number'] = []  # Empty list is falsy
        
        with self.assertRaises(serializers.ValidationError):
            serializer.validate(attrs)

    def test_aadhaar_number_boundary_values(self):
        """Test aadhaar number validation with boundary values."""
        serializer = BuyerSerializer()
        
        # Test minimum valid 12-digit aadhaar number
        attrs = self.valid_data.copy()
        attrs['aadhaar_number'] = 100000000000  # 12 digits minimum
        
        result = serializer.validate(attrs)
        self.assertEqual(result['aadhaar_number'], 100000000000)
        
        # Test 11-digit number (should still pass serializer validation, model might reject)
        attrs['aadhaar_number'] = 12345678901  # 11 digits
        result = serializer.validate(attrs)
        self.assertEqual(result['aadhaar_number'], 12345678901)

    def test_create_method_data_mutation(self):
        """Test that create method properly mutates the validated_data."""
        serializer = BuyerSerializer()
        
        original_data = {
            'aadhaar_number': 123456789012,
            'pan_number': 'ABCDE1234F',
            'aadhaar_card': self._create_test_image('test.jpg'),
            'pan_card': self._create_test_image('test2.jpg'),
            'first_name': 'John',
            'phone_number': 1234567890
        }
        
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_create_user.return_value = Mock()
            
            serializer.create(original_data)
            
            # Verify that the original data was mutated (verification fields removed)
            self.assertNotIn('aadhaar_number', original_data)
            self.assertNotIn('pan_number', original_data)
            self.assertNotIn('aadhaar_card', original_data)
            self.assertNotIn('pan_card', original_data)
            
            # But other fields should remain
            self.assertIn('first_name', original_data)
            self.assertIn('phone_number', original_data)

    def _create_test_image(self, filename):
        """Helper method to create test image files."""
        try:
            from PIL import Image
            image = Image.new('RGB', (100, 100), color='red')
            image_io = io.BytesIO()
            image.save(image_io, format='JPEG')
            image_io.seek(0)
            return SimpleUploadedFile(filename, image_io.getvalue(), content_type='image/jpeg')
        except ImportError:
            # If PIL is not available, create a simple mock file
            return SimpleUploadedFile(filename, b'fake image content', content_type='image/jpeg')


class TestBuyerSerializerIntegration(TestCase):
    """
    Integration-style tests for BuyerSerializer.
    Testing framework: Django TestCase with real model interactions where appropriate.
    """
    
    def setUp(self):
        """Set up test data for integration tests."""
        self.valid_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'username': 'johndoe',
            'password': 'securepassword123',
            'phone_number': 1234567890,
            'aadhaar_number': 123456789012,
            'pan_number': 'ABCDE1234F'
        }
        
    def test_serializer_validation_flow(self):
        """Test complete validation flow from initialization to validation."""
        # Test creation flow
        create_serializer = BuyerSerializer(data=self.valid_data)
        
        # Should be valid
        self.assertTrue(create_serializer.is_valid())
        
        # Test update flow - create mock instance
        mock_buyer = Mock()
        update_serializer = BuyerSerializer(
            instance=mock_buyer, 
            data={'first_name': 'Jane'}
        )
        
        # Should be valid for update even without required fields
        self.assertTrue(update_serializer.is_valid())
        
    def test_partial_update_validation(self):
        """Test partial update scenarios."""
        mock_buyer = Mock()
        
        # Test updating only user fields
        user_data = {'first_name': 'Jane', 'last_name': 'Smith'}
        serializer = BuyerSerializer(instance=mock_buyer, data=user_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # Test updating only verification fields
        verification_data = {'aadhaar_number': 987654321098}
        serializer = BuyerSerializer(instance=mock_buyer, data=verification_data, partial=True)
        self.assertTrue(serializer.is_valid())
        
    def test_field_validation_with_invalid_data(self):
        """Test field-level validation with invalid data types."""
        invalid_data_sets = [
            # Invalid aadhaar_number type
            {**self.valid_data, 'aadhaar_number': 'not_a_number'},
            # Invalid email format
            {**self.valid_data, 'email': 'invalid_email'},
            # Invalid username (if there are restrictions)
            {**self.valid_data, 'username': ''},
        ]
        
        for invalid_data in invalid_data_sets:
            serializer = BuyerSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertTrue(len(serializer.errors) > 0)


class TestBuyerSerializerBugDocumentation(TestCase):
    """
    Tests documenting and verifying the bug in the __init__ method.
    Testing framework: Django TestCase focused on documenting current behavior.
    """
    
    def test_init_bug_with_nonexistent_fields(self):
        """
        Test documenting the bug where __init__ tries to set required=True 
        on non-existent fields 'email_number' and 'username_number'.
        
        This test documents the current buggy behavior and will need to be 
        updated when the bug is fixed.
        """
        # The current implementation has a bug where it tries to access
        # 'email_number' and 'username_number' fields that don't exist
        
        # This should work fine as long as we don't trigger the buggy code
        serializer = BuyerSerializer()
        
        # The bug is in lines 34-35 of the original code:
        # self.fields['email_number'].required = True
        # self.fields['username_number'].required = True
        
        # These fields don't exist in the fields definition, so accessing them
        # would raise KeyError. However, since we can't easily test this without
        # modifying the source, we document it here.
        
        # What should probably be there instead:
        # self.fields['email'].required = True  
        # self.fields['username'].required = True
        
        # For now, we verify that the working fields are set correctly
        self.assertTrue(serializer.fields['aadhaar_number'].required)
        self.assertTrue(serializer.fields['pan_number'].required)
        
        # And document that the email and username fields exist but are not 
        # being set as required due to the bug
        self.assertIn('email', serializer.fields)
        self.assertIn('username', serializer.fields)
        self.assertFalse(serializer.fields['email'].required)  # Should be True after bug fix
        self.assertFalse(serializer.fields['username'].required)  # Should be True after bug fix

    def test_init_fields_properly_set_for_creation(self):
        """Test that __init__ properly sets fields as required for creation."""
        serializer = BuyerSerializer()
        
        # Verify that aadhaar_number and pan_number are set as required
        self.assertTrue(serializer.fields['aadhaar_number'].required)
        self.assertTrue(serializer.fields['pan_number'].required)

    def test_init_fields_not_required_for_updates(self):
        """Test that __init__ doesn't set fields as required for updates."""
        mock_buyer = Mock()
        serializer = BuyerSerializer(instance=mock_buyer)
        
        # Verify that fields are not required for updates
        self.assertFalse(serializer.fields['aadhaar_number'].required)
        self.assertFalse(serializer.fields['pan_number'].required)

    def test_serializer_inheritance_structure(self):
        """Test that BuyerSerializer properly inherits from BaseUserSerializer."""
        self.assertTrue(issubclass(BuyerSerializer, BaseUserSerializer))
        
        # Test Meta class inheritance
        self.assertTrue(hasattr(BuyerSerializer.Meta, '__bases__'))
        self.assertIn(BaseUserSerializer.Meta, BuyerSerializer.Meta.__bases__)

    def test_serializer_write_only_fields(self):
        """Test that sensitive fields are properly marked as write-only."""
        serializer = BuyerSerializer()
        
        write_only_fields = ['aadhaar_number', 'pan_number', 'aadhaar_card', 'pan_card', 'password']
        
        for field_name in write_only_fields:
            with self.subTest(field=field_name):
                self.assertTrue(
                    serializer.fields[field_name].write_only,
                    f"{field_name} should be write-only"
                )

    def test_validation_error_messages(self):
        """Test that validation error messages are properly formatted."""
        serializer = BuyerSerializer()
        
        # Test aadhaar_number validation error message
        attrs = {'pan_number': 'ABCDE1234F'}  # Missing aadhaar_number
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(attrs)
        
        error_detail = context.exception.detail
        self.assertIn('aadhaar_number', error_detail)
        self.assertEqual(
            error_detail['aadhaar_number'],
            'This field is required during creation.'
        )

    def test_create_verification_data_structure(self):
        """Test that create method structures verification data correctly."""
        serializer = BuyerSerializer()
        
        test_data = {
            'aadhaar_number': 123456789012,
            'pan_number': 'ABCDE1234F',
            'first_name': 'Test',
            'phone_number': 1234567890
        }
        
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_create_user.return_value = Mock()
            
            serializer.create(test_data)
            
            # Verify the structure of verification data
            call_args = mock_create_user.call_args[0]
            main_data = call_args[0]
            
            self.assertIn('buyerverification', main_data)
            verification_data = main_data['buyerverification']
            
            # Check verification data structure
            expected_verification_keys = {'aadhaar_number', 'pan_number', 'aadhaar_card', 'pan_card'}
            self.assertEqual(set(verification_data.keys()), expected_verification_keys)
            
            # Check that values are properly extracted
            self.assertEqual(verification_data['aadhaar_number'], 123456789012)
            self.assertEqual(verification_data['pan_number'], 'ABCDE1234F')
            self.assertIsNone(verification_data['aadhaar_card'])
            self.assertIsNone(verification_data['pan_card'])
