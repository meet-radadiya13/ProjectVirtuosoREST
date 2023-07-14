from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.admin import User

from projects.models import AuditHistory, Project


class ProjectCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100, allow_null=False,
        allow_blank=False
    )
    acronym = serializers.CharField(
        max_length=3, allow_null=False,
        allow_blank=False
    )
    assign = serializers.PrimaryKeyRelatedField(
        allow_null=True, many=True,
        queryset=User.objects.exclude(is_active=False)
    )
    is_completed = serializers.BooleanField(
        default=False,
    )
    dead_line = serializers.DateTimeField(allow_null=True, )
    description = serializers.CharField(
        max_length=500, allow_null=False, allow_blank=False
    )
    tags = serializers.ListField(
        child=serializers.CharField()
    )

    class Meta:
        model = Project
        fields = (
            'name', 'acronym', 'assign', 'is_completed', 'dead_line',
            'description', 'tags',)

    def validate(self, attrs):
        current_user = self.context['user']
        assign = attrs['assign']
        for user in assign:
            if user.company != current_user.company:
                raise serializers.ValidationError(
                    'You can not assign project to this user.'
                )
        attrs['created_by'] = current_user
        return attrs


class ProjectUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100, allow_null=False,
        allow_blank=False
    )
    is_completed = serializers.BooleanField(
        default=False,
    )
    description = serializers.CharField(
        max_length=500, allow_null=False, allow_blank=False
    )

    class Meta:
        model = Project
        fields = ('name', 'is_completed', 'description')

    def update(self, instance, validated_data):
        current_user = self.context['user']
        validated_data['updated_by'] = current_user
        return super(ProjectUpdateSerializer, self).update(
            instance,
            validated_data
        )


class ProjectDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        if isinstance(self.context.get('offset'), float):
            offset = float(self.context.get('offset'))
            created_at = obj.created_at + timezone.timedelta(minutes=offset)
            return created_at.strftime("%Y-%m-%d %H:%M:%S")
        return obj.created_at

    def get_updated_at(self, obj):
        if isinstance(self.context.get('offset'), float):
            offset = float(self.context.get('offset'))
            updated_at = obj.updated_at + timezone.timedelta(minutes=offset)
            return updated_at.strftime("%Y-%m-%d %H:%M:%S")
        return obj.updated_at

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'acronym', 'assign', 'is_completed', 'dead_line',
            'description', 'tags', 'created_at', 'updated_at', 'created_by',
            'updated_by',)


class AuditHistorySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        if self.context.get('offset').isinstance(float):
            offset = float(self.context.get('offset'))
            created_at = obj.created_at + timezone.timedelta(minutes=offset)
            return created_at.strftime("%Y-%m-%d %H:%M:%S")
        return obj.created_at

    def get_updated_at(self, obj):
        if self.context.get('offset').isinstance(float):
            offset = float(self.context.get('offset'))
            updated_at = obj.updated_at + timezone.timedelta(minutes=offset)
            return updated_at.strftime("%Y-%m-%d %H:%M:%S")
        return obj.updated_at

    class Meta:
        model = AuditHistory
        fields = (
            'id', 'task', 'project', 'action', 'action_by', 'user_from',
            'user_to', 'created_at', 'updated_at', 'is_deleted',)
