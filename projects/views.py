from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.utils.encoding import force_str

from projects.models import Project, Task, Attachment
from projects.serializers import ProjectCreationSerializer, \
    ProjectDetailSerializer, ProjectUpdateSerializer, TaskCreationSerializer, \
    TaskDetailSerializer, TaskUpdateSerializer, AttachmentCreateSerializer,\
    AttachmentDetailSerializer, AttachmentUpdateSerializer


# Create your views here.
class ProjectViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', ]

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreationSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProjectUpdateSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return ProjectDetailSerializer
        else:
            return ProjectDetailSerializer

    def get_queryset(self):
        queryset = Project.objects.filter(
            created_by__company=self.request.user.company
        ).exclude(is_deleted=True)
        if not self.request.user.is_owner:
            queryset = queryset.filter(
                Q(created_by=self.request.user) | Q(
                    assign=self.request.user
                )
            )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = ProjectCreationSerializer(
            data=request.data, context={'user': request.user}
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectDetailSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectUpdateSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProjectUpdateSerializer(
            instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def count_projects(self, request, *args, **kwargs):
        return Response({'count': Project.objects.count()})

class TaskViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', ]

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreationSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return TaskUpdateSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return TaskDetailSerializer
        else:
            return TaskDetailSerializer

    def get_queryset(self):
        queryset = Task.objects.filter(
            created_by__company=self.request.user.company
        ).exclude(is_deleted=True)
        if not self.request.user.is_owner:
            queryset = queryset.filter(
                Q(created_by=self.request.user) | Q(
                    assign=self.request.user
                )
            )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = TaskCreationSerializer(
            data=request.data, context={'user': request.user}
        )
        if serializer.is_valid():
            task = serializer.save()
            return Response(
                TaskDetailSerializer(task).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TaskUpdateSerializer(
            instance, data=request.data, partial=True, context={'user': request.user,
                                                                'created_by': instance.created_by,
                                                                'project':instance.project}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def count_tasks(self, request, *args, **kwargs):
        return Response({'count': Task.objects.count()})


class AttachmentViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['task', ]
    http_method_names = ['post','patch','delete','get',]

    def get_serializer_class(self):
        if self.action == 'create':
            return AttachmentCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return AttachmentUpdateSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return AttachmentDetailSerializer
        else:
            return AttachmentDetailSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task')
        if task_id:
            queryset = Attachment.objects.filter(task=task_id,is_deleted=False)
        else:
            queryset = Attachment.objects.exclude(is_deleted=True)
        return queryset

    def create(self, request, *args, **kwargs):
        documents = request.FILES.getlist('document', None)

        serializer = self.get_serializer(
            data=request.data,context={'documents': documents}
        )
        if serializer.is_valid():
            serializer.save()
            filenames = [force_str(document) for document in documents]
            return Response(
                {
                'documents': filenames,
                'status':status.HTTP_201_CREATED
                 }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = AttachmentUpdateSerializer(
            instance, data=request.data, partial=True, context={'user': request.user, }
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


