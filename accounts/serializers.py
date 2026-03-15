from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import TokenError

from accounts.models import User
from core.serializers import BaseModelSerializer
from accounts.services import blacklist_refresh_token


class CurrentUserSerializer(BaseModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "avatar",
            "role",
            "is_staff",
            "is_superuser",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AdminUserSerializer(BaseModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    role = serializers.ChoiceField(choices=User.Roles.choices, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "avatar",
            "role",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        read_only_fields = BaseModelSerializer.Meta.read_only_fields + ("is_staff", "is_superuser")

    def _apply_role(self, validated_data):
        role = validated_data.pop("role", None)
        if role is None and self.instance is None:
            role = User.Roles.ADMIN
        if role == User.Roles.SUPERADMIN:
            validated_data["is_staff"] = True
            validated_data["is_superuser"] = True
        elif role == User.Roles.ADMIN:
            validated_data["is_staff"] = True
            validated_data["is_superuser"] = False
        return validated_data

    def create(self, validated_data):
        validated_data = self._apply_role(validated_data)
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data = self._apply_role(validated_data)
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AdminLoginSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.can_access_admin_panel:
            raise AuthenticationFailed("You do not have admin panel access.")
        data["user"] = CurrentUserSerializer(self.user, context=self.context).data
        return data


class AdminTokenRefreshSerializer(TokenRefreshSerializer):
    pass


class AdminLogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        try:
            blacklist_refresh_token(self.validated_data["refresh"])
        except TokenError as exc:
            raise serializers.ValidationError({"refresh": ["Refresh token is invalid or already blacklisted."]}) from exc
