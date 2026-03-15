from aspirations.models import AspirationSubmission


def get_admin_aspiration_submissions():
    return AspirationSubmission.objects.select_related("created_by", "updated_by").all()


def get_featured_aspirations(visibility=None):
    queryset = AspirationSubmission.objects.filter(
        is_featured=True,
        status__in=[AspirationSubmission.Status.INVESTIGATING, AspirationSubmission.Status.RESOLVED],
    ).select_related("created_by", "updated_by")

    if visibility in {AspirationSubmission.Visibility.PUBLIC, AspirationSubmission.Visibility.ANONYMOUS}:
        queryset = queryset.filter(visibility=visibility)

    return queryset.order_by("-updated_at", "-created_at")[: AspirationSubmission.MAX_FEATURED]


def find_ticket_by_ticket_id(ticket_id):
    if not ticket_id:
        return None
    return (
        AspirationSubmission.objects.select_related("created_by", "updated_by")
        .filter(ticket_id=ticket_id)
        .first()
    )
