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
        required=False,
        allow_blank=True,
        error_messages={
            'invalid': '請輸入有效的電話號碼',
        }
    )
    birthday = serializers.DateField(
        required=False,
        allow_null=True,
        input_formats=['%Y-%m-%d'],
        error_messages={
            'invalid': '請輸入正確的日期格式 (YYYY-MM-DD)',
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

    def validate_email(self, value):
        """檢查 email 是否已被使用"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("此電子郵件已被註冊，請使用其他電子郵件或嘗試登入。")
        return value
    
    def validate_username(self, value):
        """檢查 username 是否已被使用"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("此使用者名稱已被使用，請選擇其他名稱。")
        return value

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"password": "密碼不一致"})
        return attrs

    def create(self, validated_data):
        # Remove password1 and password2 from validated_data
        password = validated_data.pop('password1')
        validated_data.pop('password2', None)  # Remove password2 if it exists
        
        try:
            # Create user with remaining data
            user = User.objects.create_user(**validated_data)
            
            # Set password properly
            user.set_password(password)
            user.save()
            
            return user
        except Exception as e:
            # 處理可能的資料庫錯誤（如唯一性約束違反）
            error_msg = str(e)
            if 'email' in error_msg.lower() or 'email' in str(e):
                raise serializers.ValidationError({"email": "此電子郵件已被註冊，請使用其他電子郵件或嘗試登入。"})
            elif 'username' in error_msg.lower() or 'username' in str(e):
                raise serializers.ValidationError({"username": "此使用者名稱已被使用，請選擇其他名稱。"})
            else:
                raise serializers.ValidationError({"non_field_errors": [f"註冊失敗：{error_msg}"]})
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        # mark any sensitive fields as read_only if you like
        read_only_fields = ('id', 'username', 'email')
