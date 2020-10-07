from django.db.models.signals import post_save, pre_save, post_delete
from .models import Profile
from django.dispatch import receiver
from django.utils.text import slugify





@receiver(post_delete, sender=Profile)
def submission_delete(sender, instance, **kwargs):
    """
    When a profile is deleted the corresponding
     image is also deleted form media directory
    """
    instance.image.delete(False)


