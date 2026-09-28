from django.db import migrations


def create_editor_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    group.objects.get_or_create(name='Editor')


def remove_editor_group(apps, schema_editor):
    group = apps.get_model('auth', 'Group')
    group.objects.filter(name='Editor').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('main', '0006_project_starred_by'),
    ]

    operations = [
        migrations.RunPython(create_editor_group, remove_editor_group),
    ]
