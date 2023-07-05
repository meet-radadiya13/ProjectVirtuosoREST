from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from projects.models import Project
from projects.permissions import IsProjectOwner
from projects.serializers import ProjectCreationSerializer, \
    ProjectDetailSerializer, ProjectUpdateSerializer


# Create your views here.
class ProjectViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', ]
    permission_classes = (IsAuthenticated, IsProjectOwner)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', ]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreationSerializer
        elif self.action == 'partial_update':
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
        serializer = self.get_serializer(
            data=request.data, context={'user': request.user}
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectDetailSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data,
            partial=True
        )
        if serializer.is_valid():
            project = serializer.save()
            return Response(
                ProjectDetailSerializer(project).data,
                status=status.HTTP_201_CREATED
            )
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
