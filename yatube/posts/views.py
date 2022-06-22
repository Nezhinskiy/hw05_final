from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post, User

POSTS_ON_PAGE = 10


def pagination(post_list, request):
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = pagination(post_list, request)
    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(
        Group.objects.prefetch_related('posts'),
        slug=slug
    )
    post_list = group.posts.all()
    page_obj = pagination(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(
        User.objects.prefetch_related('posts'),
        username=username
    )
    post_list = author.posts.all()
    page_obj = pagination(post_list, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
        context['following'] = following
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.prefetch_related('author', 'group'),
        id=post_id
    )
    comments = post.comments.all()
    form = CommentForm(
        request.POST or None
    )
    context = {
        'post': post,
        'comments': comments,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
    context = {
        'is_edit': False,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.user != post.author:
        return redirect('posts:post_detail', post.id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post.id)
    context = {
        'is_edit': True,
        'form': form
    }
    return render(request, template, context)


@login_required
def post_delete(request, post_id):
    author = get_object_or_404(
        Post.objects.prefetch_related('author'),
        pk=post_id
    ).author
    if request.user == author:
        Post.objects.get(pk=post_id).delete()
    return redirect('posts:profile', request.user.username)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id
    )
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.prefetch_related('author', 'group').filter(
        author__following__user=request.user
    )
    page_obj = pagination(post_list, request)
    context = {
        'page_obj': page_obj,
        'follow': True
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(
        User.objects.prefetch_related('posts'),
        username=username
    )
    if (
            author != request.user
            and not Follow.objects.filter(
                user=request.user,
                author=author
            ).exists()
    ):
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(
        User.objects.prefetch_related('posts'),
        username=username
    )
    if (
            author != request.user
            and Follow.objects.filter(
                user=request.user,
                author=author
            ).exists()
    ):
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
