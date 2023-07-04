# Create your views here.
from django.db.models import Case, Count, Q, When
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from authentication.models import User
from authentication.permissions import IsCompanyOwner
from authentication.serializers import UserCreationSerializer, \
    UserDetailSerializer
from projects.models import Project
from projects.serializers import ProjectDetailSerializer


class UserViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated, IsCompanyOwner)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['company']

    def get_serializer_class(self):
        if self.action == 'create' or \
                self.action == 'partial_update':
            return UserCreationSerializer
        elif self.action == 'list' or self.action == 'retrieve':
            return UserDetailSerializer
        else:
            return UserDetailSerializer

    def get_queryset(self):
        queryset = User.objects.exclude(is_active=False)
        if self.request.user.is_owner:
            queryset = queryset.filter(company=self.request.user.company)
        else:
            queryset = queryset.none()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = UserCreationSerializer(
            data=request.data, context={'user': request.user}
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserDetailSerializer(
                    user, context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCreationSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserCreationSerializer(
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
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RenderHomeView(GenericAPIView):
    pagination_class = None

    def get(self, request, *args, **kwargs):
        total_projects = Project.objects.filter(
            Q(is_deleted=False) &
            Q(created_by__company=request.user.company)
        )
        # total_tasks = Task.objects.filter(
        #     Q(is_deleted=False) &
        #     Q(created_by__company=request.user.company)
        # )
        total_users = User.objects.filter(
            Q(is_active=True) &
            Q(company=request.user.company)
        )
        latest_projects = Project.objects.filter(
            Q(is_deleted=False) &
            Q(created_by__company=request.user.company)
        ).annotate(
            num_tasks=Count('task')
        ).order_by(
            '-num_tasks', '-created_at'
        ).annotate(
            task_high=Count(Case(When(task__task_priority='hi', then=1))),
            task_medium=Count(
                Case(When(task__task_priority='medium', then=1))
            ),
            task_low=Count(Case(When(task__task_priority='low', then=1)))
        )
        # latest_tasks = Task.objects.filter(
        #     Q(is_deleted=False) &
        #     Q(created_by__company=request.user.company)
        # ).order_by('-created_at')
        latest_users = User.objects.filter(
            Q(is_active=True) &
            Q(company=request.user.company)
        ).order_by('-date_joined')
        context = {}
        if request.user.is_owner:
            context['total_projects'] = total_projects.count()
            # context['total_tasks'] = total_tasks.count()
            context['total_users'] = total_users.count()
            context['latest_projects'] = \
                ProjectDetailSerializer(latest_projects[:5], many=True).data
            # context['latest_tasks'] = latest_tasks[:5]
            context['latest_users'] = UserDetailSerializer(
                latest_users[:5], many=True, context={'request': request}
            ).data
        else:
            context['total_projects'] = total_projects.filter(
                Q(created_by=request.user) |
                Q(assign=request.user)
            ).distinct().count()
            # context['total_tasks'] = total_tasks.filter(
            #     Q(created_by=request.user) |
            #     Q(assign=request.user)
            # ).distinct().count()
            context['total_users'] = total_users.filter(
                Q(project__created_by=request.user)
            ).count()
            context['latest_projects'] = ProjectDetailSerializer(
                latest_projects.filter(
                    Q(created_by=request.user) |
                    Q(assign=request.user)
                ).distinct()[:5], many=True
            ).data
            # context['latest_tasks'] = latest_tasks.filter(
            #     Q(created_by=request.user) |
            #     Q(assign=request.user)
            # ).distinct()[:5]
            context['latest_users'] = UserDetailSerializer(
                latest_users[:5],
                many=True, context={'request': request}
            ).data
        return Response(context, status=status.HTTP_200_OK)
