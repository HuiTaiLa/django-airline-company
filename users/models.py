from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.contrib.auth.hashers import make_password
# Create your models here.

class UserManager(BaseUserManager):

    def create_user(self, pass_word=None, **other_fields):
        # print(pass_word)
        # print(make_password(pass_word))
        user = self.model(**other_fields)
        user.set_password(make_password(pass_word))
        user.save()
        return user

class User(AbstractUser):
    user_id = models.AutoField(primary_key=True, blank=True, null=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone_number = models.IntegerField(blank=True, null=True)
    pass_word = models.CharField(max_length=100)
    balance = models.IntegerField(blank=True, null=True)

    objects = UserManager()

    def __str__(self):
          return f"{self.first_name} {self.last_name}"