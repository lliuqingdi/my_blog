from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .forms import CommentForm
from article.models import ArticlePost
from .models import Comment
from notifications.signals import notify

from django.contrib.auth.models import User


# 文章评论
@login_required(login_url='/userprofile/login/')
def post_comment(request, article_id, parent_comment_id=None):
    article = get_object_or_404(ArticlePost, id=article_id)

    # 处理 POST 请求
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.article = article
            new_comment.user = request.user
            # print(parent_comment_id, article.id)
            # 二级或多级回复
            if parent_comment_id:

                parent_comment = Comment.objects.get(id=parent_comment_id)
                # 若回复层级超过二级，则转换为二级回复
                new_comment.parent = parent_comment
                # 被回复人
                new_comment.reply_to = parent_comment.user
                new_comment.save()

                # 给被回复的用户发送通知
                if not parent_comment.user.is_superuser and parent_comment.user != request.user:
                    notify.send(
                        request.user,
                        recipient=parent_comment.user,
                        verb='回复了你',
                        target=article,
                        action_object=new_comment,
                    )

                redirect_url = article.get_absolute_url() + '#comment_elem_' + str(new_comment.id)
                return redirect(redirect_url)

            # 普通评论（非回复）
            new_comment.save()

            # 给管理员发送通知
            if not request.user.is_superuser:
                notify.send(
                    request.user,
                    recipient=User.objects.filter(is_superuser=True),
                    verb='回复了你',
                    target=article,
                    action_object=new_comment,
                )

            # 添加锚点，跳转到新评论的位置
            redirect_url = article.get_absolute_url() + '#comment_elem_' + str(new_comment.id)
            return redirect(redirect_url)
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 处理 GET 请求
    elif request.method == 'GET':
        # print(parent_comment_id, article.id)
        comment_form = CommentForm()
        context = {
            'comment_form': comment_form,
            'article_id': article_id,
            'parent_comment_id': parent_comment_id
        }
        return render(request, 'comment/reply.html', context)

    # 处理其他请求
    else:
        return HttpResponse("仅接受GET/POST请求。")
