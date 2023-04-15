from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Genre, Filmwork, GenreFilmwork, PersonFilmwork, Person


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    autocomplete_fields = ('person',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'id')


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline,)
    list_display = ('title', 'type', 'get_genres', 'creation_date', 'rating', 'created_at', 'updated_at')
    list_filter = ('type', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'id')
    list_prefetch_related = ('genres',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(*self.list_prefetch_related)

    def get_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = _('Genres')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmworkInline,)
    search_fields = ('full_name', 'id', 'created_at', 'updated_at')
