from io import BytesIO
from PIL import Image
from decimal import Decimal
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from unittest.mock import Mock, patch
import estate_data.models as models
from seller_data.models import Seller


class BaseTestCase(TestCase):
    """Base test case with common setup and utilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = APIRequestFactory()
        
        # Create a seller instance for testing
        self.seller = Seller.objects.create(
            name="Test Seller",
            email="test@example.com",
            phone="123-456-7890"
        )
        
        # Create an estate instance for testing
        self.estate = models.Estate.objects.create(
            seller=self.seller,
            estate_name="Test Estate",
            estate_type="apartment",
            estate_government_id="GOV123",
            estate_price=Decimal('100000.00'),
            status="available",
            description="Test description",
            latitude=Decimal('40.71280000'),
            longitude=Decimal('-74.00600000')
        )
        
    def create_test_image(self, name='test.jpg', format='JPEG'):
        """Helper method to create a test image file"""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, format=format)
        image_file.seek(0)
        return SimpleUploadedFile(name, image_file.getvalue(), content_type=f'image/{format.lower()}')


class EstateImageSerializerTest(BaseTestCase):
    """Test cases for EstateImageSerializer - Testing Framework: Django TestCase with Django REST Framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        from estate_data.serializers import EstateImageSerializer
        self.serializer_class = EstateImageSerializer
        
    def test_estate_image_serializer_fields(self):
        """Test that EstateImageSerializer has correct fields"""
        serializer = self.serializer_class()
        expected_fields = {'id', 'image'}
        self.assertEqual(set(serializer.fields.keys()), expected_fields)
    
    def test_estate_image_serializer_id_read_only(self):
        """Test that id field is read-only"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['id'].read_only)
    
    def test_estate_image_serializer_image_required(self):
        """Test that image field is required"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['image'].required)
    
    def test_estate_image_serializer_valid_data(self):
        """Test serializer with valid image data"""
        image_file = self.create_test_image()
        data = {'image': image_file}
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_estate_image_serializer_missing_image(self):
        """Test serializer validation fails without image"""
        data = {}
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)
    
    def test_estate_image_serializer_invalid_file_type(self):
        """Test serializer validation fails with invalid file type"""
        invalid_file = SimpleUploadedFile("test.txt", b"not an image", content_type="text/plain")
        data = {'image': invalid_file}
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_estate_image_serializer_different_image_formats(self):
        """Test serializer accepts different valid image formats"""
        formats = [('JPEG', 'test.jpg'), ('PNG', 'test.png'), ('GIF', 'test.gif')]
        
        for format_type, filename in formats:
            with self.subTest(format=format_type):
                image_file = self.create_test_image(filename, format_type)
                data = {'image': image_file}
                serializer = self.serializer_class(data=data)
                self.assertTrue(serializer.is_valid(), f"Failed for {format_type}")
    
    def test_estate_image_serializer_meta_model(self):
        """Test that serializer Meta specifies correct model"""
        serializer = self.serializer_class()
        self.assertEqual(serializer.Meta.model, models.EstateImage)
    
    def test_estate_image_serializer_serialization(self):
        """Test serializing existing EstateImage instance"""
        estate_image = models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image.jpg'
        )
        
        serializer = self.serializer_class(instance=estate_image)
        data = serializer.data
        
        self.assertEqual(data['id'], estate_image.id)
        self.assertIn('image', data)


class EstateSerializerTest(BaseTestCase):
    """Test cases for EstateSerializer - Testing Framework: Django TestCase with Django REST Framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        from estate_data.serializers import EstateSerializer
        self.serializer_class = EstateSerializer
        
    def test_estate_serializer_fields(self):
        """Test that EstateSerializer has correct fields"""
        serializer = self.serializer_class()
        expected_fields = {
            'seller', 'estate_name', 'estate_type', 'estate_government_id', 
            'estate_price', 'status', 'slug', 'description', 'latitude', 
            'longitude', 'images', 'images_to_delete'
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)
    
    def test_estate_serializer_images_read_only(self):
        """Test that images field is read-only"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['images'].read_only)
    
    def test_estate_serializer_images_to_delete_write_only(self):
        """Test that images_to_delete field is write-only"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['images_to_delete'].write_only)
    
    def test_estate_serializer_images_to_delete_not_required(self):
        """Test that images_to_delete field is not required"""
        serializer = self.serializer_class()
        self.assertFalse(serializer.fields['images_to_delete'].required)
    
    def test_estate_serializer_valid_data(self):
        """Test serializer with valid estate data"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000'
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_estate_serializer_create_without_images(self):
        """Test creating estate without images"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000'
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        estate = serializer.save()
        self.assertEqual(estate.seller, self.seller)
        self.assertEqual(estate.estate_name, 'New Estate')
    
    def test_estate_serializer_create_with_images_to_delete(self):
        """Test creating estate removes images_to_delete from validated_data"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000',
            'images_to_delete': [1, 2, 3]
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        estate = serializer.save()
        self.assertEqual(estate.seller, self.seller)
    
    @patch('estate_data.models.EstateImage.objects.create')
    def test_estate_serializer_create_with_images(self, mock_create):
        """Test creating estate with images"""
        image_file = self.create_test_image()
        request = self.factory.post('/', {})
        request.FILES = {'images': [image_file]}
        
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000'
        }
        
        serializer = self.serializer_class(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        estate = serializer.save()
        
        # Verify EstateImage.objects.create was called
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[1]['estate'], estate)
        self.assertEqual(call_args[1]['image'], image_file)
    
    @patch('estate_data.models.EstateImage.objects.create')
    def test_estate_serializer_create_with_multiple_images(self, mock_create):
        """Test creating estate with multiple images"""
        image_file1 = self.create_test_image('test1.jpg')
        image_file2 = self.create_test_image('test2.jpg')
        request = self.factory.post('/', {})
        request.FILES = {'images': [image_file1, image_file2]}
        
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000'
        }
        
        serializer = self.serializer_class(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        serializer.save()
        
        # Verify EstateImage.objects.create was called twice
        self.assertEqual(mock_create.call_count, 2)
    
    def test_estate_serializer_create_no_request_context(self):
        """Test creating estate without request context"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000'
        }
        serializer = self.serializer_class(data=data)
        self.assertTrue(serializer.is_valid())
        estate = serializer.save()
        self.assertEqual(estate.seller, self.seller)
    
    def test_estate_serializer_create_no_files(self):
        """Test creating estate with request but no files"""
        request = self.factory.post('/', {})
        
        data = {
            'seller': self.seller.id,
            'estate_name': 'New Estate',
            'estate_type': 'commercial',
            'estate_government_id': 'GOV456',
            'estate_price': '200000.00',
            'status': 'available',
            'description': 'New description',
            'latitude': '41.87810000',
            'longitude': '-87.62980000'
        }
        
        serializer = self.serializer_class(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        estate = serializer.save()
        self.assertEqual(estate.seller, self.seller)
    
    def test_estate_serializer_validate_government_id_no_instance(self):
        """Test validation passes when no instance exists (creation)"""
        data = {
            'estate_government_id': 'GOV789'
        }
        serializer = self.serializer_class()
        validated_data = serializer.validate(data)
        self.assertEqual(validated_data['estate_government_id'], 'GOV789')
    
    def test_estate_serializer_validate_government_id_same_value(self):
        """Test validation passes when government ID unchanged"""
        data = {
            'estate_government_id': 'GOV123'
        }
        serializer = self.serializer_class(instance=self.estate)
        validated_data = serializer.validate(data)
        self.assertEqual(validated_data['estate_government_id'], 'GOV123')
    
    def test_estate_serializer_validate_government_id_changed(self):
        """Test validation fails when government ID is changed"""
        data = {
            'estate_government_id': 'GOV999'
        }
        serializer = self.serializer_class(instance=self.estate)
        with self.assertRaises(ValidationError) as context:
            serializer.validate(data)
        self.assertEqual(str(context.exception.detail[0]), 'Government ID cannot be changed once set!')
    
    def test_estate_serializer_validate_no_government_id_in_attrs(self):
        """Test validation passes when government ID not in attributes"""
        data = {
            'estate_name': 'Updated Estate'
        }
        serializer = self.serializer_class(instance=self.estate)
        validated_data = serializer.validate(data)
        self.assertEqual(validated_data['estate_name'], 'Updated Estate')
    
    def test_estate_serializer_validate_with_empty_attrs(self):
        """Test validation with empty attributes"""
        data = {}
        serializer = self.serializer_class(instance=self.estate)
        validated_data = serializer.validate(data)
        self.assertEqual(validated_data, {})
    
    def test_estate_serializer_update_basic_fields(self):
        """Test updating estate basic fields"""
        data = {
            'estate_name': 'Updated Estate',
            'estate_price': '150000.00',
            'description': 'Updated description'
        }
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
        self.assertEqual(updated_estate.estate_price, Decimal('150000.00'))
        self.assertEqual(updated_estate.description, 'Updated description')
    
    @patch('estate_data.models.EstateImage.objects.filter')
    def test_estate_serializer_update_with_images_to_delete(self, mock_filter):
        """Test updating estate with images to delete"""
        # Create mock images to delete
        mock_image1 = Mock()
        mock_image1.image.storage.exists.return_value = True
        mock_image1.image.name = 'test1.jpg'
        mock_image2 = Mock()
        mock_image2.image.storage.exists.return_value = False
        mock_image2.image.name = 'test2.jpg'
        
        mock_queryset = Mock()
        mock_queryset.__iter__ = Mock(return_value=iter([mock_image1, mock_image2]))
        mock_queryset.delete = Mock()
        mock_filter.return_value = mock_queryset
        
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': [1, 2]
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        # Verify filter was called with correct parameters
        mock_filter.assert_called_once_with(id__in=[1, 2], estate=self.estate)
        
        # Verify delete was called on storage for existing file
        mock_image1.image.storage.delete.assert_called_once_with('test1.jpg')
        
        # Verify delete was not called for non-existing file
        mock_image2.image.storage.delete.assert_not_called()
        
        # Verify queryset delete was called
        mock_queryset.delete.assert_called_once()
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_update_no_images_to_delete(self):
        """Test updating estate without images to delete"""
        data = {
            'estate_name': 'Updated Estate'
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_update_empty_images_to_delete(self):
        """Test updating estate with empty images_to_delete list"""
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': []
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    @patch('estate_data.models.EstateImage.objects.create')
    def test_estate_serializer_update_with_new_images(self, mock_create):
        """Test updating estate with new images"""
        image_file = self.create_test_image()
        request = self.factory.post('/', {})
        request.FILES = {'images': [image_file]}
        
        data = {
            'estate_name': 'Updated Estate'
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True, context={'request': request})
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        # Verify EstateImage.objects.create was called
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[1]['estate'], self.estate)
        self.assertEqual(call_args[1]['image'], image_file)
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_update_no_request_context(self):
        """Test updating estate without request context"""
        data = {
            'estate_name': 'Updated Estate'
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_update_no_files(self):
        """Test updating estate with request but no files"""
        request = self.factory.post('/', {})
        
        data = {
            'estate_name': 'Updated Estate'
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True, context={'request': request})
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    @patch('estate_data.models.EstateImage.objects.filter')
    @patch('estate_data.models.EstateImage.objects.create')
    def test_estate_serializer_update_delete_and_add_images(self, mock_create, mock_filter):
        """Test updating estate with both images to delete and new images"""
        # Setup mock for images to delete
        mock_image = Mock()
        mock_image.image.storage.exists.return_value = True
        mock_image.image.name = 'old.jpg'
        
        mock_queryset = Mock()
        mock_queryset.__iter__ = Mock(return_value=iter([mock_image]))
        mock_queryset.delete = Mock()
        mock_filter.return_value = mock_queryset
        
        # Setup new image
        image_file = self.create_test_image('new.jpg')
        request = self.factory.post('/', {})
        request.FILES = {'images': [image_file]}
        
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': [1]
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True, context={'request': request})
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        # Verify deletion operations
        mock_filter.assert_called_once_with(id__in=[1], estate=self.estate)
        mock_image.image.storage.delete.assert_called_once_with('old.jpg')
        mock_queryset.delete.assert_called_once()
        
        # Verify creation operation
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        self.assertEqual(call_args[1]['estate'], self.estate)
        self.assertEqual(call_args[1]['image'], image_file)
        
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_images_to_delete_child_field_type(self):
        """Test that images_to_delete has correct child field type"""
        serializer = self.serializer_class()
        images_to_delete_field = serializer.fields['images_to_delete']
        self.assertEqual(type(images_to_delete_field.child).__name__, 'IntegerField')
    
    def test_estate_serializer_images_many_true(self):
        """Test that images field has many=True"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['images'].many)
    
    def test_estate_serializer_meta_model(self):
        """Test that serializer Meta specifies correct model"""
        serializer = self.serializer_class()
        self.assertEqual(serializer.Meta.model, models.Estate)
    
    def test_estate_serializer_estate_type_choices(self):
        """Test serializer with different estate type choices"""
        valid_choices = ['apartment', 'house', 'land', 'commercial', 'villa', 'townhouse', 'duplex', 'studio', 'penthouse', 'cottage']
        
        for choice in valid_choices:
            with self.subTest(estate_type=choice):
                data = {
                    'seller': self.seller.id,
                    'estate_name': f'Test {choice}',
                    'estate_type': choice,
                    'estate_government_id': f'GOV{choice}',
                    'estate_price': '100000.00',
                    'status': 'available'
                }
                serializer = self.serializer_class(data=data)
                self.assertTrue(serializer.is_valid(), f"Failed for estate_type: {choice}")
    
    def test_estate_serializer_status_choices(self):
        """Test serializer with different status choices"""
        valid_choices = ['available', 'sold', 'rented', 'pending']
        
        for choice in valid_choices:
            with self.subTest(status=choice):
                data = {
                    'seller': self.seller.id,
                    'estate_name': f'Test Estate {choice}',
                    'estate_type': 'apartment',
                    'estate_government_id': f'GOV{choice}',
                    'estate_price': '100000.00',
                    'status': choice
                }
                serializer = self.serializer_class(data=data)
                self.assertTrue(serializer.is_valid(), f"Failed for status: {choice}")


class EstateListSerializerTest(BaseTestCase):
    """Test cases for EstateListSerializer - Testing Framework: Django TestCase with Django REST Framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        from estate_data.serializers import EstateListSerializer
        self.serializer_class = EstateListSerializer
    
    def test_estate_list_serializer_fields(self):
        """Test that EstateListSerializer has correct fields"""
        serializer = self.serializer_class()
        expected_fields = {'slug', 'estate_name', 'estate_price', 'estate_type', 'images'}
        self.assertEqual(set(serializer.fields.keys()), expected_fields)
    
    def test_estate_list_serializer_images_read_only(self):
        """Test that images field is read-only"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['images'].read_only)
    
    def test_estate_list_serializer_images_many_true(self):
        """Test that images field has many=True"""
        serializer = self.serializer_class()
        self.assertTrue(serializer.fields['images'].many)
    
    def test_estate_list_serializer_serialization(self):
        """Test serializing estate data with EstateListSerializer"""
        serializer = self.serializer_class(instance=self.estate)
        data = serializer.data
        
        expected_fields = {'slug', 'estate_name', 'estate_price', 'estate_type', 'images'}
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertIsNotNone(data['slug'])  # Slug is auto-generated
        self.assertEqual(data['estate_name'], 'Test Estate')
        self.assertEqual(data['estate_price'], '100000.00')
        self.assertEqual(data['estate_type'], 'apartment')
        self.assertEqual(data['images'], [])
    
    def test_estate_list_serializer_with_images(self):
        """Test serializing estate with images"""
        # Create an estate image
        estate_image = models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image.jpg'
        )
        
        serializer = self.serializer_class(instance=self.estate)
        data = serializer.data
        
        self.assertEqual(len(data['images']), 1)
        self.assertEqual(data['images'][0]['id'], estate_image.id)
    
    def test_estate_list_serializer_multiple_estates(self):
        """Test serializing multiple estates"""
        models.Estate.objects.create(
            seller=self.seller,
            estate_name="Test Estate 2",
            estate_type="commercial",
            estate_government_id="GOV456",
            estate_price=Decimal('200000.00'),
            status="sold",
            description="Test description 2",
            latitude=Decimal('41.87810000'),
            longitude=Decimal('-87.62980000')
        )
        
        estates = models.Estate.objects.all()
        serializer = self.serializer_class(estates, many=True)
        data = serializer.data
        
        self.assertEqual(len(data), 2)
        
        # Check both estates are represented
        estate_names = [item['estate_name'] for item in data]
        self.assertIn('Test Estate', estate_names)
        self.assertIn('Test Estate 2', estate_names)
    
    def test_estate_list_serializer_meta_model(self):
        """Test that serializer Meta specifies correct model"""
        serializer = self.serializer_class()
        self.assertEqual(serializer.Meta.model, models.Estate)
    
    def test_estate_list_serializer_with_multiple_images(self):
        """Test serializing estate with multiple images"""
        # Create multiple estate images
        estate_image1 = models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image1.jpg'
        )
        estate_image2 = models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image2.jpg'
        )
        
        serializer = self.serializer_class(instance=self.estate)
        data = serializer.data
        
        self.assertEqual(len(data['images']), 2)
        image_ids = [img['id'] for img in data['images']]
        self.assertIn(estate_image1.id, image_ids)
        self.assertIn(estate_image2.id, image_ids)


class SerializerIntegrationTest(BaseTestCase):
    """Integration tests for serializer interactions - Testing Framework: Django TestCase with Django REST Framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        from estate_data.serializers import EstateImageSerializer, EstateSerializer, EstateListSerializer
        self.estate_image_serializer = EstateImageSerializer
        self.estate_serializer = EstateSerializer
        self.estate_list_serializer = EstateListSerializer
        
    def test_serializer_inheritance_chain(self):
        """Test that all serializers properly inherit from ModelSerializer"""
        from rest_framework.serializers import ModelSerializer
        
        self.assertTrue(issubclass(self.estate_image_serializer, ModelSerializer))
        self.assertTrue(issubclass(self.estate_serializer, ModelSerializer))
        self.assertTrue(issubclass(self.estate_list_serializer, ModelSerializer))
    
    def test_estate_image_serializer_in_estate_serializer(self):
        """Test that EstateSerializer properly uses EstateImageSerializer"""
        estate_image = models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image.jpg'
        )
        
        serializer = self.estate_serializer(instance=self.estate)
        data = serializer.data
        
        self.assertIn('images', data)
        self.assertEqual(len(data['images']), 1)
        self.assertEqual(data['images'][0]['id'], estate_image.id)
    
    def test_estate_image_serializer_in_estate_list_serializer(self):
        """Test that EstateListSerializer properly uses EstateImageSerializer"""
        estate_image = models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image.jpg'
        )
        
        serializer = self.estate_list_serializer(instance=self.estate)
        data = serializer.data
        
        self.assertIn('images', data)
        self.assertEqual(len(data['images']), 1)
        self.assertEqual(data['images'][0]['id'], estate_image.id)
    
    def test_field_consistency_between_serializers(self):
        """Test that image fields are consistent between EstateSerializer and EstateListSerializer"""
        estate_serializer = self.estate_serializer()
        list_serializer = self.estate_list_serializer()
        
        # Both should use EstateImageSerializer for images
        self.assertEqual(type(estate_serializer.fields['images']).__name__, 'EstateImageSerializer')
        self.assertEqual(type(list_serializer.fields['images']).__name__, 'EstateImageSerializer')
        
        # Both should have many=True and read_only=True for images
        self.assertTrue(estate_serializer.fields['images'].many)
        self.assertTrue(estate_serializer.fields['images'].read_only)
        self.assertTrue(list_serializer.fields['images'].many)
        self.assertTrue(list_serializer.fields['images'].read_only)
    
    def test_serializer_context_propagation(self):
        """Test that context is properly propagated to nested serializers"""
        models.EstateImage.objects.create(
            estate=self.estate,
            image='test_image.jpg'
        )
        
        request = self.factory.get('/')
        context = {'request': request, 'custom_key': 'custom_value'}
        
        serializer = self.estate_serializer(instance=self.estate, context=context)
        data = serializer.data
        
        # Verify images are properly serialized with context
        self.assertIn('images', data)
        self.assertEqual(len(data['images']), 1)


class SerializerEdgeCaseTest(BaseTestCase):
    """Test edge cases and error conditions - Testing Framework: Django TestCase with Django REST Framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        from estate_data.serializers import EstateSerializer
        self.serializer_class = EstateSerializer
    
    def test_estate_serializer_empty_images_to_delete_list(self):
        """Test handling empty images_to_delete list"""
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': []
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_none_images_to_delete(self):
        """Test handling None value for images_to_delete"""
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': None
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        # This should not be valid as ListField doesn't accept None
        self.assertFalse(serializer.is_valid())
    
    def test_estate_serializer_invalid_images_to_delete(self):
        """Test handling invalid images_to_delete values"""
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': ['not', 'integers']
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertFalse(serializer.is_valid())
        self.assertIn('images_to_delete', serializer.errors)
    
    def test_estate_serializer_negative_images_to_delete(self):
        """Test handling negative image IDs in images_to_delete"""
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': [-1, -2]
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())  # Negative IDs are valid integers
    
    @patch('estate_data.models.EstateImage.objects.filter')
    def test_estate_serializer_update_nonexistent_images_to_delete(self, mock_filter):
        """Test updating with nonexistent image IDs to delete"""
        mock_queryset = Mock()
        mock_queryset.__iter__ = Mock(return_value=iter([]))
        mock_queryset.delete = Mock()
        mock_filter.return_value = mock_queryset
        
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': [999, 998]
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        # Should still work even if no images found
        mock_filter.assert_called_once_with(id__in=[999, 998], estate=self.estate)
        mock_queryset.delete.assert_called_once()
        self.assertEqual(updated_estate.estate_name, 'Updated Estate')
    
    def test_estate_serializer_partial_update(self):
        """Test partial updates work correctly"""
        data = {'estate_name': 'Partially Updated Estate'}
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_estate = serializer.save()
        
        self.assertEqual(updated_estate.estate_name, 'Partially Updated Estate')
        # Other fields should remain unchanged
        self.assertEqual(updated_estate.estate_government_id, 'GOV123')
    
    def test_estate_serializer_validation_error_message(self):
        """Test specific validation error message format"""
        data = {'estate_government_id': 'CHANGED_ID'}
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        
        error_detail = context.exception.detail
        self.assertEqual(str(error_detail[0]), 'Government ID cannot be changed once set!')
    
    def test_estate_serializer_invalid_estate_type(self):
        """Test serializer validation with invalid estate type"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'Invalid Type Estate',
            'estate_type': 'invalid_type',
            'estate_government_id': 'GOV999',
            'estate_price': '100000.00',
            'status': 'available'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('estate_type', serializer.errors)
    
    def test_estate_serializer_invalid_status(self):
        """Test serializer validation with invalid status"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'Invalid Status Estate',
            'estate_type': 'apartment',
            'estate_government_id': 'GOV999',
            'estate_price': '100000.00',
            'status': 'invalid_status'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)
    
    def test_estate_serializer_decimal_price_validation(self):
        """Test estate price decimal field validation"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'Price Test Estate',
            'estate_type': 'apartment',
            'estate_government_id': 'GOV999',
            'estate_price': 'not_a_number',
            'status': 'available'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('estate_price', serializer.errors)
    
    def test_estate_serializer_latitude_longitude_validation(self):
        """Test latitude and longitude decimal field validation"""
        data = {
            'seller': self.seller.id,
            'estate_name': 'Location Test Estate',
            'estate_type': 'apartment',
            'estate_government_id': 'GOV999',
            'estate_price': '100000.00',
            'status': 'available',
            'latitude': 'invalid_lat',
            'longitude': 'invalid_lng'
        }
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)
        self.assertIn('longitude', serializer.errors)
    
    def test_estate_serializer_missing_required_fields(self):
        """Test serializer validation with missing required fields"""
        data = {}
        
        serializer = self.serializer_class(data=data)
        self.assertFalse(serializer.is_valid())
        
        # Check that required fields are in errors
        required_fields = ['seller', 'estate_name', 'estate_type', 'estate_government_id', 'estate_price', 'status']
        for field in required_fields:
            self.assertIn(field, serializer.errors, f"Missing error for required field: {field}")
    
    @patch('estate_data.models.EstateImage.objects.filter')
    def test_estate_serializer_storage_error_handling(self, mock_filter):
        """Test handling storage errors during image deletion"""
        # Create mock image that raises exception on storage delete
        mock_image = Mock()
        mock_image.image.storage.exists.return_value = True
        mock_image.image.name = 'test.jpg'
        mock_image.image.storage.delete.side_effect = Exception("Storage error")
        
        mock_queryset = Mock()
        mock_queryset.__iter__ = Mock(return_value=iter([mock_image]))
        mock_queryset.delete = Mock()
        mock_filter.return_value = mock_queryset
        
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': [1]
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        
        # The save should still work even if storage deletion fails
        # This tests the resilience of the update method
        try:
            updated_estate = serializer.save()
            self.assertEqual(updated_estate.estate_name, 'Updated Estate')
        except Exception as e:
            # If an exception is raised, it should be a storage-related error
            self.assertIn("Storage error", str(e))
    
    def test_estate_serializer_large_images_to_delete_list(self):
        """Test handling large images_to_delete lists"""
        large_list = list(range(1000))  # 1000 image IDs
        data = {
            'estate_name': 'Updated Estate',
            'images_to_delete': large_list
        }
        
        serializer = self.serializer_class(instance=self.estate, data=data, partial=True)
        self.assertTrue(serializer.is_valid())