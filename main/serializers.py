from django.utils.html import strip_tags
from django.utils.text import slugify
from rest_framework import serializers

from main.models import Experience, Project


class StarFieldsMixin:
    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and request.user in obj.starred_by.all()
        )

    def get_starred_by_names(self, obj):
        return ', '.join(user.username for user in obj.starred_by.all())


class ProjectSerializer(StarFieldsMixin, serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    technology_list = serializers.ReadOnlyField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'slug', 'title', 'summary', 'category', 'category_display',
            'status', 'status_display', 'role', 'technologies', 'technology_list',
            'project_url', 'thumbnail_url', 'featured', 'star_count',
            'is_starred', 'starred_by_names',
        ]
        read_only_fields = ['id', 'slug']

    def validate_title(self, value):
        title = strip_tags(value).strip()
        if not title:
            raise serializers.ValidationError('Title cannot be empty.')
        return title

    def validate_summary(self, value):
        summary = strip_tags(value).strip()
        if not summary:
            raise serializers.ValidationError('Summary cannot be empty.')
        return summary

    def validate_role(self, value):
        return strip_tags(value).strip()

    def validate_technologies(self, value):
        return strip_tags(value).strip()

    def create(self, validated_data):
        base_slug = slugify(validated_data['title']) or 'project'
        slug = base_slug
        suffix = 2
        while Project.objects.filter(slug=slug).exists():
            slug = f'{base_slug[:255 - len(str(suffix)) - 1]}-{suffix}'
            suffix += 1
        return Project.objects.create(slug=slug, **validated_data)


class ExperienceSerializer(StarFieldsMixin, serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_ongoing = serializers.ReadOnlyField()
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'thumbnail', 'started_at', 'ended_at', 'is_ongoing',
            'star_count', 'is_starred', 'starred_by_names',
        ]
        read_only_fields = ['id', 'started_at']

    def validate_title(self, value):
        title = strip_tags(value).strip()
        if not title:
            raise serializers.ValidationError('Title cannot be empty.')
        return title

    def validate_description(self, value):
        description = strip_tags(value).strip()
        if not description:
            raise serializers.ValidationError('Description cannot be empty.')
        return description
