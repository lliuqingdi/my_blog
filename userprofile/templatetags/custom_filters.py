from django import template

register = template.Library()


@register.filter
def is_following(user_profile, target_profile):
    """检查用户是否关注了目标用户"""
    return user_profile.following.filter(id=target_profile.id).exists()