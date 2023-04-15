"""
Views for first API version.
"""

from django.http import JsonResponse
from django.db.models import Q, F
from django.db.models.functions import Coalesce
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.contrib.postgres.aggregates import ArrayAgg

from movies.models import Filmwork, PersonFilmwork


MOVIES_PER_PAGE = 50


class MoviesApiMixin:
    """Base API model for Filmwork."""

    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        return self.model.objects.prefetch_related(
            'persons', 'genres'
        ).values(
            'id', 'title', 'description', 'creation_date', 'type'
        ).annotate(
            rating=Coalesce(F('rating'), 0.0),
            genres=ArrayAgg('genres__name', distinct=True),
            actors=self.get_person_aggregation_by_role(PersonFilmwork.RoleType.Actor),
            directors=self.get_person_aggregation_by_role(PersonFilmwork.RoleType.Director),
            writers=self.get_person_aggregation_by_role(PersonFilmwork.RoleType.Writer),
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

    @staticmethod
    def get_person_aggregation_by_role(role: PersonFilmwork.RoleType):
        return ArrayAgg(
            'persons__full_name',
            filter=Q(personfilmwork__role=role),
            distinct=True
        )


class MoviesListApi(MoviesApiMixin, BaseListView):
    """List API model for Filmwork."""

    PAGINATE_BY = MOVIES_PER_PAGE

    def get_context_data(self, *args, **kwargs):
        queryset = self.object_list
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset,
            self.PAGINATE_BY
        )

        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    """Detailed API model for Filmwork."""

    def get_context_data(self, *args, **kwargs):
        pk = self.kwargs.get('pk', '')
        context = self.get_queryset().filter(id=pk)[0]
        return context
