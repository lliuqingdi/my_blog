from django import forms
from .models import Comment
from django_ckeditor_5.widgets import CKEditor5Widget


class CommentForm(forms.ModelForm):
    """Form for comments to the article."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["body"].required = False

    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="comment"
            )
        }
