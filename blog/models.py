import datetime
import base64
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    category_name = models.CharField(
        max_length=150,
        unique=True,
        error_messages={
            'unique': "Cette catégorie exists déja.",
        },
    )

    def __str__(self):
        return self.category_name


class ResetPassword(models.Model):
    username = models.CharField(max_length=200)
    resetting_password = models.CharField(max_length=255)


class Article(models.Model):
    title = models.CharField(max_length=200, unique=True)
    content = models.TextField()
    body = RichTextUploadingField(blank=True, null=True)
    slug = models.CharField(max_length=254, blank=True, unique=True)
    pub_date = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(null=True, blank=True)
    published = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    categories = models.ManyToManyField(Category)

    def save(self, *args, **kwargs):
        self.title = self.title.lower()
        self.slug = slugify(self.title)
        self.update_date = timezone.now()
        if not self.pub_date:
            self.pub_date = timezone.now()
        if self.published and not self.pub_date:
            self.pub_date = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    message = models.TextField()
    comment_date = models.DateField(blank=True, auto_now_add=True)
    pseudo = models.CharField(max_length=200)
    email = models.EmailField()
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.message


class SubComment(models.Model):
    message = models.TextField()
    comment_date = models.DateField(blank=True, auto_now_add=True)
    pseudo = models.CharField(max_length=200)
    email = models.EmailField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)