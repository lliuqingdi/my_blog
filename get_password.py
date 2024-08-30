import string
import secrets


def generate_password(length=12):
    # 定义只包含英文字母和数字的字符集
    alphabet = string.ascii_letters + string.digits

    # 使用secrets模块生成随机密码
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# 生成一个长度为12的随机密码，只包含英文字母和数字

random_password = generate_password()
print(f"随机生成的密码: {random_password}")