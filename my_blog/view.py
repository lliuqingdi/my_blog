# views.py
from django.contrib.auth.views import PasswordResetConfirmView


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset/password_reset_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uidb64'] = self.kwargs['uidb64']
        context['token'] = self.kwargs['token']
        return context
