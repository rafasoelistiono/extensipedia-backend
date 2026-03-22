from competency.models import AgendaCard, CompetencyProgram


BOOLEAN_QUERY_VALUES = {
    "true": True,
    "1": True,
    "false": False,
    "0": False,
}


def parse_boolean_query_param(value):
    if value is None:
        return None
    return BOOLEAN_QUERY_VALUES.get(str(value).strip().lower())


def get_public_competency_programs():
    return CompetencyProgram.objects.filter(is_published=True).select_related("created_by", "updated_by")


def get_admin_competency_programs():
    return CompetencyProgram.objects.select_related("created_by", "updated_by").all()


def get_public_agenda_cards(filters=None):
    queryset = AgendaCard.objects.filter(is_active=True).select_related("created_by", "updated_by").all()
    filters = filters or {}

    boolean_filter_map = {
        "urgency_tag": "urgency_tag",
        "recommendation_tag": "recommendation_tag",
    }
    text_filter_map = {
        "category_tag": "category_tag__iexact",
        "scope_tag": "scope_tag__iexact",
        "pricing_tag": "pricing_tag__iexact",
    }

    for query_param, lookup in boolean_filter_map.items():
        parsed_value = parse_boolean_query_param(filters.get(query_param))
        if parsed_value is not None:
            queryset = queryset.filter(**{lookup: parsed_value})

    for query_param, lookup in text_filter_map.items():
        value = filters.get(query_param)
        if value:
            queryset = queryset.filter(**{lookup: value})

    return queryset.order_by("-created_at", "-updated_at", "deadline_date", "title")


def get_admin_agenda_cards():
    return AgendaCard.objects.select_related("created_by", "updated_by").all()
