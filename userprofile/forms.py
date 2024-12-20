from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()


# 注册用户表单
class UserRegisterForm(UserCreationForm):
    # 添加email到默认的UserCreationForm
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ('username', 'email',)


# Profile的表单类
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # 定义表单包含的字段
        fields = ('phone', 'avatar', 'bio')
