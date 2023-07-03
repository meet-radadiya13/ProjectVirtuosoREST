# Generated by Django 4.2.2 on 2023-06-28 09:28

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
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
                ('acronym',
                 models.CharField(blank=True, max_length=3, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('dead_line', models.DateField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('tags', django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(max_length=200), blank=True,
                    size=None
                    )),
                ('assign', models.ManyToManyField(
                    blank=True, to=settings.AUTH_USER_MODEL
                    )),
                ('created_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='project_created_by',
                    to=settings.AUTH_USER_MODEL
                    )),
                ('updated_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.DO_NOTHING,
                    related_name='project_updated_by',
                    to=settings.AUTH_USER_MODEL
                    )),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
