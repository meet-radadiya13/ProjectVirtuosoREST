import base64
import binascii
import imghdr
import os
import six
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.authtoken.admin import User
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from projects.models import Project, Task, Attachment


class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:'):
            format, encoded_content = data.split(';base64,')
            content_type = format.split(':')[1]
            decoded_content = base64.b64decode(encoded_content)
            file_name = str(binascii.hexlify(os.urandom(6)).decode())
            file_extension = content_type.split('/')[-1]
            complete_file_name = "%s.%s" % (file_name, file_extension)
            data = ContentFile(decoded_content, name=complete_file_name)
            data.content_type = content_type
            data.name = complete_file_name
            return data
        return super(Base64FileField, self).to_internal_value(data)
# class Base64ImageField(serializers.ImageField):
#     """
#     Decode Base64 to Image.
#     """
#
#     def to_internal_value(self, data):
#         if isinstance(data, six.string_types):
#             if 'data:' in data and ';base64,' in data:
#                 header, data = data.split(';base64,')
#                 try:
#                     decoded_file = base64.b64decode(data)
#                 except Exception as e:
#                     print("exception", e)
#                     self.fail('invalid_image')
#                 if decoded_file:
#                     file_name = str(binascii.hexlify(os.urandom(6)).decode())
#                     file_extension = self.get_file_extension(
#                         file_name, decoded_file
#                     )
#                     if file_extension.lower() not in ['png', 'jpg', 'jpeg',
#                                                       'gif']:
#                         raise ValidationError(
#                             {'detail': 'please upload valid image.'}
#                         )
#                     complete_file_name = "%s.%s" % (file_name, file_extension,)
#                     data = ContentFile(decoded_file, name=complete_file_name)
#                     if data.size > 5242880:
#                         raise ValidationError(
#                             {'detail': 'please upload image '
#                                        'with less then 5MB size.'}
#                         )
#                     else:
#                         pass
#         return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension

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


class ProjectDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'acronym', 'assign', 'is_completed', 'dead_line',
            'description', 'tags', 'created_at', 'updated_at', 'created_by',
            'updated_by',)


class TaskCreationSerializer(serializers.ModelSerializer):
    CHOICES = [
        ("task", "Task"),
        ("bug", "Bug"),
    ]
    STATUS_CHOICES = [
        ("todo", "TODO"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]
    PRIORITY_CHOICES = [
        ("hi", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]
    name = serializers.CharField(
        max_length=100, allow_null=False,
        allow_blank=False
    )
    assign = serializers.PrimaryKeyRelatedField(
        allow_null=True, many=True, queryset=User.objects.all()
    )
    project = serializers.PrimaryKeyRelatedField(
        allow_null=True, many=True, queryset=Project.objects.all()
    )
    description = serializers.CharField(
        max_length=500, allow_null=False, allow_blank=False
    )
    task_type = serializers.ChoiceField(choices=CHOICES)
    task_status = serializers.ChoiceField(choices=STATUS_CHOICES)
    task_priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)

    class Meta:
        model = Task
        fields = (
            'name', 'assign', 'project', 'description',
            'task_type', 'task_status', 'task_priority')

    def validate(self, attrs):
        project_id = attrs["project"][0].id
        related_project = Project.objects.get(id=project_id)
        task_acronym_partial = related_project.acronym
        task_count = Task.objects.filter(
            project=project_id).exclude(is_deleted=True).count() + 1
        task_acronym_partial += "-" + str(task_count)
        current_user = self.context['user']
        attrs['task_acronym'] = task_acronym_partial
        attrs['project'] = attrs['project'][0]
        attrs['assign'] = attrs['assign'][0]
        attrs['created_by'] = current_user
        attrs['updated_by'] = current_user
        if attrs['assign'].company != current_user.company:
            raise serializers.ValidationError(
                'You can not assign Task to this user.'
            )
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    CHOICES = [
        ("task", "Task"),
        ("bug", "Bug"),
    ]
    STATUS_CHOICES = [
        ("todo", "TODO"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]
    PRIORITY_CHOICES = [
        ("hi", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]
    name = serializers.CharField(
        max_length=100, allow_null=False,
        allow_blank=False
    )
    description = serializers.CharField(
        max_length=500, allow_null=False, allow_blank=False
    )
    assign = serializers.PrimaryKeyRelatedField(
        allow_null=True, many= True,queryset=User.objects.all()
    )
    task_type = serializers.ChoiceField(choices=CHOICES)
    task_status = serializers.ChoiceField(choices=STATUS_CHOICES)
    task_priority = serializers.ChoiceField(choices=PRIORITY_CHOICES)

    class Meta:
        model = Task
        fields = (
            'name', 'description', 'assign', 'task_type', 'task_status', 'task_priority',
        )

    def validate(self, attrs):
        project_id = self.context['project'].id
        related_project = Project.objects.get(id=project_id)
        task_acronym_partial = related_project.acronym
        task_count = Task.objects.filter(
            project=project_id).exclude(is_deleted=True).count() + 1
        task_acronym_partial += "-" + str(task_count)
        attrs['assign'] = attrs['assign'][0]
        attrs['updated_by'] = self.context['user']
        attrs['created_by'] = self.context['created_by']
        attrs['task_acronym'] = task_acronym_partial
        return attrs


class TaskDetailSerializer(serializers.ModelSerializer):
    task_acronym = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = (
            'id', 'name', 'task_acronym', 'assign', 'project', 'description', 'task_type',
            'task_status', 'task_priority', 'created_at', 'updated_at', 'created_by',
            'updated_by',)

    def get_task_acronym(self,obj):
        project_id = obj.project.id
        related_project = Project.objects.get(id=project_id)
        task_acronym_partial = related_project.acronym
        task_count = Task.objects.filter(
            project=project_id).exclude(is_deleted=True).count() + 1
        task_acronym_partial += "-" + str(task_count)
        return task_acronym_partial

class AttachmentCreateSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(
        max_length=100, allow_null=False,
        allow_blank=False,
    )
    document = serializers.ListField(
         child=serializers.FileField(allow_null=True,)
    )
    task = serializers.PrimaryKeyRelatedField(
        allow_null=True,queryset=Task.objects.all()
    )

    class Meta:
        model = Attachment
        fields = (
            'document_name', 'document', 'task'
        )

    def create(self, validated_data):
        documents = self.context['documents']
        attachments = []
        for document in documents:
            attachment = Attachment.objects.create(
                document_name=document.name,
                task=validated_data['task'],
                document=document
            )
            attachments.append(attachment)
        return attachments


class AttachmentUpdateSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(
        max_length=100, allow_null=False, allow_blank=False
    )

    class Meta:
        model = Attachment
        fields = ('document_name',)

    def update(self, instance, validated_data):
        instance.document_name = validated_data.get('document_name', instance.document_name)
        instance.save()
        return instance

class AttachmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = (
            'document_name', 'document', 'task'
        )


