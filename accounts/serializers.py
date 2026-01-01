from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claim(s)
        token['role'] = user.role  # or user.is_staff / user.is_superuser if you use that
        token['username'] = user.username  # optional

        return token

# class RegisterSerializer(serializers.ModelSerializer):
#     username = serializers.CharField(error_messages={
#         "required": "نام کاربری الزامی است",
#         "blank": "نام کاربری نمی‌تواند خالی باشد",
#         "unique": "این نام کاربری قبلاً ثبت شده است",
#     })

    

#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password],error_messages={
#         "required": "رمز عبور الزامی است",
#         "blank": "رمز عبور نمی‌تواند خالی باشد",
#         "min_length": "رمز عبور حداقل ۸ کاراکتر باشد",
#     })
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email',"verified","phone","discord", 'password', 'password2', 'role', 'profile_image']

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password2')
#         user = User.objects.create_user(**validated_data)
#         return user
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        error_messages={
            "required": "نام کاربری الزامی است",
            "blank": "نام کاربری نمی‌تواند خالی باشد",
        }
    )

    email = serializers.EmailField(
        error_messages={
            "required": "ایمیل الزامی است",
            "invalid": "ایمیل معتبر نیست",
        }
    )

    phone = serializers.CharField(
        max_length=15,
        required=False,
        allow_blank=True,
        allow_null=True, 
        error_messages={
            "max_length": "شماره موبایل نباید بیشتر از ۱۵ رقم باشد",
            "blank": "شماره موبایل نمی‌تواند خالی باشد",
        },
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "رمز عبور الزامی است",
            "blank": "رمز عبور نمی‌تواند خالی باشد",
        },
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "تکرار رمز عبور الزامی است",
            "blank": "تکرار رمز عبور نمی‌تواند خالی باشد",
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone",
            "verified",
            "discord",
            "password",
            "password2",
            "role",
            "profile_image",
        ]

        # جلوگیری از تمام validatorهای پیش‌فرض مدل
        extra_kwargs = {
            "email": {"validators": []},
            "username": {"validators": []},
            "phone": {"validators": []},
        }

    # ---------- FIELD VALIDATIONS ----------

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "کاربری با این ایمیل قبلاً ثبت شده است"
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "این نام کاربری قبلاً ثبت شده است"
            )
        return value

    def validate_phone(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError(
                "شماره موبایل فقط باید شامل عدد باشد"
            )
        return value

    # ---------- CROSS-FIELD VALIDATION ----------

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password": "رمز عبور و تکرار آن یکسان نیست"
            })

        try:
            validate_password(attrs["password"])
        except DjangoValidationError:
            raise serializers.ValidationError({
                "password": "رمز عبور باید حداقل ۸ کاراکتر و امن باشد"
            })

        return attrs

    # ---------- CREATE USER ----------

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user

    username = serializers.CharField(error_messages={
        "required": "نام کاربری الزامی است",
        "blank": "نام کاربری نمی‌تواند خالی باشد",
    })

    email = serializers.EmailField(error_messages={
        "required": "ایمیل الزامی است",
        "invalid": "ایمیل معتبر نیست",
    })

    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "رمز عبور الزامی است",
            "blank": "رمز عبور نمی‌تواند خالی باشد",
        },
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "تکرار رمز عبور الزامی است",
            "blank": "تکرار رمز عبور نمی‌تواند خالی باشد",
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "verified",
            "phone",
            "discord",
            "password",
            "password2",
            "role",
            "profile_image",
        ]

        # جلوگیری از unique validator پیش‌فرض
        extra_kwargs = {
            "email": {"validators": []},
            "username": {"validators": []},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "کاربری با این ایمیل قبلاً ثبت شده است"
            )
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "این نام کاربری قبلاً ثبت شده است"
            )
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({
                "password": "رمز عبور و تکرار آن یکسان نیست"
            })

        try:
            validate_password(attrs["password"])
        except DjangoValidationError:
            raise serializers.ValidationError({
                "password": "رمز عبور باید حداقل ۸ کاراکتر و امن باشد"
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user



# serializers.py

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "username","verified","phone","discord", "email", "role", "profile_image"]


#     def update(self, instance, validated_data):
#         request = self.context["request"]

#         # user → only own discord
#         if request.user == instance and not request.user.is_admin and not request.user.is_owner:
#             validated_data = {
#                 "discord": validated_data.get("discord", instance.discord)
#             }

#         return super().update(instance, validated_data)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username","verified","phone","discord", "email", "role", "profile_image"]

    def update(self, instance, validated_data):
        request = self.context["request"]

        # Normal users → only discord
        if request.user == instance and not request.user.is_admin and not request.user.is_owner:
            if "discord" in validated_data:
                instance.discord = validated_data["discord"]
            instance.save()
            return instance

        # Admins/Owners → normal update
        return super().update(instance, validated_data)
