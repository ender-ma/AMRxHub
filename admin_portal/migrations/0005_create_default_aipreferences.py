from django.db import migrations


def create_default_prefs(apps, schema_editor):
    AIPreferences = apps.get_model('admin_portal', 'AIPreferences')
    if not AIPreferences.objects.exists():
        AIPreferences.objects.create(default_model='gpt-5.6-terra', research_model='', classification_model='', metadata_model='', quality_model='', research_fetch_timeout=30, research_fetch_retries=3)


class Migration(migrations.Migration):
    dependencies = [
        ('admin_portal', '0004_aipreferences'),
    ]

    operations = [
        migrations.RunPython(create_default_prefs, migrations.RunPython.noop),
    ]
