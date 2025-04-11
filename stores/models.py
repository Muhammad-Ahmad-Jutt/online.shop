from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CoreUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
class Store(models.Model):
    id = models.AutoField(_("ID"), primary_key=True)  # AutoField will automatically generate the ID value
    title = models.CharField(_("Title"), max_length=100, null=False, blank=False,unique=True)
    description = models.CharField(_("Description"), max_length=256)
    store_category = models.ForeignKey('Category', verbose_name=_("Store Category"), on_delete=models.SET_NULL, null=True, blank=True, default=None)
    completed_orders = models.IntegerField(_("Completed Orders"), default=0)
    store_address = models.CharField(_("Store Address"), max_length=256, null=False, blank=False, default='Virtual')
    store_phone = PhoneNumberField(_("Store Phone Number"), unique=True, blank=True, null=True)
    store_email = models.EmailField(_("Store Email"), max_length=100, null=True, blank=True)  # EmailField for store email
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    activate = models.BooleanField(_("Activate"), default=True)
    user_id = models.ForeignKey('users.CoreUser', verbose_name=_("Owned By User"), on_delete=models.CASCADE)
    ntn_number = models.CharField(_("NTN Number"), max_length=20, null=True, blank=True)
    store_bank_account_no = models.CharField(_("Store Bank Account No"), max_length=30, null=True, blank=True)
    store_website = models.URLField(_("Store Website"), max_length=200, null=True, blank=True)
    store_fb = models.URLField(_("Store Facebook"), max_length=200, null=True, blank=True)
    store_youtube = models.URLField(_("Store YouTube"), max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title

from django.db import models

class Category(models.Model):
    id = models.AutoField(_("ID"), primary_key=True,unique=True)  # Automatically increments
    category_title = models.CharField(_("Title"), max_length=30, null=False, blank=False)  # Ensure category title is unique
    parent_category = models.ForeignKey('self', verbose_name='Parent Category', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(CoreUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.category_title
    
    class Meta:
            constraints = [
            models.UniqueConstraint(fields=['category_title', 'parent_category'], name='unique_category_title_per_parent')
        ]


        # This method will ensure that the "General" category is created by default
    # @classmethod
    # def create_default_category(cls):
    #     if not cls.objects.filter(category_title="General").exists():
    #         cls.objects.create(category_title="General")

class Store_Images(models.Model):
    id = models.AutoField(_("ID"), primary_key=True,unique=True)  # Automatically increments
    store_id = models.ForeignKey(Store, verbose_name=_("Store Image"), on_delete=models.CASCADE)
    image = models.ImageField(upload_to="store_images/")  # S3 will store it in media/store_images/
    display = models.BooleanField(_("dp"), default=False)
    user_id = models.ForeignKey(CoreUser, on_delete=models.CASCADE, null=True, blank=True)
   
    class Meta:
        pass

    def save(self, *args, **kwargs):
        if self.display:
            # Ensure only one image per store is set to display=True
            # This will uncheck 'display' for all other images in the store before saving
            Store_Images.objects.filter(store_id=self.store_id, display=True).update(display=False)
        super().save(*args, **kwargs)  # Save the image instance

class Store_Review(models.Model):
    id = models.AutoField(_("ID"), primary_key=True,unique=True)  # Automatically increments
    store_id = models.ForeignKey(Store, verbose_name=_("Store Review"), on_delete=models.CASCADE)
    user_id = models.ForeignKey(CoreUser, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.CharField(_("comment"), max_length=200)
    ratings = models.DecimalField(_("Ratings"), max_digits=3, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'store_id'], name='unique_user_per_store')
        ]

    def __str__(self):
        return f"{self.user_id}--->{self.store}---->{self.comment}"
    
