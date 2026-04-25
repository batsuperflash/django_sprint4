from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, Post

User = get_user_model()
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'


def split_raw_datetime(value):
    value = str(value).strip()
    separator = 'T' if 'T' in value else ' '
    if separator not in value:
        return None
    date_part, time_part = value.split(separator, 1)
    return [date_part, time_part[:5]]


class DateAndTimeSplitWidget(forms.SplitDateTimeWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.DateInput(
                attrs={'type': 'date'},
                format=DATE_FORMAT,
            ),
            forms.TimeInput(
                attrs={'type': 'time'},
                format=TIME_FORMAT,
            ),
        )
        super().__init__(
            attrs=attrs,
            date_format=DATE_FORMAT,
            time_format=TIME_FORMAT,
        )
        self.widgets = list(widgets)

    def value_from_datadict(self, data, files, name):
        widget_value = super().value_from_datadict(data, files, name)
        if widget_value and any(part for part in widget_value):
            return widget_value

        raw_value = data.get(name)
        if raw_value in (None, ''):
            return widget_value

        if isinstance(raw_value, datetime):
            return [
                raw_value.strftime(DATE_FORMAT),
                raw_value.strftime(TIME_FORMAT),
            ]

        return split_raw_datetime(raw_value) or widget_value


class PostForm(forms.ModelForm):
    pub_date = forms.SplitDateTimeField(
        input_date_formats=(DATE_FORMAT, '%d.%m.%Y'),
        input_time_formats=(TIME_FORMAT, '%H:%M:%S'),
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
