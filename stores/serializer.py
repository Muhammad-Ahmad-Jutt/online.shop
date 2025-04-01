from users.tasks import send_mail_to_user
from stores.models import store
from rest_framework import serializers
from stores.models import Store
import logging

logger = logging.getLogger(__name__)


class StoreCreateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='phone_number.as_e164', read_only=True)
    
    class Meta:
        model = Store
        fields = [
            "id",
            "title",
            "description",
            "store_category",
            "completed_orders",
            "store_display_picture",
            "store_pictures",
            "store_address",
            "store_phone",
            "store_email",
            "store_ratings",
            "total_reviews",
            "created_at",
            "activate",
            "user_id",
            "ntn_number",
            "store_bank_account_no",
            "store_website",
            "store_fb",
            "store_youtube",
        ]
        read_only_fields = ["id", "created_at", "total_reviews", "store_ratings"]

    def validate(self, data):
        """Ensure required fields are provided."""
        required_fields = ["title", "description", "store_category", "store_phone", "store_email"]
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: f"{field} is required."})
        return data

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
    
    class Meta:
        model = Store
        fields = [
            "id",
            "title",
            "description",
            "store_category",
            "completed_orders",
            "store_display_picture",
            "store_pictures",
            "store_address",
            "store_phone",
            "store_email",
            "store_ratings",
            "total_reviews",
            "created_at",
            "activate",
            "user_id",
            "ntn_number",
            "store_bank_account_no",
            "store_website",
            "store_fb",
            "store_youtube",
        ]
        read_only_fields = ["id", "created_at", "total_reviews", "store_ratings"]
    def validate(self,data):
        if not data:
            raise serializers.ValidationError("No Data Provided")
        return data
    def update_store(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
class GetStoreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Store
        fields = [
            "id",
            "title",
            "description",
            "store_category",
            "completed_orders",
            "store_display_picture",
            "store_pictures",
            "store_address",
            "store_phone",
            "store_email",
            "store_ratings",
            "total_reviews",
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
        return super().to_representation(store)