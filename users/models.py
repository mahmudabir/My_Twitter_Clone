from django.db import models

from django.contrib.auth.models import (User, AbstractBaseUser,
                                        BaseUserManager, PermissionsMixin)
from PIL import Image
from django.utils import timezone


# Create your models here.
class ProfileManager(BaseUserManager):
    """
    docstring
    """
    def _create_user(self, username, name, email, password, **extra_fields):
        if not username:
            raise ValueError("Users must have an Email Address.")
        if not email:
            raise ValueError("Users must have an Username.")
        if not name:
            raise ValueError("Users must have an email Name.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            name=name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,
                         username,
                         name,
                         email,
                         password=None,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_user', False)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Superuser must have is_admin=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_user') is not False:
            raise ValueError('Superuser must have is_admin=False.')

        return self._create_user(username=username,
                                 name=name,
                                 email=email,
                                 password=password,
                                 **extra_fields)

    def create_user(self,
                    username,
                    name,
                    email,
                    password=None,
                    **extra_fields):

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_user', True)

        if extra_fields.get('is_staff') is not False:
            raise ValueError('User must have is_staff=False.')
        if extra_fields.get('is_superuser') is not False:
            raise ValueError('User must have is_superuser=False.')
        if extra_fields.get('is_admin') is not False:
            raise ValueError('Superuser must have is_admin=False.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_user') is not True:
            raise ValueError('Superuser must have is_admin=True.')

        return self._create_user(username=username,
                                 name=name,
                                 email=email,
                                 password=password,
                                 **extra_fields)


class Profile(AbstractBaseUser, PermissionsMixin):
    """
    docstring
    """

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    name = models.CharField(max_length=150)
    date_of_birth = models.DateField(blank=True, null=True)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    date_joined = models.DateTimeField(verbose_name='date joined',
                                       auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', default=timezone.now)
    is_admin = models.BooleanField(verbose_name='Admin', default=False)
    is_staff = models.BooleanField(verbose_name='Staff', default=False)
    is_superuser = models.BooleanField(verbose_name='Super User', default=False)
    is_active = models.BooleanField(verbose_name='Active', default=True)
    is_user = models.BooleanField(verbose_name='User',default=True)

    objects = ProfileManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return f'{self.username} Profile'

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def followers(self):
        return Follow.objects.filter(follow_user=self.user).count()

    @property
    def following(self):
        return Follow.objects.filter(user=self.user).count()

    def save(self,
             force_insert=False,
             force_update=False,
             using=None,
             update_fields=None):
        super().save()

        if self.is_superuser == False:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
        else:
            pass


class Follow(models.Model):
    user = models.ForeignKey(Profile,
                             related_name='user',
                             on_delete=models.CASCADE)
    follow_user = models.ForeignKey(Profile,
                                    related_name='follow_user',
                                    on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
