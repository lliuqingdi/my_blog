from django.urls import path
# 引入views.py
from . import views
from . import api
app_name = 'article'

urlpatterns = [
    # 文章列表
    path('articles-list/', views.article_list, name='article_list'),
    # 文章详情
    path('articles-detail/<int:id>/', views.article_detail, name='article_detail'),
    # 写文章
    path('articles-create/', views.article_create, name='article_create'),
    # 删除文章
    path('articles-delete/<int:id>/', views.article_delete, name='article_delete'),
    # 安全删除文章
    path('articles-safe-delete/<int:id>/', views.article_safe_delete, name='article_safe_delete'),
    # 更新文章
    path('articles-update/<int:id>/', views.article_update, name='article_update'),
    # 点赞 +1
    path('increase-likes/<int:id>/', views.IncreaseLikesView.as_view(), name='increase_likes'),
    # 自己发的博客
    path('my-articles/', views.my_articles, name='my_articles'),
    # 列表类视图
    path('list-view/', views.ArticleListView.as_view(), name='list_view'),
    # 详情类视图
    path('detail-view/<int:pk>/', views.ArticleDetailView.as_view(), name='detail_view'),
    # 创建类视图
    path('create-view/', views.ArticleCreateView.as_view(), name='create_view'),
    path('chat/', api.ChatView.as_view(), name='ai_chat'),
]