from rest_framework import serializers
from rest_framework.authtoken.admin import User

from projects.models import Project


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
        allow_null=True, many=True, queryset=User.objects.all()
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
        return super().validate(attrs)


class ProjectUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100, allow_null=False,
        allow_blank=False
    )
    acronym = serializers.CharField(
        max_length=3, allow_null=False,
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
        fields = ('name', 'acronym', 'is_completed', 'description')

    def update(self, instance, validated_data):
        current_user = self.context['user']
        validated_data['updated_by'] = current_user
        return super().update(instance, validated_data)


class ProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'acronym', 'assign', 'is_completed', 'dead_line',
            'description', 'tags', 'created_at', 'updated_at', 'created_by',
            'updated_by',)
