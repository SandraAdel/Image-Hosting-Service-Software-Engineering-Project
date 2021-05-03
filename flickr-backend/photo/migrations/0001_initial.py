# Generated by Django 3.0.5 on 2021-05-08 06:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import photo.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('media_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('secret', models.CharField(blank=True, max_length=100)),
                ('original_secret', models.CharField(blank=True, max_length=100)),
                ('server', models.PositiveSmallIntegerField(blank=True)),
                ('farm', models.PositiveSmallIntegerField(blank=True)),
                ('original_format', models.CharField(blank=True, max_length=5)),
                ('title', models.CharField(blank=True, max_length=300)),
                ('description', models.TextField(blank=True, max_length=2000)),
                ('is_public', models.BooleanField(default=True)),
                ('is_friend', models.BooleanField(default=False)),
                ('is_family', models.BooleanField(default=False)),
                ('is_favourite', models.BooleanField(default=False)),
                ('can_comment', models.PositiveSmallIntegerField(default=3)),
                ('can_addmeta', models.PositiveSmallIntegerField(default=3)),
                ('date_posted', models.DateTimeField(blank=True)),
                ('date_taken', models.DateTimeField(blank=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('views', models.PositiveIntegerField(default=0)),
                ('comments', models.PositiveIntegerField(default=0)),
                ('favourites', models.PositiveIntegerField(default=0)),
                ('count_tags', models.PositiveIntegerField(default=0)),
                ('has_people', models.BooleanField(default=False)),
                ('count_people_tagged', models.PositiveIntegerField(default=0)),
                ('media', models.CharField(choices=[('Photo', 'Photo'), ('Video', 'Video')], max_length=10)),
                ('media_file', models.FileField(upload_to=photo.models.media_upload)),
                ('file_size', models.PositiveIntegerField(blank=True)),
                ('photo_height', models.PositiveSmallIntegerField(blank=True)),
                ('photo_width', models.PositiveSmallIntegerField(blank=True)),
                ('photo_displaypx', models.PositiveSmallIntegerField()),
                ('video_duration', models.PositiveSmallIntegerField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_photos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='View',
            fields=[
                ('view_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('view_date', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo_views', to='photo.Photo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_views', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tagging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_contact', models.BooleanField(default=False)),
                ('is_friend', models.BooleanField(default=False)),
                ('is_family', models.BooleanField(default=False)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagging_people_actions', to=settings.AUTH_USER_MODEL)),
                ('person_tagged', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='photo.Photo')),
            ],
        ),
        migrations.AddField(
            model_name='photo',
            name='people_tagged',
            field=models.ManyToManyField(related_name='photos_tagged_in', through='photo.Tagging', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('note_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('left_coord', models.PositiveSmallIntegerField()),
                ('top_coord', models.PositiveSmallIntegerField()),
                ('note_width', models.PositiveSmallIntegerField()),
                ('note_height', models.PositiveSmallIntegerField()),
                ('note_text', models.TextField(max_length=1000)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_notes', to=settings.AUTH_USER_MODEL)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo_notes', to='photo.Photo')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now=True)),
                ('comment_text', models.TextField(max_length=1000)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_comments', to=settings.AUTH_USER_MODEL)),
                ('photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo_comments', to='photo.Photo')),
            ],
        ),
    ]