from django.db import migrations


RISTEK_DESCRIPTION = (
    'Active member of the Game Development Special Interest Group, learning '
    'and building game prototypes with other members.'
)

BEM_DESCRIPTION = (
    'Member of Departemen Pengabdian Masyarakat, contributing to '
    'community-focused programs and social initiatives.'
)

SORTIFY_DESCRIPTION = (
    'Developed the waste-classification component and contributed to a web '
    'app that directs users to nearby disposal locations.'
)


def curate_portfolio_data(apps, schema_editor):
    experience_model = apps.get_model('main', 'Experience')
    project_model = apps.get_model('main', 'Project')

    experience_model.objects.update_or_create(
        title='RISTEK Fasilkom UI',
        defaults={
            'description': RISTEK_DESCRIPTION,
            'category': 'organization',
            'ended_at': None,
        },
    )
    experience_model.objects.update_or_create(
        title='BEM Fasilkom UI — Departemen Pengabdian Masyarakat',
        defaults={
            'description': BEM_DESCRIPTION,
            'category': 'organization',
            'ended_at': None,
        },
    )

    experience_model.objects.filter(title='Sortify AI').delete()
    project_model.objects.update_or_create(
        slug='sortify-ai',
        defaults={
            'title': 'Sortify AI',
            'summary': SORTIFY_DESCRIPTION,
            'category': 'data',
            'status': 'prototype',
            'role': 'Computer Vision Developer',
            'technologies': (
                'Python, Computer Vision, Machine Learning, Web Development'
            ),
            'project_url': '',
            'thumbnail_url': '',
            'featured': True,
        },
    )


def reverse_portfolio_data(apps, schema_editor):
    experience_model = apps.get_model('main', 'Experience')
    project_model = apps.get_model('main', 'Project')

    experience_model.objects.filter(
        title='BEM Fasilkom UI — Departemen Pengabdian Masyarakat'
    ).delete()
    experience_model.objects.filter(title='RISTEK Fasilkom UI').update(
        category='volunteer',
        description='Active member of the Game Development Special Interest Group.',
    )
    project_model.objects.filter(slug='sortify-ai').delete()
    experience_model.objects.update_or_create(
        title='Sortify AI',
        defaults={
            'description': SORTIFY_DESCRIPTION,
            'category': 'research',
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0004_alter_experience_category_alter_project_project_url'),
    ]

    operations = [
        migrations.RunPython(curate_portfolio_data, reverse_portfolio_data),
    ]
