from django.contrib import admin
from rest_framework.authtoken.models import Token

from authentication.models import Company, User
from projects.models import Project, Task, Attachment


# Register your models here.
class TokenAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(User)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Company)
admin.site.register(Attachment)
# admin.site.register(Token, TokenAdmin)
