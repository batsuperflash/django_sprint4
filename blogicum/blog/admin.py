"""Admin configuration placeholder for blog app."""
from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.db import models as db_models

from .models import Category, Location, Post, Comment

User = get_user_model()


class GroupAdminForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        label='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438',
        widget=admin.widgets.FilteredSelectMultiple(
            verbose_name='\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438',
            is_stacked=False,
        ),
    )

    class Meta:
        model = Group
        fields = ('name', 'permissions', 'users')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.user_set.all()

    def save(self, commit=True):
        group = super().save(commit=commit)
        if group.pk:
            group.user_set.set(self.cleaned_data['users'])
        return group


try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    form = GroupAdminForm
    filter_horizontal = ('permissions',)
    fieldsets = (
        (None, {'fields': ('name', 'permissions', 'users')}),
    )


admin.site.register(Category)
admin.site.register(Location)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'pub_date', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('category',)
    search_fields = ('title', 'text')
    formfield_overrides = {
        db_models.DateTimeField: {'widget': AdminSplitDateTime},
    }


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('text',)