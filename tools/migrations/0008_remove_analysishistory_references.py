from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
    ("tools", "0007_toolcategory_detailed_description"),
    ]
    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS tools_analysishistory;",
            "SELECT 1;",
        ),
    ]