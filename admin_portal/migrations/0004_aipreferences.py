# Generated migration to add AIPreferences
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('admin_portal', '0003_aicontentsuggestion'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_model', models.CharField(blank=True, max_length=150, help_text='Fallback model for agents')),
                ('research_model', models.CharField(blank=True, max_length=150)),
                ('classification_model', models.CharField(blank=True, max_length=150)),
                ('metadata_model', models.CharField(blank=True, max_length=150)),
                ('quality_model', models.CharField(blank=True, max_length=150)),
                ('research_fetch_timeout', models.IntegerField(default=30)),
                ('research_fetch_retries', models.IntegerField(default=3)),
            ],
            options={
                'verbose_name': 'AI Preferences',
                'verbose_name_plural': 'AI Preferences',
            },
        ),
    ]
