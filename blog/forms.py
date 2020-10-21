from django import forms

from blog.models import *


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        # fields = '__all__'

class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
