from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator

from blog.models import Comment, Article, Category, SubComment
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']
        labels = {
            'username': "Nom d'utilisateur",
            'password': "Mot de passe",
            'email': "Email",
        }
        widgets = {
            "password": forms.PasswordInput
        }
        help_texts = {
            "username": ""
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['email', 'pseudo', 'message']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'input'}),
            'pseudo': forms.TextInput(attrs={'class': 'input'}),
            'message': forms.Textarea(attrs={'class': 'textarea', 'rows': 5}, ),
        }


class SubCommentForm(forms.ModelForm):
    class Meta:
        model = SubComment
        fields = ['email', 'pseudo', 'message']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'input'}),
            'pseudo': forms.TextInput(attrs={'class': 'input'}),
            'message': forms.Textarea(attrs={'class': 'textarea', 'rows': 5}, ),
        }


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['title', 'content', 'categories', 'photo', 'published', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'content': forms.Textarea(attrs={'class': 'textarea', 'rows': 2}),
            'categories': forms.SelectMultiple(attrs={'class': 'textarea'}),
        }
        labels = {
            'title': 'Titre de l\'article',
            'content': 'Description'
        }
        error_messages ={
            'title': {
                'unique': 'ce titre est déja utilisé'
            }
        }

    def clean_title(self):
        return self.cleaned_data.get('title').lower()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name']

    def clean_category_name(self):
        categories = [category.category_name for category in Category.objects.all()]
        field_categories = [category.strip().lower() for category in self.cleaned_data.get('category_name').split(';')]
        for field_category in field_categories:
            if field_category in categories:
                self.add_error('category_name', field_category+' existe déja dans la base de données')
            else:
                print(Category(category_name=field_category).save())
