from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class store:
    id = models.IntegerField(_("ID"),primary_key=True, unique=True)
    title = models.CharField(_("Title"), max_length=100, null=False, blank = False)
    description = models.CharField(_("Description"), max_length=256)
    s_type = models.CharField(_("Store Type"), max_length=50)
    price = models.IntegerField(_("Prc"), null=False, blank=False)
    display_picture = models.CharField(_("Display Picture"), max_length=256,null=False)
    pictures = models.JSONField(_("Pictures"), default=dict)
    comments = models.JSONField(_("Comments"), default=dict)
    user_id = models.ForeignKey("users.core_user", verbose_name=_("Owned By User"), on_delete=models.CASCADE)



