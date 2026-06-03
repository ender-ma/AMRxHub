# In the newly created migration file
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('tools', '0008_remove_analysishistory_references'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS tools_analysishistory;",
            "SELECT 1;"  # Dummy reverse operation
        ),
    ]