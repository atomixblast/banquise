from django.urls import path
from . import views

from django.conf.urls.static import static
from django.conf import settings



app_name = "blog"
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('tous les articles/', views.all_article, name="all_articles"),
    path('read/<str:slug>/', views.detail, name="detail"),
    path('sub_comment/<str:comment_id>/<str:comment_pseudo>', views.sub_comment, name='sub_comment'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/create', views.create_article, name="create_article"),
    path('dashboard/add_category', views.add_category, name="add_category"),
    path('dashboard/articles', views.list_articles, name="list_article"),
    path('dashboard/edit/<int:article_id>/<str:slug>', views.EditView.as_view(), name="edit_article"),
    path('dashboard/delete/<int:pk>/', views.ArticleDeleteView.as_view(), name="delete_article"),
    path('mail/send/', views.send_email, name='mail_send'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('reset_password/<int:user_id>/<str:user_username>', views.reset_password_f, name='reset_password_f'),
]
