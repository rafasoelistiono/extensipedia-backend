from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ("id", "created_at", "updated_at", "created_by", "updated_by")


class ApiRootSerializer(serializers.Serializer):
    name = serializers.CharField()
    version = serializers.CharField()
    public_base_url = serializers.URLField()
    admin_base_url = serializers.URLField()


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.CharField()
