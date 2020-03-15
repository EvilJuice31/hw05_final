from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10) # показывать по 10 записей на странице.

    page_number = request.GET.get('page') # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number) # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    # функция get_object_or_404 позволяет получить объект из базы данных
    # по заданным критериям или вернуть сообщение об ошибке если объект не найден
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям. Это аналог добавления
    # условия WHERE group_id = {group_id}
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'paginator': paginator, 'group': group})


@login_required(login_url='/auth/login/')
def new_post(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = user
            new_post.save()
            return redirect('index')
    else:
        form = PostForm()
    return render(request, 'new_post.html', {'form': form})

def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=profile).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if Follow.objects.filter(user= request.user, author=profile).exists():
        following = True
    else:
        following = False
    count = Post.objects.filter(author=profile).count()
    follower = Follow.objects.filter(author=profile).count()
    followers = Follow.objects.filter(user=profile).count()
    form = CommentForm() 
    #comment = Comment.objects.filter(post = post).all()
    return render(request, "profile.html", {'form':form,
                                            'profile': profile,
                                            'page': page,
                                            'paginator': paginator,
                                            'count': count,
                                            'follower': follower,
                                            'followers': followers,
                                            'following': following})

def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    count = Post.objects.filter(author=profile).count()
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post = post).order_by("-created")
    form = CommentForm()
    return render(request, "post.html", {'post': post, 'profile': profile, 'count': count, 'comments': comments, 'form':form})

def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.filter(post = post).all()
    if request.user != post.author:
        return redirect(f'/{username}/{post_id}/')
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            post = form.save(commit=True)
            post.save()
            return redirect(f'/{username}/{post_id}/')
    else:
        form = PostForm(instance=post)
    return render(request, 'new_post.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию, 
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required(login_url='/auth/login/')
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment = Comment.objects.filter(post = post).all()
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                comment.author = request.user
                comment = form.save(commit=False)
                comment.post = post
                comment.save()
                return redirect('post', username=post.author.username, post_id=post_id)
        else:
            form = CommentForm()
        return redirect('post', username=post.author.username, post_id=post_id,)
    

@login_required
def follow_index(request):
    #follow = Follow.objects.get(user=request.user) #Кто
    favorite_list = Follow.objects.select_related('author', 'user').filter(user=request.user)
    author_list = [favorite.author for favorite in favorite_list]
    post_list = Post.objects.filter(author__in=author_list).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page, 'paginator': paginator})

@login_required
def profile_follow(request, username):
    foolow = get_object_or_404(User, username=username)
    if foolow != request.user:
        if Follow.objects.filter(user= request.user, author=foolow).exists():
            return redirect('profile',username=username)
        else:
            Follow.objects.create(user=request.user, author=foolow)
    return redirect('profile',username=username)

@login_required
def profile_unfollow(request, username):
    foolow = get_object_or_404(User, username=username)
    if foolow != request.user:
        if Follow.objects.filter(user= request.user, author=foolow).exists():
            Follow.objects.filter(user=request.user, author=foolow).delete()
    return redirect('profile',username=username)
