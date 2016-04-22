from django.db import models

# Create your models here.


class WeiboUser(models.Model):
    user_id = models.CharField(max_length=36)
    description = models.CharField(max_length=1000, blank=True, null=True)
    fans_num = models.CharField(max_length=20, blank=True, null=True)
    screen_name = models.CharField(max_length=50, blank=True, null=True)
    statuses_count = models.CharField(max_length=20, blank=True, null=True)
    follow_num = models.CharField(max_length=20, blank=True, null=True)
    profile_image_url = models.CharField(max_length=200, blank=True, null=True)
    profile_url = models.CharField(max_length=200, blank=True, null=True)
    gender = models.CharField(max_length=4, blank=True, null=True)
    address = models.CharField(max_length=50, blank=True, null=True)
    edu_info = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)



class Blog(models.Model):
    blog_id = models.CharField(max_length=36)
    text = models.CharField(max_length=2000, blank=True, null=True)
    user_id = models.CharField(max_length=36, blank=True, null=True)
    retweet_id = models.CharField(max_length=36, blank=True, null=True)
    forward_count = models.CharField(max_length=15, blank=True, null=True)
    comment_count = models.CharField(max_length=15, blank=True, null=True)
    like_count = models.CharField(max_length=15, blank=True, null=True)
    created_timestamp = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.CharField(max_length=25)
    source = models.CharField(max_length=50, blank=True, null=True)


class Comment(models.Model):
    comment_id = models.CharField(max_length=36, blank=True, null=True)
    text = models.CharField(max_length=2000, blank=True, null=True)
    created_at = models.CharField(max_length=25, blank=True, null=True)
    like_counts = models.CharField(max_length=36, blank=True, null=True)
    user_id = models.CharField(max_length=36, blank=True, null=True)
    blog_id = models.CharField(max_length=36, blank=True, null=True)


class Fans(models.Model):
    user_id = models.CharField(max_length=36)
    follow_user_id = models.CharField(max_length=36)


class Picture(models.Model):
    pic_id = models.CharField(max_length=50, blank=True, null=True)
    pic_url = models.CharField(max_length=300, blank=True, null=True)
    blog_id = models.CharField(max_length=36, blank=True, null=True)