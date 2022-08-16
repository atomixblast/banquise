import base64
import datetime
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.views import generic
from django.views.decorators.cache import cache_page, never_cache
from django.views.generic import UpdateView, DeleteView
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError

from .models import Article, Comment, Category, SubComment, ResetPassword
from .forms import CommentForm, ArticleForm, UserForm, CategoryForm, SubCommentForm


class IndexView(generic.ListView):
    template_name = 'blog/index.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(published=True).order_by('-pub_date')[:5]


def all_article(request):
    articles = Article.objects.filter(published=True).order_by('-pub_date')
    categories = Category.objects.all()
    return render(request, 'blog/list_article.html', context={'articles': articles, 'categories': categories})


def detail(request, slug):
    article = Article.objects.get(slug=slug)
    if request.method == "POST":
        comment = Comment(article=article)
        form = CommentForm(request.POST, instance=comment)
        form.save()
        return HttpResponseRedirect(reverse('blog:detail', args=[slug]))
    else:
        form = CommentForm
    return render(request, 'blog/detail.html', {"article": article, "form": form})


def sub_comment(request, comment_id, comment_pseudo):
    comment = get_object_or_404(Comment, pseudo=comment_pseudo, pk=comment_id)
    if request.method == "POST":
        subcomment = SubComment(comment=comment)
        form = SubCommentForm(request.POST, instance=subcomment)
        form.save()
        return HttpResponseRedirect(reverse('blog:detail', args=[comment.article.slug]))
    else:
        form = SubCommentForm
    return render(request, 'blog/sub_comment.html', {"comment": comment, "form": form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect(reverse('blog:index'))
    return HttpResponse('logout')


def send_email(request):
    subject = "Avis sur le blog"
    if request.method == 'POST':
        message = request.POST.get('message', '')
        from_email = f"mail envoyé par : {request.POST.get('from_email', '')}\n\n{message}"
        if subject and message and from_email:
            try:
                send_mail(subject, message, '', ['eustashbiantona@gmail.com', 'romaldiroma24@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return HttpResponseRedirect('/contact/thanks/')
        else:
            return HttpResponse('Make sure all fields are entered and valid.')


def sign_in(request):
    error = False
    if request.method == "POST":
        value = request.POST.dict()
        user = authenticate(username=value['username'].lower(), password=value['password'])
        if user is not None:
            login(request, user)
            next_page_url = request.POST.dict().get('next')
            next_page = next_page_url if next_page_url != 'None' else reverse('blog:dashboard')
            return HttpResponseRedirect(next_page)
        else:
            error = True
    return render(request, 'blog/sign_in.html', context={'error': error, 'next': request.GET.dict().get('next')})


def reset_password(request):
    if request.method == 'POST':
        user_email = request.POST.get('email').lower()
        all_users = [user.email.lower() for user in User.objects.all()]
        if user_email in all_users:
            add = f"{random.randint(0, 10000)}{datetime.datetime.now()}".encode('ascii')
            password = base64.b64encode(add).decode("ascii")
            html_content = render_to_string('blog/reset_mail_template.html', {'password': password})
            text_content = strip_tags(html_content)
            send_mail('Réinitialisation de mot de passe', message='', from_email='', recipient_list=[user_email], html_message=html_content)
            user = get_object_or_404(User, email=user_email)
            entrie = ResetPassword(username=user.username, resetting_password=password)
            entrie.save()
            return HttpResponseRedirect(reverse('blog:reset_password_f', args=[entrie.id, user.username]))
    return render(request, 'blog/reset_password.html')


def reset_password_f(request, user_id, user_username):
    password = get_object_or_404(ResetPassword, pk=user_id)
    if request.method == 'POST':
        resetting_password_submit = request.POST.get('reset_pass')
        new_pass = request.POST.get('new_pass')
        confirm_pass = request.POST.get('confirm_pass')
        if password.resetting_password == resetting_password_submit:
            if new_pass == confirm_pass:
                print("changement du mot de passe")
                password.delete()
                return HttpResponseRedirect(reverse('blog:sign_in'))
            else:
                print("les champs ne sont pas identiques")
        else:
            print('le mot de passe de reinitialisation ne corresponf')
    return render(request, 'blog/reset_password_f.html', context={'password': password})



@login_required()
def dashboard(request):
    messages.add_message(request, messages.SUCCESS, "Bienvenue")
    return render(request, 'blog/admin/dashboard.html')

@never_cache
@login_required()
def create_article(request):
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = user
            article.save()

            for category in form.cleaned_data.get('categories'):
                article.categories.add(category)

            return HttpResponseRedirect(reverse('blog:dashboard'))
        else:
            return JsonResponse(form.errors)
    else:
        form = ArticleForm
    return render(request, "blog/admin/create_article.html", context={'form': form})

@never_cache
@login_required()
def list_articles(request):
    articles = Article.objects.filter(author=request.user).order_by('-pub_date')
    return render(request, 'blog/admin/articles.html', context={'articles': articles})


class EditView(LoginRequiredMixin, UpdateView):
    model = Article
    template_name = 'blog/admin/article_update_form.html'
    template_name_suffix = '_update_form'
    form_class = ArticleForm
    success_url = reverse_lazy('blog:dashboard')


class ArticleDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'blog.delete_article'
    model = Article
    template_name = 'blog/admin/article_confirm_delete.html'
    success_url = reverse_lazy('blog:dashboard')


@login_required()
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(reverse('blog:dashboard'))
    else:
        form = CategoryForm
    return render(request, 'blog/admin/category.html', context={'form': form})
