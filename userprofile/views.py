from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserLoginForm, UserRegisterForm
from .forms import ProfileForm
from .models import Profile
from django.contrib import messages
from article.models import ArticlePost
from django.db.models import Q


# 用户登录
def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户数据保存在 session 中，即实现了登录动作
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码输入有误。请重新输入~")
        else:
            return HttpResponse("账号或密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = { 'form': user_login_form }
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


# 用户退出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 用户注册
def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save()
            # 保存好数据后立即登录并返回博客列表页面
            login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("article:article_list")
        else:
            # 使用默认的表单的check函数不仅会检查密码是否相同，还会检查密码复杂程度，以及是否与其他信息相关等等
            # print(user_register_form.errors)
            return HttpResponse("注册表单输入有误。请再次检查输入密码是否符合标准，并重新输入~")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = {'form': user_register_form}
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


# 用户删除
# 验证用户是否登录的装饰器
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户、待删除用户是否相同
        if request.user == user:
            #退出登录，删除数据并返回博客列表
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作的权限。")
    else:
        return HttpResponse("仅接受post请求。")


# 编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)

    # 旧教程代码
    # profile = Profile.objects.get(user_id=id)
    # 新教程代码： 获取 Profile
    if Profile.objects.filter(user_id=id).exists():
        # user_id 是 OneToOneField 自动生成的字段
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)


    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")

        # 上传的文件保存在 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data

            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            # 如果 request.FILES 存在文件，则保存
            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]

            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = { 'profile_form': profile_form, 'profile': profile, 'user': user }
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


@login_required
def toggle_follow(request, user_id):
    """切换关注状态"""
    target_profile = get_object_or_404(Profile, user_id=user_id)
    current_profile = request.user.profile

    if target_profile == current_profile:
        return JsonResponse({'status': 'error', 'message': '不能关注自己！'}, status=400)

    is_following = current_profile.following.filter(id=target_profile.id).exists()

    if is_following:
        current_profile.following.remove(target_profile)
        status = 'unfollowed'
    else:
        current_profile.following.add(target_profile)
        status = 'followed'

    return JsonResponse({
        'status': status,
        'message': f'已{"取消" if is_following else ""}关注 {target_profile.user.username}',
        'new_state': '已关注' if not is_following else '关注'
    })


def user_profile(request, username):
    # 获取用户对象
    profile_user = get_object_or_404(User, username=username)

    # 获取用户的文章
    articles = ArticlePost.objects.filter(author=profile_user)

    # 搜索和排序
    search = request.GET.get('search', '')
    if search:
        articles = articles.filter(Q(title__icontains=search) | Q(body__icontains=search))

    order = request.GET.get('order', 'created')
    if order == 'total_views':
        articles = articles.order_by('-total_views')
    else:
        articles = articles.order_by('-created')

    # 获取粉丝和关注数量
    followers_count = profile_user.profile.followers.count()
    following_count = profile_user.profile.following.count()

    # 判断当前用户是否已关注
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        # 判断当前登录用户是否已关注该用户
        is_following = profile_user.profile.followers.filter(id=request.user.profile.id).exists()

    context = {
        'profile_user': profile_user,
        'articles': articles,
        'is_following': is_following,
        'search': search,
        'order': order,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'userprofile/profile.html', context)