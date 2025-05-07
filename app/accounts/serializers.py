# accounts/serializers.py

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    # here are the two fields you declared…
    password1 = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'birthday', 'password1', 'password2')

    def validate(self, attrs):
        if attrs['password1'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        pwd = validated_data.pop('password1')
        # Strip out password2 since we only need it for validation
        validated_data.pop('password2', None)

        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        # mark any sensitive fields as read_only if you like
        read_only_fields = ('id', 'username', 'email')
