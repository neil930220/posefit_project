# accounts/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()



class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': '這個欄位不能留空',
            'required': '這個欄位不能留空',
            'invalid': '請輸入有效的電子郵件',
        }
    )
    phone = serializers.CharField(
        required=True,
        error_messages={
            'blank': '這個欄位不能留空',
            'required': '這個欄位不能留空',
        }
    )
    birthday = serializers.DateField(
        required=True,
        input_formats=['%Y-%m-%d'],
        error_messages={
            'invalid': '請輸入正確的日期格式 (YYYY-MM-DD)',
            'blank': '這個欄位不能留空',
            'required': '這個欄位不能留空',
        }
    )
    password1 = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        error_messages={
            'blank': '這個欄位不能留空',
            'required': '這個欄位不能留空',
        }
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'blank': '這個欄位不能留空',
            'required': '這個欄位不能留空',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'birthday', 'password1', 'password2')
        extra_kwargs = {
            'username': {
                'required': True,
                'error_messages': {
                    'blank': '這個欄位不能留空',
                    'required': '這個欄位不能留空',
                }
            }
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "密碼不一致"})
        return attrs
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        # mark any sensitive fields as read_only if you like
        read_only_fields = ('id', 'username', 'email')
