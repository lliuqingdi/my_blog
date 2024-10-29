"""
URL configuration for my_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
import notifications.urls
from article.views import article_list
from django.contrib.auth import views as auth_views
from .view import CustomPasswordResetConfirmView
urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', article_list, name='home'),
                  path('article/', include('article.urls', namespace='article')),
                  path('userprofile/', include('userprofile.urls', namespace='userprofile')),
                  path('comment/', include('comment.urls', namespace='comment')),
                  path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
                  path('notice/', include('notice.urls', namespace='notice')),
                  path('accounts/', include('allauth.urls')),
                  path('password-reset/',
                       auth_views.PasswordResetView.as_view(template_name='password_reset/password_reset_form.html',
                       email_template_name='password_reset/password_reset_email.html',
                       subject_template_name='password_reset/password_reset_subject.txt',),
                       name='password_reset'),
                  path('password-reset/done/',
                       auth_views.PasswordResetDoneView.as_view(
                           template_name='password_reset/password_reset_done.html'),
                       name='password_reset_done'),
                  path('password-reset-confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
                       name='password_reset_confirm'),
                  path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
                      template_name='password_reset/password_reset_complete.html'),
                       name='password_reset_complete'),
                  path('ckeditor5/', include('django_ckeditor_5.urls')),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += [
    path('i18n/', include('django.conf.urls.i18n')),
]
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
