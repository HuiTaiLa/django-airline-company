from django.db import models
# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True, blank=True, null=False)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    phone_number = models.IntegerField(blank=True, null=True)
    pass_word = models.CharField(max_length=100)
    balance = models.IntegerField(blank=True, null=True)

    def __str__(self):
          return f"{self.first_name} {self.last_name}"