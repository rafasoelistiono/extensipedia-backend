from accounts.models import User


def get_user_list_queryset():
    return User.objects.select_related("created_by", "updated_by").all()
