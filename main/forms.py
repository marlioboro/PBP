from django import forms

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
            'ended_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        help_texts = {
            'thumbnail': 'Opsional; gunakan URL gambar yang diawali https://.',
            'ended_at': 'Kosongkan jika pengalaman masih berlangsung.',
        }


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
