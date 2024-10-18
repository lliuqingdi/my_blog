from django.shortcuts import render, redirect

from django.views import View
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from article.models import ArticlePost


class CommentNoticeListView(LoginRequiredMixin, ListView):
    """通知列表"""
    # 上下文的名称
    context_object_name = 'notices'
    # 模板位置
    template_name = 'notice/list.html'
    # 登录重定向
    login_url = '/userprofile/login/'

    # 未读通知的查询集
    def get_queryset(self):
        return self.request.user.notifications.unread()


class CommentNoticeUpdateView(View):
    """更新通知状态"""
    def get(self, request):
        # 获取未读消息
        notice_id = request.GET.get('notice_id')
        article_id = request.GET.get('article_id')
        # print(notice_id, article_id)
        # 确保 notice_id 和 article_id 是有效的数字
        if notice_id and notice_id.isdigit() and article_id and article_id.isdigit():
            try:
                article = ArticlePost.objects.get(id=article_id)
                request.user.notifications.get(id=notice_id).mark_as_read()
                return redirect(article)
            except ArticlePost.DoesNotExist:
                return redirect('notice:list')  # 文章不存在时重定向到通知列表
        else:
            # 更新全部通知为已读
            request.user.notifications.mark_all_as_read()
            return redirect('notice:list')
