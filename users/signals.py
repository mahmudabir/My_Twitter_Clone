from django.db.models.signals import post_save, pre_save, post_delete
from .models import Profile
from django.dispatch import receiver
from django.utils.text import slugify




# signal that gets fired after the user is saved
@receiver(post_delete, sender=Profile)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)