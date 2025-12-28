# إذا احتجت تعمل migration يدوي، استخدم هذا الكود:

# في terminal:
# cd backend/Education/Educational_system
# python manage.py shell

# ثم في الـ shell:
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings

# أو استخدم الأمر المباشر:
# python manage.py makemigrations eduAPI --name create_live_sessions --empty

# ثم عدل الـ migration file اللي هيتعمل في:
# backend/Education/Educational_system/eduAPI/migrations/

# الـ migration هيكون شكله كده:
"""
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('eduAPI', '0001_initial'),  # أو آخر migration عندك
    ]

    operations = [
        migrations.CreateModel(
            name='LiveSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('subject', models.CharField(max_length=255)),
                ('level', models.CharField(choices=[('1', '1st Grade'), ('2', '2nd Grade'), ('3', '3rd Grade'), ('4', '4th Grade'), ('5', '5th Grade'), ('6', '6th Grade'), ('7', '7th Grade'), ('8', '8th Grade'), ('9', '9th Grade'), ('10', '10th Grade'), ('11', '11th Grade'), ('12', '12th Grade')], max_length=2)),
                ('scheduled_datetime', models.DateTimeField()),
                ('duration_minutes', models.IntegerField(default=60, validators=[django.core.validators.MinValueValidator(15), django.core.validators.MaxValueValidator(240)])),
                ('jitsi_room_name', models.CharField(max_length=100, unique=True)),
                ('jitsi_room_password', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending Assignment'), ('ASSIGNED', 'Assigned to Students'), ('ACTIVE', 'Currently Active'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('max_participants', models.IntegerField(default=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('actual_start_time', models.DateTimeField(blank=True, null=True)),
                ('actual_end_time', models.DateTimeField(blank=True, null=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='live_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-scheduled_datetime'],
            },
        ),
        # باقي الـ models...
    ]
"""