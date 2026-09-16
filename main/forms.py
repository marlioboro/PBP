from django import forms

from main.models import Project


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
