from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class product:
    id = models.IntegerField(_("id"),primary_key=True, unique=True)
    title = models.CharField(_("title"), max_length=100, null=False, blank = False)
    description = models.CharField(_("description"), max_length=256)
    quantity = models.IntegerField(_("quantity"), default = 0)
    price = models.IntegerField(_("price"), null=False, blank=False)
    display_picture = models.CharField(_("Display Picture"), max_length=256,null=False)
    pictures = models.JSONField(_("Pictures"), default=dict)
    comments = models.JSONField(_("Comments"), default=dict)
    store_id = models.ForeignKey("stores.store", verbose_name=_(""), on_delete=models.CASCADE)
    user_id = models.ForeignKey("users.core_user", verbose_name=_("maintained_by_user"), on_delete=models.CASCADE)