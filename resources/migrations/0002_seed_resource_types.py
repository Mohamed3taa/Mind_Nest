from django.db import migrations


def seed_resource_types(apps, schema_editor):
    ResourceType = apps.get_model('resources', 'ResourceType')
    types = [
        {'name': 'Video',     'icon': 'bi-play-circle'},
        {'name': 'Article',   'icon': 'bi-file-text'},
        {'name': 'Course',    'icon': 'bi-mortarboard'},
        {'name': 'Book',      'icon': 'bi-book'},
        {'name': 'Tool',      'icon': 'bi-tools'},
        {'name': 'GitHub',    'icon': 'bi-github'},
        {'name': 'Other',     'icon': 'bi-link-45deg'},
    ]
    for t in types:
        ResourceType.objects.get_or_create(name=t['name'], defaults={'icon': t['icon']})


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('resources', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(seed_resource_types, reverse_seed),
    ]
