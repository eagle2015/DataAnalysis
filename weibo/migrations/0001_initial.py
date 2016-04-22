# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('blog_id', models.CharField(max_length=36)),
                ('text', models.CharField(max_length=2000, null=True, blank=True)),
                ('user_id', models.CharField(max_length=36, null=True, blank=True)),
                ('retweet_id', models.CharField(max_length=36, null=True, blank=True)),
                ('forward_count', models.CharField(max_length=15, null=True, blank=True)),
                ('comment_count', models.CharField(max_length=15, null=True, blank=True)),
                ('like_count', models.CharField(max_length=15, null=True, blank=True)),
                ('created_timestamp', models.CharField(max_length=25, null=True, blank=True)),
                ('created_at', models.CharField(max_length=25)),
                ('source', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('comment_id', models.CharField(max_length=36, null=True, blank=True)),
                ('text', models.CharField(max_length=300, null=True, blank=True)),
                ('created_at', models.CharField(max_length=25, null=True, blank=True)),
                ('like_counts', models.CharField(max_length=36, null=True, blank=True)),
                ('user_id', models.CharField(max_length=36, null=True, blank=True)),
                ('blog_id', models.CharField(max_length=36, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fans',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('user_id', models.CharField(max_length=36)),
                ('follow_user_id', models.CharField(max_length=36)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('pic_id', models.CharField(max_length=50, null=True, blank=True)),
                ('pic_url', models.CharField(max_length=300, null=True, blank=True)),
                ('blog_id', models.CharField(max_length=36, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WeiboUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('user_id', models.CharField(max_length=36)),
                ('description', models.CharField(max_length=1000, null=True, blank=True)),
                ('fans_num', models.CharField(max_length=20, null=True, blank=True)),
                ('screen_name', models.CharField(max_length=50, null=True, blank=True)),
                ('statuses_count', models.CharField(max_length=20, null=True, blank=True)),
                ('follow_num', models.CharField(max_length=20, null=True, blank=True)),
                ('profile_image_url', models.CharField(max_length=200, null=True, blank=True)),
                ('profile_url', models.CharField(max_length=200, null=True, blank=True)),
                ('gender', models.CharField(max_length=4, null=True, blank=True)),
                ('address', models.CharField(max_length=50, null=True, blank=True)),
                ('edu_info', models.CharField(max_length=100, null=True, blank=True)),
                ('email', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
