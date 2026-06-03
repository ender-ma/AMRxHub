from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .signals import object_viewed_signal

User = settings.AUTH_USER_MODEL

class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    viewed_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} viewed {self.content_object} on {self.viewed_on.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name_plural = "Histories"
        ordering = ['-viewed_on']

def object_viewed_receiver(sender, instance, request, **kwargs):
    if request.user.is_authenticated:
        History.objects.create(user=request.user, content_object=instance)

object_viewed_signal.connect(object_viewed_receiver)