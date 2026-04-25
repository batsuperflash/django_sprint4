from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserCreationModelForm, UserEditForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE = 10
POST_RELATED_FIELDS = ('author', 'category', 'location')


def add_post_page(queryset, request):
    paginator = Paginator(queryset, POSTS_PER_PAGE)
    return paginator.get_page(request.GET.get('page'))


def posts_with_details(queryset):
    return (
        queryset.select_related(*POST_RELATED_FIELDS)
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )


def published_posts():
    return (
        posts_with_details(Post.objects)
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    )


def author_posts(author, viewer):
    if viewer == author:
        return posts_with_details(Post.objects.filter(author=author))
    return published_posts().filter(author=author)


def post_is_visible(post, user):
    visible_to_everyone = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category is not None
        and post.category.is_published
    )
    return post.author == user or visible_to_everyone


def index(request):
    return render(
        request,
        'blog/index.html',
        {'page_obj': add_post_page(published_posts(), request)},
    )


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related(*POST_RELATED_FIELDS),
        pk=id,
    )

    if not post_is_visible(post, request.user):
        raise Http404

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'comments': post.comments.select_related('author'),
            'form': CommentForm(),
        },
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    return render(
        request,
        'blog/category.html',
        {
            'category': category,
            'page_obj': add_post_page(
                published_posts().filter(category=category),
                request,
            ),
        },
    )


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    return render(
        request,
        'blog/profile.html',
        {
            'profile': profile,
            'page_obj': add_post_page(
                author_posts(profile, request.user),
                request,
            ),
        },
    )


@login_required
def edit_profile(request):
    form = UserEditForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/user.html', {'form': form})


def registration(request):
    form = UserCreationModelForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(
        request,
        'registration/registration_form.html',
        {'form': form},
    )


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    form = PostForm(instance=post)
    if request.method == 'POST':
        username = post.author.username
        post.delete()
        return redirect('blog:profile', username=username)

    return render(request, 'blog/create.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)

    return render(
        request,
        'blog/comment.html',
        {
            'form': form,
            'comment': comment,
        },
    )


@login_required
def delete_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = get_object_or_404(Comment, pk=comment_id, post=post)
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    return render(
        request,
        'blog/comment.html',
        {
            'comment': comment,
        },
    )
