from django.contrib import admin
# из файла models импортируем модель Post
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    list_display = ("pk", "text", "pub_date", "author", "get_title_group")
    # добавляем интерфейс для поиска по тексту постов
    search_fields = ("text",)
    # добавляем возможность фильтрации по дате
    list_filter = ("pub_date",)
    empty_value_display = '-пусто-'

    def get_title_group(self, object):
        return object.group.title
    get_title_group.short_description = 'group title'


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    empty_value_display = '-пусто-'
# при регистрации модели Post источником конфигурации для неё назначаем класс PostAdmin


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
