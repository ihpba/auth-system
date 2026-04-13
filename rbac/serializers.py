"""
Сериализаторы для модуля RBAC.

Используются администратором для управления ролями, разрешениями
 и назначениями.
"""

from rest_framework import serializers

from rbac.models import Resource, Action, Role, Permission, UserRole


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ("id", "codename", "name", "description")
        read_only_fields = ("id",)


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = ("id", "codename", "name")
        read_only_fields = ("id",)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "codename", "name", "description")
        read_only_fields = ("id",)


class PermissionSerializer(serializers.ModelSerializer):
    """Разрешение с вложенным представлением роли, ресурса и действия."""

    role_codename = serializers.CharField(source="role.codename", read_only=True)
    resource_codename = serializers.CharField(source="resource.codename", read_only=True)
    action_codename = serializers.CharField(source="action.codename", read_only=True)

    class Meta:
        model = Permission
        fields = (
            "id",
            "role",
            "resource",
            "action",
            "role_codename",
            "resource_codename",
            "action_codename",
        )
        read_only_fields = ("id",)


class PermissionCreateSerializer(serializers.Serializer):
    """Сериализатор для создания разрешения по кодовым именам."""

    role_codename = serializers.SlugField()
    resource_codename = serializers.SlugField()
    action_codename = serializers.SlugField()

    def validate(self, data):
        from rbac.models import Role, Resource, Action

        role = Role.objects.filter(codename=data["role_codename"]).first()
        if not role:
            raise serializers.ValidationError({"role_codename": "Роль не найдена."})

        resource = Resource.objects.filter(codename=data["resource_codename"]).first()
        if not resource:
            raise serializers.ValidationError({"resource_codename": "Ресурс не найден."})

        action = Action.objects.filter(codename=data["action_codename"]).first()
        if not action:
            raise serializers.ValidationError({"action_codename": "Действие не найдено."})

        if Permission.objects.filter(role=role, resource=resource, action=action).exists():
            raise serializers.ValidationError("Такое разрешение уже существует.")

        data["role"] = role
        data["resource"] = resource
        data["action"] = action
        return data

    def create(self, validated_data):
        return Permission.objects.create(
            role=validated_data["role"],
            resource=validated_data["resource"],
            action=validated_data["action"],
        )


class UserRoleSerializer(serializers.ModelSerializer):
    """Назначение роли пользователю."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    role_codename = serializers.CharField(source="role.codename", read_only=True)

    class Meta:
        model = UserRole
        fields = ("id", "user", "role", "user_email", "role_codename")
        read_only_fields = ("id",)


class UserRoleCreateSerializer(serializers.Serializer):
    """Назначение роли по email и кодовому имени роли."""

    user_email = serializers.EmailField()
    role_codename = serializers.SlugField()

    def validate(self, data):
        from accounts.models import CustomUser
        from rbac.models import Role

        user = CustomUser.objects.filter(email=data["user_email"].lower(), is_active=True).first()
        if not user:
            raise serializers.ValidationError({"user_email": "Активный пользователь не найден."})

        role = Role.objects.filter(codename=data["role_codename"]).first()
        if not role:
            raise serializers.ValidationError({"role_codename": "Роль не найдена."})

        if UserRole.objects.filter(user=user, role=role).exists():
            raise serializers.ValidationError("Пользователю уже назначена эта роль.")

        data["user"] = user
        data["role"] = role
        return data

    def create(self, validated_data):
        return UserRole.objects.create(
            user=validated_data["user"],
            role=validated_data["role"],
        )


class UserPermissionsSummarySerializer(serializers.Serializer):
    """Сводка всех разрешений пользователя (для отладки и администрирования)."""

    user_email = serializers.EmailField()
    roles = serializers.ListField()
    permissions = serializers.ListField()
