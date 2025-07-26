from unittest.mock import Mock, patch
from django.test import TestCase
from rest_framework import serializers
import seller_data.models as models
from common.serializer import BaseUserSerializer
from seller_data.serializer import SellerSerializer


class TestSellerSerializer(TestCase):
    """
    Comprehensive unit tests for SellerSerializer.
    Testing framework: Django's built-in unittest framework with TestCase.
    """
    
    def setUp(self):
        """Set up test fixtures and mock objects."""
        self.user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'username': 'johndoe',
            'password': 'securepassword123'
        }
        
        self.seller_data = {
            'business_name': 'Doe Real Estate',
            'phone_number': 1234567890,
            'pan_number': 'ABCDE1234F',
            'gstin': 123456789012345,
            'agent_rera_id': 'RERA123456'  # Changed from agent_rera_id_write to agent_rera_id for create method
        }
        
        self.complete_data = {**self.user_data, **self.seller_data}
        
        # Mock user and seller instances
        self.mock_user = Mock()
        self.mock_user.first_name = 'John'
        self.mock_user.last_name = 'Doe'
        self.mock_user.email = 'john.doe@example.com'
        self.mock_user.username = 'johndoe'
        
        self.mock_seller = Mock(spec=models.Seller)
        self.mock_seller.user = self.mock_user
        self.mock_seller.business_name = 'Doe Real Estate'
        self.mock_seller.phone_number = 1234567890
        
        # Mock seller verification
        self.mock_verification = Mock()
        self.mock_verification.agent_rera_id = 'RERA123456'
        self.mock_seller.sellerverification = self.mock_verification

    def test_init_without_instance_sets_required_fields(self):
        """Test that required fields are set when no instance is provided (creation mode)."""
        serializer = SellerSerializer()
        
        self.assertTrue(serializer.fields['pan_number'].required)
        self.assertTrue(serializer.fields['gstin'].required)
        self.assertTrue(serializer.fields['agent_rera_id_write'].required)
        self.assertTrue(serializer.fields['business_name'].required)
        self.assertTrue(serializer.fields['username'].required)
        self.assertTrue(serializer.fields['email'].required)

    def test_init_with_instance_keeps_fields_optional(self):
        """Test that fields remain optional when an instance is provided (update mode)."""
        serializer = SellerSerializer(instance=self.mock_seller)
        
        self.assertFalse(serializer.fields['pan_number'].required)
        self.assertFalse(serializer.fields['gstin'].required)
        self.assertFalse(serializer.fields['agent_rera_id_write'].required)
        self.assertFalse(serializer.fields['business_name'].required)
        self.assertFalse(serializer.fields['username'].required)
        self.assertFalse(serializer.fields['email'].required)

    def test_field_definitions_and_properties(self):
        """Test that all fields are defined with correct properties."""
        serializer = SellerSerializer()
        
        # Test write_only fields
        self.assertTrue(serializer.fields['pan_number'].write_only)
        self.assertTrue(serializer.fields['pan_card'].write_only)
        self.assertTrue(serializer.fields['gstin'].write_only)
        self.assertTrue(serializer.fields['agent_rera_id_write'].write_only)
        
        # Test read_only fields
        self.assertTrue(serializer.fields['agent_rera_id'].read_only)
        
        # Test field types
        self.assertIsInstance(serializer.fields['pan_number'], serializers.CharField)
        self.assertIsInstance(serializer.fields['pan_card'], serializers.ImageField)
        self.assertIsInstance(serializer.fields['gstin'], serializers.IntegerField)
        self.assertIsInstance(serializer.fields['profile_picture'], serializers.ImageField)
        self.assertIsInstance(serializer.fields['business_name'], serializers.CharField)
        self.assertIsInstance(serializer.fields['email'], serializers.EmailField)

    def test_field_sources(self):
        """Test that fields have correct source mappings."""
        serializer = SellerSerializer()
        
        self.assertEqual(serializer.fields['first_name'].source, 'user.first_name')
        self.assertEqual(serializer.fields['last_name'].source, 'user.last_name')
        self.assertEqual(serializer.fields['email'].source, 'user.email')
        self.assertEqual(serializer.fields['username'].source, 'user.username')
        self.assertEqual(serializer.fields['agent_rera_id_write'].source, 'agent_rera_id')

    def test_meta_class_configuration(self):
        """Test Meta class configuration."""
        serializer = SellerSerializer()
        expected_fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 
                          'business_name', 'username', 'password', 'pan_number', 
                          'pan_card', 'gstin', 'agent_rera_id', 'agent_rera_id_write', 
                          'profile_picture')
        
        self.assertEqual(serializer.Meta.model, models.Seller)
        self.assertEqual(serializer.Meta.fields, expected_fields)

    def test_get_agent_rera_id_with_verification(self):
        """Test get_agent_rera_id returns RERA ID when verification exists."""
        result = SellerSerializer.get_agent_rera_id(self.mock_seller)
        
        self.assertEqual(result, 'RERA123456')

    def test_get_agent_rera_id_without_verification(self):
        """Test get_agent_rera_id returns None when verification doesn't exist."""
        mock_seller_no_verification = Mock(spec=models.Seller)
        # Mock AttributeError when accessing sellerverification
        type(mock_seller_no_verification).sellerverification = property(
            lambda self: (_ for _ in ()).throw(AttributeError())
        )
        
        result = SellerSerializer.get_agent_rera_id(mock_seller_no_verification)
        
        self.assertIsNone(result)

    def test_get_agent_rera_id_with_attribute_error(self):
        """Test get_agent_rera_id handles AttributeError gracefully."""
        mock_seller = Mock()
        # Remove the sellerverification attribute to trigger AttributeError
        type(mock_seller).sellerverification = property(
            lambda self: (_ for _ in ()).throw(AttributeError())
        )
        
        result = SellerSerializer.get_agent_rera_id(mock_seller)
        
        self.assertIsNone(result)

    def test_get_agent_rera_id_with_none_verification(self):
        """Test get_agent_rera_id when sellerverification exists but agent_rera_id is None."""
        mock_seller = Mock()
        mock_verification = Mock()
        mock_verification.agent_rera_id = None
        mock_seller.sellerverification = mock_verification
        
        result = SellerSerializer.get_agent_rera_id(mock_seller)
        
        self.assertIsNone(result)

    @patch.object(BaseUserSerializer, 'create_user')
    def test_create_success(self, mock_create_user):
        """Test successful creation of seller with verification data."""
        mock_seller_instance = Mock(spec=models.Seller)
        mock_create_user.return_value = mock_seller_instance
        
        serializer = SellerSerializer()
        validated_data = self.complete_data.copy()
        
        result = serializer.create(validated_data)
        
        # Verify that verification data was properly extracted and passed
        expected_verification_data = {
            'pan_number': 'ABCDE1234F',
            'pan_card': None,
            'gstin': 123456789012345,
            'agent_rera_id': 'RERA123456'
        }
        
        # Check that create_user was called with correct arguments
        mock_create_user.assert_called_once()
        call_args = mock_create_user.call_args[0]
        self.assertIn('sellerverification', call_args[0])
        self.assertEqual(call_args[0]['sellerverification'], expected_verification_data)
        self.assertEqual(call_args[1], models.Seller)
        self.assertEqual(call_args[2], models.SellerVerification)
        self.assertEqual(call_args[3], 'sellerverification')
        self.assertEqual(result, mock_seller_instance)

    @patch.object(BaseUserSerializer, 'create_user')
    def test_create_with_pan_card(self, mock_create_user):
        """Test creation with pan_card included."""
        mock_seller_instance = Mock(spec=models.Seller)
        mock_create_user.return_value = mock_seller_instance
        
        mock_pan_card = Mock()
        validated_data = self.complete_data.copy()
        validated_data['pan_card'] = mock_pan_card
        
        serializer = SellerSerializer()
        serializer.create(validated_data)
        
        # Verify pan_card was included in verification data
        call_args = mock_create_user.call_args[0][0]
        self.assertEqual(call_args['sellerverification']['pan_card'], mock_pan_card)

    def test_create_missing_required_fields(self):
        """Test that create method handles missing verification fields properly."""
        serializer = SellerSerializer()
        incomplete_data = self.user_data.copy()
        # Missing verification fields
        
        with self.assertRaises(KeyError):
            serializer.create(incomplete_data)

    def test_create_missing_pan_number(self):
        """Test create method raises KeyError when pan_number is missing."""
        serializer = SellerSerializer()
        data_without_pan = self.complete_data.copy()
        del data_without_pan['pan_number']
        
        with self.assertRaises(KeyError) as context:
            serializer.create(data_without_pan)
        self.assertEqual(str(context.exception), "'pan_number'")

    def test_create_missing_gstin(self):
        """Test create method raises KeyError when gstin is missing."""
        serializer = SellerSerializer()
        data_without_gstin = self.complete_data.copy()
        del data_without_gstin['gstin']
        
        with self.assertRaises(KeyError) as context:
            serializer.create(data_without_gstin)
        self.assertEqual(str(context.exception), "'gstin'")

    def test_create_missing_agent_rera_id(self):
        """Test create method raises KeyError when agent_rera_id is missing."""
        serializer = SellerSerializer()
        data_without_rera = self.complete_data.copy()
        del data_without_rera['agent_rera_id']
        
        with self.assertRaises(KeyError) as context:
            serializer.create(data_without_rera)
        self.assertEqual(str(context.exception), "'agent_rera_id'")

    @patch.object(BaseUserSerializer, 'update_user')
    def test_update_success(self, mock_update_user):
        """Test successful update of seller instance."""
        mock_updated_seller = Mock(spec=models.Seller)
        mock_update_user.return_value = mock_updated_seller
        
        serializer = SellerSerializer()
        update_data = {'first_name': 'Jane', 'phone_number': 9876543210}
        
        result = serializer.update(self.mock_seller, update_data)
        
        mock_update_user.assert_called_once_with(
            self.mock_seller,
            update_data,
            'sellerverification'
        )
        self.assertEqual(result, mock_updated_seller)

    def test_update_business_name_unchanged_allowed(self):
        """Test that updating with same business name is allowed."""
        with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
            mock_updated_seller = Mock(spec=models.Seller)
            mock_update_user.return_value = mock_updated_seller
            
            serializer = SellerSerializer()
            update_data = {'business_name': 'Doe Real Estate', 'phone_number': 9876543210}
            
            result = serializer.update(self.mock_seller, update_data)
            
            # Should not raise ValidationError
            mock_update_user.assert_called_once()
            self.assertEqual(result, mock_updated_seller)

    def test_update_business_name_change_raises_validation_error(self):
        """Test that changing business name raises ValidationError."""
        serializer = SellerSerializer()
        update_data = {'business_name': 'New Business Name'}
        
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.update(self.mock_seller, update_data)
        
        self.assertIn('business_name', context.exception.detail)
        self.assertEqual(context.exception.detail['business_name'], 'Cannot modify business_name once set.')

    def test_update_business_name_none_to_value_allowed(self):
        """Test that setting business name from None is allowed."""
        with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
            mock_updated_seller = Mock(spec=models.Seller)
            mock_update_user.return_value = mock_updated_seller
            
            # Mock seller with None business name
            mock_seller_no_business = Mock(spec=models.Seller)
            mock_seller_no_business.business_name = None
            
            serializer = SellerSerializer()
            update_data = {'business_name': 'New Business Name'}
            
            result = serializer.update(mock_seller_no_business, update_data)
            
            mock_update_user.assert_called_once()
            self.assertEqual(result, mock_updated_seller)

    def test_update_business_name_empty_string_to_value_allowed(self):
        """Test that setting business name from empty string is allowed."""
        with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
            mock_updated_seller = Mock(spec=models.Seller)
            mock_update_user.return_value = mock_updated_seller
            
            # Mock seller with empty business name
            mock_seller_empty_business = Mock(spec=models.Seller)
            mock_seller_empty_business.business_name = ''
            
            serializer = SellerSerializer()
            update_data = {'business_name': 'New Business Name'}
            
            result = serializer.update(mock_seller_empty_business, update_data)
            
            mock_update_user.assert_called_once()
            self.assertEqual(result, mock_updated_seller)

    def test_update_without_business_name_field(self):
        """Test update when business_name is not in validated_data."""
        with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
            mock_updated_seller = Mock(spec=models.Seller)
            mock_update_user.return_value = mock_updated_seller
            
            serializer = SellerSerializer()
            update_data = {'phone_number': 9876543210, 'profile_picture': Mock()}
            
            result = serializer.update(self.mock_seller, update_data)
            
            # Should not raise ValidationError and should call update_user
            mock_update_user.assert_called_once()
            self.assertEqual(result, mock_updated_seller)

    def test_serializer_inheritance(self):
        """Test that SellerSerializer properly inherits from BaseUserSerializer."""
        self.assertTrue(issubclass(SellerSerializer, BaseUserSerializer))

    def test_serializer_method_field_agent_rera_id(self):
        """Test that agent_rera_id SerializerMethodField works correctly."""
        serializer = SellerSerializer(instance=self.mock_seller)
        
        # The SerializerMethodField should call get_agent_rera_id
        representation = serializer.to_representation(self.mock_seller)
        self.assertEqual(representation['agent_rera_id'], 'RERA123456')

    def test_serializer_method_field_agent_rera_id_none(self):
        """Test that agent_rera_id SerializerMethodField returns None when no verification."""
        # Mock seller without verification
        mock_seller_no_verification = Mock(spec=models.Seller)
        type(mock_seller_no_verification).sellerverification = property(
            lambda self: (_ for _ in ()).throw(AttributeError())
        )
        
        serializer = SellerSerializer(instance=mock_seller_no_verification)
        
        representation = serializer.to_representation(mock_seller_no_verification)
        self.assertIsNone(representation['agent_rera_id'])

    def test_field_choices_and_constraints(self):
        """Test field-specific choices and constraints if any."""
        serializer = SellerSerializer()
        
        # Test that ImageField fields are properly configured
        self.assertIsInstance(serializer.fields['pan_card'], serializers.ImageField)
        self.assertIsInstance(serializer.fields['profile_picture'], serializers.ImageField)
        
        # Test required=False for optional fields
        self.assertFalse(serializer.fields['pan_card'].required)
        self.assertFalse(serializer.fields['profile_picture'].required)

    def test_serializer_context_handling(self):
        """Test that serializer handles context properly."""
        context = {'request': Mock(), 'view': Mock()}
        serializer = SellerSerializer(context=context)
        
        self.assertEqual(serializer.context, context)

    def test_create_validation_data_extraction(self):
        """Test that create method properly extracts and transforms validation data."""
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_seller_instance = Mock()
            mock_create_user.return_value = mock_seller_instance
            
            # Test data with all possible fields
            test_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'username': 'johndoe',
                'password': 'password123',
                'business_name': 'Test Business',
                'phone_number': 1234567890,
                'pan_number': 'ABCDE1234F',
                'pan_card': Mock(),
                'gstin': 123456789012345,
                'agent_rera_id': 'RERA123456'
            }
            
            serializer = SellerSerializer()
            serializer.create(test_data.copy())
            
            # Verify verification data extraction
            call_args = mock_create_user.call_args[0][0]
            verification_data = call_args['sellerverification']
            
            self.assertEqual(verification_data['pan_number'], 'ABCDE1234F')
            self.assertEqual(verification_data['gstin'], 123456789012345)
            self.assertEqual(verification_data['agent_rera_id'], 'RERA123456')
            self.assertIsNotNone(verification_data['pan_card'])

    def test_create_without_optional_pan_card(self):
        """Test create method when pan_card is not provided."""
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_seller_instance = Mock()
            mock_create_user.return_value = mock_seller_instance
            
            test_data = self.complete_data.copy()
            # pan_card is not included in test_data
            
            serializer = SellerSerializer()
            serializer.create(test_data)
            
            # Verify that pan_card defaults to None
            call_args = mock_create_user.call_args[0][0]
            verification_data = call_args['sellerverification']
            self.assertIsNone(verification_data['pan_card'])

    def test_static_method_independence(self):
        """Test that get_agent_rera_id is truly static and doesn't depend on instance state."""
        # Call the static method directly without instantiating the class
        result1 = SellerSerializer.get_agent_rera_id(self.mock_seller)
        
        # Create an instance and call the method
        serializer = SellerSerializer()
        result2 = serializer.get_agent_rera_id(self.mock_seller)
        
        # Both should return the same result
        self.assertEqual(result1, result2)
        self.assertEqual(result1, 'RERA123456')

    def test_create_method_field_order_independence(self):
        """Test that create method works regardless of field order in validated_data."""
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_seller_instance = Mock()
            mock_create_user.return_value = mock_seller_instance
            
            # Create data with different field ordering
            reordered_data = {
                'agent_rera_id': 'RERA123456',
                'gstin': 123456789012345,
                'business_name': 'Test Business',
                'pan_number': 'ABCDE1234F',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john@example.com',
                'username': 'johndoe',
                'password': 'password123',
                'phone_number': 1234567890
            }
            
            serializer = SellerSerializer()
            result = serializer.create(reordered_data)
            
            # Should still work correctly
            mock_create_user.assert_called_once()
            self.assertEqual(result, mock_seller_instance)

    def test_comprehensive_business_name_update_scenarios(self):
        """Test all business name update scenarios comprehensively."""
        serializer = SellerSerializer()
        
        # Test 1: Same business name - should work
        with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
            mock_update_user.return_value = self.mock_seller
            result = serializer.update(self.mock_seller, {'business_name': 'Doe Real Estate'})
            mock_update_user.assert_called_once()
        
        # Test 2: Different business name - should raise ValidationError
        with self.assertRaises(serializers.ValidationError):
            serializer.update(self.mock_seller, {'business_name': 'Different Name'})
        
        # Test 3: None to some value - should work
        mock_seller_none = Mock(spec=models.Seller)
        mock_seller_none.business_name = None
        with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
            mock_update_user.return_value = mock_seller_none
            serializer.update(mock_seller_none, {'business_name': 'New Name'})
            mock_update_user.assert_called_once()

    def test_serializer_method_field_edge_cases(self):
        """Test SerializerMethodField with various edge cases."""
        # Test with Mock that has no sellerverification attribute at all
        mock_seller_no_attr = Mock()
        del mock_seller_no_attr.sellerverification  # Remove attribute entirely
        
        result = SellerSerializer.get_agent_rera_id(mock_seller_no_attr)
        self.assertIsNone(result)
        
        # Test with Mock that has sellerverification but accessing agent_rera_id raises AttributeError
        mock_seller_partial = Mock()
        mock_verification_no_id = Mock()
        type(mock_verification_no_id).agent_rera_id = property(
            lambda self: (_ for _ in ()).throw(AttributeError())
        )
        mock_seller_partial.sellerverification = mock_verification_no_id
        
        result = SellerSerializer.get_agent_rera_id(mock_seller_partial)
        self.assertIsNone(result)

    def test_field_requirement_toggling_comprehensive(self):
        """Test comprehensive field requirement toggling behavior."""
        # Test creation mode - all specified fields should be required
        create_serializer = SellerSerializer()
        required_fields = ['pan_number', 'gstin', 'agent_rera_id_write', 'business_name', 'username', 'email']
        for field in required_fields:
            self.assertTrue(create_serializer.fields[field].required, f"Field {field} should be required in create mode")
        
        # Test update mode - all specified fields should be optional
        update_serializer = SellerSerializer(instance=self.mock_seller)
        for field in required_fields:
            self.assertFalse(update_serializer.fields[field].required, f"Field {field} should be optional in update mode")
        
        # Test that non-specified fields maintain their original required status
        self.assertFalse(create_serializer.fields['pan_card'].required)
        self.assertFalse(create_serializer.fields['profile_picture'].required)
        self.assertFalse(update_serializer.fields['pan_card'].required)
        self.assertFalse(update_serializer.fields['profile_picture'].required)

    def test_serializer_fields_write_only_behavior(self):
        """Test that write_only fields are properly handled in serialization."""
        serializer = SellerSerializer(instance=self.mock_seller)
        representation = serializer.to_representation(self.mock_seller)
        
        # Write-only fields should not appear in representation
        write_only_fields = ['pan_number', 'pan_card', 'gstin', 'agent_rera_id_write', 'password']
        for field in write_only_fields:
            self.assertNotIn(field, representation, f"Write-only field {field} should not appear in representation")

    def test_serializer_fields_read_only_behavior(self):
        """Test that read_only fields are properly handled."""
        serializer = SellerSerializer(instance=self.mock_seller)
        representation = serializer.to_representation(self.mock_seller)
        
        # Read-only fields should appear in representation
        self.assertIn('agent_rera_id', representation)
        self.assertEqual(representation['agent_rera_id'], 'RERA123456')

    def test_create_data_modification_isolation(self):
        """Test that create method doesn't modify the original validated_data dict."""
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_seller_instance = Mock()
            mock_create_user.return_value = mock_seller_instance
            
            original_data = self.complete_data.copy()
            test_data = original_data.copy()
            
            serializer = SellerSerializer()
            serializer.create(test_data)
            
            # Verify that original keys are removed from test_data but original_data is unchanged
            self.assertNotIn('pan_number', test_data)
            self.assertNotIn('gstin', test_data)
            self.assertNotIn('agent_rera_id', test_data)
            self.assertIn('sellerverification', test_data)
            
            # Original data should be unchanged
            self.assertIn('pan_number', original_data)
            self.assertIn('gstin', original_data)
            self.assertIn('agent_rera_id', original_data)

    def test_comprehensive_validation_error_messages(self):
        """Test that ValidationError messages are properly formatted."""
        serializer = SellerSerializer()
        
        # Test business name validation error format
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.update(self.mock_seller, {'business_name': 'Different Name'})
        
        error_detail = context.exception.detail
        self.assertIsInstance(error_detail, dict)
        self.assertIn('business_name', error_detail)
        self.assertEqual(error_detail['business_name'], 'Cannot modify business_name once set.')

    def test_edge_case_special_characters_in_business_name(self):
        """Test handling of special characters in business name updates."""
        serializer = SellerSerializer()
        
        # Test with special characters that might cause comparison issues
        special_names = [
            'Business & Co.',
            'Business "Quotes"',
            "Business 'Apostrophe'",
            'Business\nNewline',
            'Business\tTab',
        ]
        
        for special_name in special_names:
            mock_seller_special = Mock(spec=models.Seller)
            mock_seller_special.business_name = special_name
            
            # Same name should not raise error
            with patch.object(BaseUserSerializer, 'update_user') as mock_update_user:
                mock_update_user.return_value = mock_seller_special
                serializer.update(mock_seller_special, {'business_name': special_name})
                mock_update_user.assert_called_once()
            
            # Different name should raise error
            with self.assertRaises(serializers.ValidationError):
                serializer.update(mock_seller_special, {'business_name': 'Different Name'})

    def test_comprehensive_create_method_error_scenarios(self):
        """Test various error scenarios in the create method."""
        serializer = SellerSerializer()
        
        # Test 1: All required verification fields missing
        empty_data = {'first_name': 'John'}
        with self.assertRaises(KeyError):
            serializer.create(empty_data)
        
        # Test 2: Only some verification fields present
        partial_data = self.user_data.copy()
        partial_data.update({'pan_number': 'ABC123'})
        with self.assertRaises(KeyError):
            serializer.create(partial_data)
        
        # Test 3: Verification fields with None values
        none_data = self.complete_data.copy()
        none_data['pan_number'] = None
        with patch.object(BaseUserSerializer, 'create_user') as mock_create_user:
            mock_create_user.return_value = Mock()
            serializer.create(none_data)
            # Should still work as None is a valid value
            mock_create_user.assert_called_once()

    def test_serializer_method_field_return_types(self):
        """Test that SerializerMethodField returns appropriate types."""
        # Test with string RERA ID
        result_string = SellerSerializer.get_agent_rera_id(self.mock_seller)
        self.assertIsInstance(result_string, str)
        
        # Test with None return
        mock_seller_no_verification = Mock()
        type(mock_seller_no_verification).sellerverification = property(
            lambda self: (_ for _ in ()).throw(AttributeError())
        )
        result_none = SellerSerializer.get_agent_rera_id(mock_seller_no_verification)
        self.assertIsNone(result_none)
        
        # Test with integer RERA ID (edge case)
        mock_seller_int_rera = Mock()
        mock_verification_int = Mock()
        mock_verification_int.agent_rera_id = 123456
        mock_seller_int_rera.sellerverification = mock_verification_int
        
        result_int = SellerSerializer.get_agent_rera_id(mock_seller_int_rera)
        self.assertEqual(result_int, 123456)
        self.assertIsInstance(result_int, int)

    def test_inheritance_and_method_resolution_order(self):
        """Test that method resolution follows proper inheritance chain."""
        mro = SellerSerializer.__mro__
        self.assertIn(BaseUserSerializer, mro)
        self.assertIn(serializers.ModelSerializer, mro)
        
        # Verify that specific methods are overridden
        self.assertTrue(hasattr(SellerSerializer, '__init__'))
        self.assertTrue(hasattr(SellerSerializer, 'create'))
        self.assertTrue(hasattr(SellerSerializer, 'update'))
        self.assertTrue(hasattr(SellerSerializer, 'get_agent_rera_id'))
        
        # Verify static method decoration
        self.assertTrue(isinstance(SellerSerializer.__dict__['get_agent_rera_id'], staticmethod))