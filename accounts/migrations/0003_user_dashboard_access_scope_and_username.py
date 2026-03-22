from django.db import migrations, models


def populate_dashboard_user_fields(apps, schema_editor):
    User = apps.get_model("accounts", "User")

    for user in User.objects.all().order_by("id"):
        base_username = (user.email or "").split("@", 1)[0] or f"user-{user.pk}"
        candidate = base_username
        suffix = 1
        while User.objects.exclude(pk=user.pk).filter(dashboard_username=candidate).exists():
            candidate = f"{base_username}{suffix}"
            suffix += 1

        user.dashboard_username = candidate
        user.dashboard_access_scope = "full"
        user.save(update_fields=["dashboard_username", "dashboard_access_scope"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_created_by_user_updated_by_alter_user_avatar"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="dashboard_access_scope",
            field=models.CharField(
                choices=[
                    ("full", "Superadmin"),
                    ("academic", "Akademik"),
                    ("competency", "Kompetensi"),
                    ("advocacy", "Advokasi"),
                ],
                default="full",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="dashboard_username",
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.RunPython(populate_dashboard_user_fields, migrations.RunPython.noop),
    ]
