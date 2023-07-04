# Generated by Django 4.2.2 on 2023-07-04 06:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID'
                    )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('name',
                 models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('task_acronym',
                 models.CharField(blank=True, max_length=100, null=True)),
                ('task_type', models.CharField(
                    choices=[('task', 'Task'), ('bug', 'Bug')], default='task'
                    )),
                ('task_status', models.CharField(
                    choices=[('todo', 'TODO'), ('in_progress', 'In Progress'),
                             ('completed', 'Completed')], default='todo'
                    )),
                ('task_priority', models.CharField(
                    choices=[('hi', 'High'), ('medium', 'Medium'),
                             ('low', 'Low')], default='medium'
                    )),
                ('assign', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    to=settings.AUTH_USER_MODEL
                    )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='task_created_by', to=settings.AUTH_USER_MODEL
                    )),
                ('project', models.ForeignKey(
                    null=True, on_delete=django.db.models.deletion.SET_NULL,
                    to='projects.project'
                    )),
                ('updated_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='task_updated_by', to=settings.AUTH_USER_MODEL
                    )),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuditHistory',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID'
                    )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('action', models.TextField(blank=True, null=True)),
                ('action_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='action_by', to=settings.AUTH_USER_MODEL
                    )),
                ('project', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    to='projects.project'
                    )),
                ('task', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    to='projects.task'
                    )),
                ('user_from', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='user_form', to=settings.AUTH_USER_MODEL
                    )),
                ('user_to', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='user_to', to=settings.AUTH_USER_MODEL
                    )),
            ],
            options={
                'db_table': 'audit_history',
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID'
                    )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('document_name',
                 models.CharField(blank=True, max_length=100, null=True)),
                ('document', models.FileField(
                    blank=True, null=True, upload_to='attachments/'
                    )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='attachment_created_by',
                    to=settings.AUTH_USER_MODEL
                    )),
                ('task', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='tasks_attachments', to='projects.task'
                    )),
                ('updated_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='attachment_updated_by',
                    to=settings.AUTH_USER_MODEL
                    )),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
