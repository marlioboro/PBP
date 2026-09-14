from django.contrib import admin

from main.models import Experience, Project


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'started_at', 'ended_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'role', 'featured')
    list_filter = ('category', 'status', 'featured')
    search_fields = ('title', 'summary', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
