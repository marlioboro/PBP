from django.db import migrations


PROJECTS = [
    {
        'title': 'Where Do You Belong',
        'slug': 'where-do-you-belong',
        'summary': (
            'A narrative puzzle game about an afterlife train conductor '
            'working five days to correct a celestial clerical mistake.'
        ),
        'category': 'game',
        'status': 'in-development',
        'role': 'Collaborator',
        'technologies': 'Godot, HTML5, 2D, Singleplayer',
        'project_url': 'https://mir4na.itch.io/where-do-you-belong',
        'thumbnail_url': (
            'https://img.itch.zone/aW1nLzI5OTA1Njc4LnBuZw=='
            '/original/JWN1Sh.png'
        ),
        'featured': True,
    },
    {
        'title': 'Brine & Blade',
        'slug': 'brine-and-blade',
        'summary': (
            'A top-down 2D roguelite bullet hell about cutting through '
            'projectiles and turning abyssal pressure into a counterattack.'
        ),
        'category': 'game',
        'status': 'released',
        'role': 'Programmer',
        'technologies': 'Godot, HTML5, 2D, Bullet Hell, Roguelike',
        'project_url': 'https://marlioboro.itch.io/brine-and-blade',
        'thumbnail_url': (
            'https://img.itch.zone/aW1nLzI4NzU4Nzk5LnBuZw=='
            '/original/rFavwS.png'
        ),
        'featured': True,
    },
    {
        'title': 'Wait, New Rule!',
        'slug': 'wait-new-rule',
        'summary': (
            'A 3D platformer built for GAMESEED 2026 around the childhood '
            'challenge: the floor is lava.'
        ),
        'category': 'game',
        'status': 'released',
        'role': 'Developer',
        'technologies': 'Godot, HTML5, 3D Platformer, Game Jam',
        'project_url': 'https://marlioboro.itch.io/wait-new-rules',
        'thumbnail_url': (
            'https://img.itch.zone/aW1nLzI4Mjc4NDIzLnBuZw=='
            '/original/LWdeaL.png'
        ),
        'featured': False,
    },
    {
        'title': 'Remora',
        'slug': 'remora',
        'summary': (
            'An in-development browser adventure made with Good Bones Games.'
        ),
        'category': 'game',
        'status': 'in-development',
        'role': 'Developer',
        'technologies': 'Godot, HTML5, Adventure',
        'project_url': 'https://marlioboro.itch.io/remora',
        'thumbnail_url': (
            'https://img.itch.zone/aW1nLzI5MjQ5MDIyLnBuZw=='
            '/original/ZdXWo0.png'
        ),
        'featured': False,
    },
    {
        'title': 'Survi-Vim>/',
        'slug': 'survi-vim',
        'summary': 'A released browser action game built with Godot.',
        'category': 'game',
        'status': 'released',
        'role': 'Solo Developer',
        'technologies': 'Godot, HTML5, Action',
        'project_url': 'https://marlioboro.itch.io/survi-vim',
        'thumbnail_url': '',
        'featured': False,
    },
    {
        'title': 'Trust The Light.',
        'slug': 'trust-the-light',
        'summary': (
            'Lost in the woods after a crash, you must decide whether to '
            'trust your limited matches or find another way out.'
        ),
        'category': 'game',
        'status': 'released',
        'role': 'Solo Developer',
        'technologies': 'HTML5, Adventure, Atmospheric',
        'project_url': 'https://marlioboro.itch.io/trust-the-light',
        'thumbnail_url': '',
        'featured': True,
    },
]


def seed_projects(apps, schema_editor):
    project_model = apps.get_model('main', 'Project')

    for project in PROJECTS:
        project_model.objects.update_or_create(
            slug=project['slug'],
            defaults=project,
        )


def remove_seeded_projects(apps, schema_editor):
    project_model = apps.get_model('main', 'Project')
    slugs = [project['slug'] for project in PROJECTS]
    project_model.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('main', '0002_project'),
    ]

    operations = [
        migrations.RunPython(seed_projects, remove_seeded_projects),
    ]
