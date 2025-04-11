from django.db.models.signals import post_migrate
from django.dispatch import receiver
from stores.models import Category

@receiver(post_migrate)
def create_general_category(sender, **kwargs):
    # Create the 'General' category if it doesn't exist
    # Category.create_default_category()
    pass