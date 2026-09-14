import uuid

from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('organization', 'Organization'),
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default='full-time',
    )
    thumbnail = models.URLField(blank=True, default='')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    CATEGORY_CHOICES = [
        ('game', 'Game Development'),
        ('security', 'Cybersecurity & CTF'),
        ('data', 'Data & AI'),
    ]
    STATUS_CHOICES = [
        ('released', 'Released'),
        ('in-development', 'In Development'),
        ('prototype', 'Prototype'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    summary = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='game',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='released',
    )
    role = models.CharField(max_length=120)
    technologies = models.CharField(max_length=255)
    project_url = models.URLField(blank=True, default='')
    thumbnail_url = models.URLField(blank=True, default='')
    featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['-featured', 'title']

    def __str__(self):
        return self.title

    @property
    def technology_list(self):
        return [
            technology.strip()
            for technology in self.technologies.split(',')
            if technology.strip()
        ]
