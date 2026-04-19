from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()


class DateAndTimeSplitWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d',
            ),
            forms.TimeInput(
                attrs={'type': 'time'},
                format='%H:%M',
            ),
        )
        super().__init__(attrs=attrs, date_format='%Y-%m-%d', time_format='%H:%M')
        self.widgets = list(widgets)

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if value and any(part for part in value):
            return value

        raw_value = data.get(name)
        if raw_value in (None, ''):
            return value

        if isinstance(raw_value, datetime):
            return [
                raw_value.strftime('%Y-%m-%d'),
                raw_value.strftime('%H:%M'),
            ]

        raw_value = str(raw_value).strip()
        if 'T' in raw_value:
            date_part, time_part = raw_value.split('T', 1)
            return [date_part, time_part[:5]]
        if ' ' in raw_value:
            date_part, time_part = raw_value.split(' ', 1)
            return [date_part, time_part[:5]]
        return value


class PostForm(forms.ModelForm):
    pub_date = forms.SplitDateTimeField(
        input_date_formats=('%Y-%m-%d', '%d.%m.%Y'),
        input_time_formats=('%H:%M', '%H:%M:%S'),
        widget=DateAndTimeSplitWidget(),
    )

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'pub_date',
            'category',
            'location',
            'image',
            'is_published',
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserCreationModelForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
