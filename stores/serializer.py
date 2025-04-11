from users.tasks import send_mail_to_user
from rest_framework import serializers
from stores.models import Store,Category,Store_Review
import logging
from phonenumber_field.serializerfields import PhoneNumberField

logger = logging.getLogger(__name__)

class GetReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store_Review
        fields = ['id', 'store_id', 'user_id', 'ratings', 'comment']

class PostReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store_Review
        fields = ['id', 'store_id', 'user_id', 'ratings','comment']
        extra_kwargs = {
            "id": {"read_only": True},
            "store_id": {"required": False},  
            "user_id": {"read_only": True},
            "ratings":{"required":True},
            "comment": {"required": True}
        }

    def create(self, validated_data):
        # Get the current user from the request context
        user = self.context['request'].user
        
        # Create and save the new review
        review = Store_Review(
            user_id=user,
            store_id=validated_data['store_id'],  # Store instance passed in validated_data
            comment=validated_data['comment'],
            ratings=validated_data['ratings']
        )
        review.save()
        return review


class UpdateCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'category_title', 'parent_category', 'created_at', 'user_id']
        extra_kwargs = {
            "id": {"read_only": True},
            "user_id": {"read_only": True},
            "created_at": {"read_only": True},
            "category_title": {"required": True},
            "parent_category": {"required": False}
            }

    def validate_parent_category(self, value):
        if value is not None:
            try:
                category = Category.objects.filter(id=value.id).first()

            except Category.DoesNotExist:
                raise serializers.ValidationError("category not found------------->")
            return category
        return value
        
    def update(self, instance, validated_data):
        # Ensure 'user_id' is not updated
        # validated_data.pop('user_id', None)

        # Update each field present in validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CategoryListingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Category
        fields = [
            "id",
            "category_title",
            "parent_category",
            "user_id"
        ]


    def to_representation(self, instance):
        """Customize the response to return only the store related to the user"""
        return super().to_representation(instance)
class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "category_title",
            "parent_category",
            "user_id"
        ]
        # No need for required_fields. Use the `required` argument for the serializer field
        extra_kwargs = {
            'category_title': {'required': True},  # Ensuring category_title is required
            'parent_category': {'required':False},
            'id': {'read_only': True}  # id should be read-only
        }
    def validate_parent_category(self, value):
        if isinstance(value, int):
            category = Category.object.get(id=value)
            if not category:
                raise serializers.ValidationError("category not found")
            return category
        return value
    def create(self, validated_data):
        # Add the user dynamically to the validated data
        validated_data['user_id'] = self.context['request'].user
        return super().create(validated_data)
class CreateStoreSerializer(serializers.ModelSerializer):
    # store_phone = serializers.CharField(source='store_phone.as_e164', read_only=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "title",
            "description",
            "store_category",
            "completed_orders",
            "store_address",
            "store_phone",
            "store_email",
            "created_at",
            "activate",
            # "user_id",
            "ntn_number",
            "store_bank_account_no",
            "store_website",
            "store_fb",
            "store_youtube",
        ]
        # read_only_fields = ["id", "created_at", "total_reviews", "store_ratings"]
        extra_kwargs = {
            'id': {'read_only': True}, 
            'created_at': {'read_only': True},  
            'total_reviews': {'read_only': True},  
            'store_ratings': {'read_only':True},
            'title': {'required': True},  
            'description': {'required': True},  
            'store_category': {'required': True},  
            'store_phone': {'required': True},  # Ensure it's required
            'store_email': {'required': True},  
            }
    def create(self, validated_data):
        # Add the authenticated user's ID to validated data
        user = self.context['request'].user  # Get the user from the context
        validated_data['user_id'] = user  # Assign the user object to validated data
        
        # Now call the parent class's create method
        return super().create(validated_data)

    def validate(self, data):
        """Ensure required fields are provided."""
        # required_fields = ["title", "description", "store_category", "store_phone", "store_email"]
        # for field in required_fields:
        #     print(field,'------->',data.get(field),'\n\n\n\n')
        #     if not data.get(field):
        #         raise serializers.ValidationError({field: f"{field} is required."})
        return data
    def validate_store_pictures(self, value):
        if value and not isinstance(value, list):
            raise serializers.ValidationError("store_pictures must be a list of URLs.")
        if value:
            for url in value:
                # Simple URL validation (you can customize this as needed)
                if not url.startswith("http://") and not url.startswith("https://"):
                    raise serializers.ValidationError(f"{url} is not a valid URL.")
        return value
        
    def validate_store_email(self, value):
        """Ensure store email is unique."""
        if Store.objects.filter(store_email=value).exists():
            raise serializers.ValidationError("A store with this email already exists.")
        return value

    def validate_store_phone(self, value):
        """Ensure store phone number is unique."""
        if Store.objects.filter(store_phone=value).exists():
            raise serializers.ValidationError("A store with this phone number already exists.")
        return value


class StoreUpdateSerializer(serializers.ModelSerializer):
    store_phone = PhoneNumberField(required=False, allow_null=True)
    
    class Meta:
        model = Store
        fields = [
            'title',
            'description',
            'store_category',
            'store_address',
            'store_phone',
            'store_email',
            'ntn_number',
            'store_bank_account_no',
            'store_website',
            'store_fb',
            'store_youtube',
            'activate'
        ]
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': False},
            'description': {'required': False, 'allow_blank': False},
            'store_address': {'required': False, 'allow_blank': False},
            'store_email': {'required': False, 'allow_blank': True},
        }

    def validate_title(self, value):
        """
        Check that the title is unique (excluding the current instance)
        """
        instance = self.instance
        if instance and Store.objects.exclude(pk=instance.pk).filter(title=value).exists():
            raise serializers.ValidationError("A store with this title already exists.")
        return value

    def validate_store_phone(self, value):
        """
        Check that the phone number is unique (excluding the current instance)
        """
        instance = self.instance
        if instance and value and Store.objects.exclude(pk=instance.pk).filter(store_phone=value).exists():
            raise serializers.ValidationError("A store with this phone number already exists.")
        return value
        
class GetStoreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Store
        fields = [
            "id",
            "title",
            "description",
            "store_category",
            "completed_orders",
            "store_address",
            "store_phone",
            "store_email",
            "created_at",
            "activate",
            "user_id",
            "ntn_number",
            "store_bank_account_no",
            "store_website",
            "store_fb",
            "store_youtube",
        ]


    def to_representation(self, instance):
        """Customize the response to return only the store related to the user"""
        return super().to_representation(instance)