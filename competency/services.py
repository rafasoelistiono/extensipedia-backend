from django.db import transaction
from rest_framework import serializers

from competency.models import CompetencyWinnerSlide


def reorder_winner_slides(*, items, actor=None):
    ids = [item["id"] for item in items]
    display_orders = [item["display_order"] for item in items]

    if len(ids) != len(set(ids)):
        raise serializers.ValidationError("Duplicate slide IDs are not allowed.")
    if len(display_orders) != len(set(display_orders)):
        raise serializers.ValidationError("Display order values must be unique.")
    if any(order < 1 or order > CompetencyWinnerSlide.MAX_RECORDS for order in display_orders):
        raise serializers.ValidationError(
            f"Display order must be between 1 and {CompetencyWinnerSlide.MAX_RECORDS}."
        )

    slide_map = {
        str(slide.id): slide
        for slide in CompetencyWinnerSlide.objects.filter(id__in=ids)
    }
    missing_ids = [slide_id for slide_id in ids if slide_id not in slide_map]
    if missing_ids:
        raise serializers.ValidationError("One or more winner slide IDs are invalid.")

    with transaction.atomic():
        for item in items:
            slide = slide_map[item["id"]]
            slide.display_order = item["display_order"] + 100
            if actor is not None:
                slide.updated_by = actor
                slide.save(update_fields=["display_order", "updated_by", "updated_at"])
            else:
                slide.save(update_fields=["display_order", "updated_at"])

        for item in items:
            slide = slide_map[item["id"]]
            slide.display_order = item["display_order"]
            if actor is not None:
                slide.updated_by = actor
                slide.save(update_fields=["display_order", "updated_by", "updated_at"])
            else:
                slide.save(update_fields=["display_order", "updated_at"])

    return [
        slide_map[item["id"]]
        for item in sorted(items, key=lambda entry: entry["display_order"])
    ]
