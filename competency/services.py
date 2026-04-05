from django.db import connections, router, transaction

from competency.models import CompetencyWinnerSlide


def get_default_winner_slide_alt_text(slot_number):
    return f"Winner slide slot {slot_number}"


def get_winner_slide_slot_numbers():
    return range(1, CompetencyWinnerSlide.MAX_RECORDS + 1)


def winner_slide_table_exists(using=None):
    alias = using or router.db_for_read(CompetencyWinnerSlide)
    connection = connections[alias]
    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
    return CompetencyWinnerSlide._meta.db_table in table_names


def build_empty_winner_slide(slot_number):
    return CompetencyWinnerSlide(
        display_order=slot_number,
        alt_text=get_default_winner_slide_alt_text(slot_number),
    )


def ensure_winner_slide_slots(using=None):
    alias = using or router.db_for_write(CompetencyWinnerSlide)
    if not winner_slide_table_exists(using=alias):
        return []

    valid_slots = list(get_winner_slide_slot_numbers())
    slides = []

    with transaction.atomic(using=alias):
        (
            CompetencyWinnerSlide.objects.using(alias)
            .exclude(display_order__in=valid_slots)
            .delete()
        )

        for slot_number in valid_slots:
            existing = list(
                CompetencyWinnerSlide.objects.using(alias)
                .filter(display_order=slot_number)
                .order_by("created_at", "pk")
            )
            slide = existing[0] if existing else None

            if len(existing) > 1:
                CompetencyWinnerSlide.objects.using(alias).filter(
                    pk__in=[item.pk for item in existing[1:]]
                ).delete()

            if slide is None:
                slide = CompetencyWinnerSlide.objects.using(alias).create(
                    display_order=slot_number,
                    alt_text=get_default_winner_slide_alt_text(slot_number),
                )
            elif not slide.alt_text:
                slide.alt_text = get_default_winner_slide_alt_text(slot_number)
                slide.save()

            slides.append(slide)

    return slides


def get_winner_slide_slot_instance(slot_number, using=None):
    alias = using or router.db_for_read(CompetencyWinnerSlide)
    if not winner_slide_table_exists(using=alias):
        return build_empty_winner_slide(slot_number)

    instance = CompetencyWinnerSlide.objects.using(alias).filter(display_order=slot_number).first()
    return instance or build_empty_winner_slide(slot_number)


def build_winner_slide_slots(using=None):
    alias = using or router.db_for_read(CompetencyWinnerSlide)
    item_map = {}

    if winner_slide_table_exists(using=alias):
        item_map = {
            item.display_order: item
            for item in CompetencyWinnerSlide.objects.using(alias).order_by("display_order", "-updated_at")
        }

    return [
        {
            "number": slot_number,
            "item": item_map.get(slot_number) or build_empty_winner_slide(slot_number),
        }
        for slot_number in get_winner_slide_slot_numbers()
    ]
