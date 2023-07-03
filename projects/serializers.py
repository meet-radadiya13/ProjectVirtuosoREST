from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.serializers import UserCreationSerializer
from projects.models import Project


class ProjectUserSerializer(UserCreationSerializer):
    class Meta:
        model = UserCreationSerializer.Meta.model
        fields = ('id',)


class ProjectCreationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100, allow_null=True,
        allow_blank=True
    )
    acronym = serializers.CharField(
        max_length=3, allow_null=True,
        allow_blank=True
    )
    assign = ProjectUserSerializer(
        allow_null=True,
    )
    is_completed = serializers.BooleanField(
        allow_null=True,
    )
    dead_line = serializers.DateField(allow_null=True, )
    description = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=True
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
            username = attrs.get('username')
            if username and username != self.instance.username:
                if User.objects.filter(
                        username=username
                ).exclude(
                    id=self.instance.id
                ).exists():
                    raise ValidationError({"detail": "username is taken"})
                attrs["username"] = username
            return attrs


class ProjectUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100, allow_null=True,
        allow_blank=True
    )
    acronym = serializers.CharField(
        max_length=3, allow_null=True,
        allow_blank=True
    )
    is_completed = serializers.BooleanField(
        allow_null=True,
    )
    description = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Project
        fields = ('name', 'acronym', 'is_completed', 'description')


class ProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'acronym', 'assign', 'is_completed', 'dead_line',
            'description', 'tags', 'created_at', 'updated_at', 'created_by',
            'updated_by',)
