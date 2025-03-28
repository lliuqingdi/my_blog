from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, verbose_name="电话")
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True, verbose_name="头像")
    bio = models.TextField(max_length=500, blank=True, verbose_name="个人简介")
    following = models.ManyToManyField("self", symmetrical=False, related_name="followers", blank=True,
                                       verbose_name="关注关系")

    def __str__(self):
        return 'user {}'.format(self.user.username)

    class Meta:
        verbose_name_plural = '个人简介'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
