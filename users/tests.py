from django.test import TestCase

# Create your tests here.
from django.contrib.auth.hashers import make_password
# 设置密码
res = make_password('aabbcc')