from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from churchmembers.models import Person


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_person(sender, instance, created, **kwargs):
    if created:
        try:
            Person.objects.get(user=instance)
        except Person.DoesNotExist:
            Person.create(user=instance)
