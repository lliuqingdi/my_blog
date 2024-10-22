from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image


class ArticleColumn(models.Model):
    """
    文章栏目的 Model
    """
    title = models.CharField(max_length=100, blank=True, verbose_name="栏目标题")
    created = models.DateTimeField(default=timezone.now, verbose_name="创建时间")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = '文章栏目'


class ArticlePost(models.Model):
    """
    文章的 Model
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="文章作者")
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True, verbose_name="文章标题图")
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article',
        verbose_name="文章栏目"
    )
    tags = TaggableManager(blank=True, verbose_name="文章标签")
    title = models.CharField(max_length=100, verbose_name="文章标题")
    body = models.TextField(verbose_name="文章正文")
    total_views = models.PositiveIntegerField(default=0, verbose_name="浏览量")
    likes = models.PositiveIntegerField(default=0, verbose_name="文章点赞数")
    created = models.DateTimeField(default=timezone.now, verbose_name="文章创建时间")
    updated = models.DateTimeField(auto_now=True, verbose_name="文章更新时间")

    class Meta:
        db_table = 'article_post'
        verbose_name_plural = "文章"
        ordering = ('-created',)

    def __str__(self):
        # 将文章标题返回
        return self.title

    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    def save(self, *args, **kwargs):
        # 保存文章实例
        article = super(ArticlePost, self).save(*args, **kwargs)

        # 如果存在 avatar（文章标题图）并且不是在更新字段时
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size  # 获取当前图像尺寸
            new_x = 400  # 设置新图像的宽度
            new_y = int(new_x * (y / x))  # 按比例计算新图像的高度
            resized_image = image.resize((new_x, new_y), Image.Resampling.LANCZOS)  # 使用 LANCZOS 重采样
            resized_image.save(self.avatar.path)  # 保存调整大小后的图像

        return article

    def was_created_recently(self):
        diff = timezone.now() - self.created
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(ArticlePost, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')