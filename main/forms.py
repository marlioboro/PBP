from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from main.models import Experience, Project


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            'title',
            'description',
            'category',
            'thumbnail',
            'ended_at',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'ended_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }
        help_texts = {
            'thumbnail': 'Opsional; gunakan URL gambar yang diawali https://.',
            'ended_at': 'Kosongkan jika pengalaman masih berlangsung.',
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data['title']).strip()
        if not title:
            raise ValidationError('Judul pengalaman tidak boleh hanya berisi tag HTML.')
        return title

    def clean_description(self):
        description = strip_tags(self.cleaned_data['description']).strip()
        if not description:
            raise ValidationError('Deskripsi pengalaman tidak boleh hanya berisi tag HTML.')
        return description


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'summary',
            'category',
            'status',
            'role',
            'technologies',
            'project_url',
            'thumbnail_url',
            'featured',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 5}),
        }
        help_texts = {
            'technologies': 'Pisahkan nama teknologi dengan koma.',
            'project_url': 'Opsional; gunakan URL lengkap yang diawali https://.',
            'thumbnail_url': 'Opsional; gunakan URL gambar yang diawali https://.',
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data['title']).strip()
        if not title:
            raise ValidationError('Nama proyek tidak boleh hanya berisi tag HTML.')
        return title

    def clean_summary(self):
        return strip_tags(self.cleaned_data['summary']).strip()

    def clean_role(self):
        return strip_tags(self.cleaned_data['role']).strip()

    def clean_technologies(self):
        return strip_tags(self.cleaned_data['technologies']).strip()
