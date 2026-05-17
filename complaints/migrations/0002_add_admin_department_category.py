# complaints/migrations/0002_add_admin_department_category.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('complaints', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaint',
            name='category',
            field=models.CharField(
                choices=[
                    ('roads', 'Roads & Infrastructure'),
                    ('water', 'Water & Sewerage'),
                    ('electricity', 'Electricity & Street Lights'),
                    ('sanitation', 'Sanitation & Waste'),
                    ('parks', 'Parks & Recreation'),
                    ('health', 'Public Health'),
                    ('building', 'Building & Construction'),
                    ('transport', 'Transport & Traffic'),
                    ('environment', 'Environment & Drainage'),
                    ('fire', 'Fire & Emergency'),
                    ('it', 'IT & Technology'),
                    ('admin_dept', 'General Administration'),
                    ('other', 'Other'),
                ],
                max_length=30,
            ),
        ),
    ]
