import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedMixin(models.Model):

    updated_at = models.DateTimeField(_('modified'), auto_now=True)
    created_at = models.DateTimeField(_('created'), auto_now_add=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(TimeStampedMixin, UUIDMixin):

    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = _('Genre')
        verbose_name_plural = _('Genres')


class Person(TimeStampedMixin, UUIDMixin):

    full_name = models.CharField(_('full_name'), max_length=255)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "content\".\"person"
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')


class Filmwork(TimeStampedMixin, UUIDMixin):

    class FilmType(models.TextChoices):
        Movie = 'movie', _('Movie')
        TV_SHOW = 'tv_show', _('TV Show')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField(_('creation_date'), null=True)
    rating = models.FloatField(_('rating'), blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    type = models.CharField(_('type'), max_length=7, choices=FilmType.choices, default=FilmType.Movie)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')
    file_path = models.CharField(_('file_path'), max_length=255, blank=True, null=True, default='')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = _('Filmwork')
        verbose_name_plural = _('Filmworks')
        indexes = [
            models.Index(fields=['creation_date', 'rating'], name='creation_date_rating_idx'),
            models.Index(fields=['title'], name='title_idx')
        ]


class GenreFilmwork(UUIDMixin):

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "content\".\"genre_film_work"
        indexes = [
            models.Index(fields=['film_work_id', 'genre_id'], name='film_work_genre_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['film_work_id', 'genre_id'], name='film_work_genre_uniq')
        ]


class PersonFilmwork(UUIDMixin):

    class RoleType(models.TextChoices):
        Actor = 'actor', _('Actor')
        Writer = 'writer', _('Writer')
        Director = 'director', _('Director')

    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.TextField(_('role'), choices=RoleType.choices, default=RoleType.Actor)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "content\".\"person_film_work"
        indexes = [
            models.Index(fields=['film_work', 'person', 'role'], name='film_work_person_role_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='film_work_person_role_uniq')
        ]
