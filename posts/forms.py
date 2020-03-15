from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        # эта форма будет хранить данные в модели Post
        model = Post
        # на странице формы будут отображаться поля 'group' и 'text'
        fields = ['group', 'text', 'image']


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']