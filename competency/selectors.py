from competency.models import AgendaCard, CompetencyProgram


def get_public_competency_programs():
    return CompetencyProgram.objects.filter(is_published=True).select_related("created_by", "updated_by")


def get_admin_competency_programs():
    return CompetencyProgram.objects.select_related("created_by", "updated_by").all()


def get_public_agenda_cards(filters=None):
    queryset = AgendaCard.objects.filter(is_active=True).select_related("created_by", "updated_by").all()
    filters = filters or {}

    filter_map = {
        "urgency_tag": "urgency_tag__iexact",
        "recommendation_tag": "recommendation_tag__iexact",
        "category_tag": "category_tag__iexact",
        "scope_tag": "scope_tag__iexact",
        "pricing_tag": "pricing_tag__iexact",
    }

    for query_param, lookup in filter_map.items():
        value = filters.get(query_param)
        if value:
            queryset = queryset.filter(**{lookup: value})

    return queryset.order_by("sort_order", "deadline_date", "title")


def get_admin_agenda_cards():
    return AgendaCard.objects.select_related("created_by", "updated_by").all()
