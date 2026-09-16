from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from main.forms import ProjectForm
from main.models import Experience, Project


PROFILE_CONTEXT = {
    'name': 'Muhammad Farel Ammar',
    'npm': '2506585731',
    'study_program': 'S1 Ilmu Komputer',
    'bio': (
        'Game developer and Computer Science student at Universitas Indonesia '
        'who enjoys building playful systems, solving CTF challenges, and '
        'finding useful stories inside data.'
    ),
}


def build_context(**page_context):
    return {**PROFILE_CONTEXT, **page_context}


def show_main(request):
    context = build_context(
        active_page='profile',
        project_count=Project.objects.count(),
    )
    return render(request, 'index.html', context)


def show_experience(request):
    context = build_context(
        active_page='experience',
        experience_list=Experience.objects.all(),
    )
    return render(request, 'experience.html', context)


def show_projects(request):
    # Tutorial 03 demonstrates the JSON delivery boundary even though this
    # Django app could query the ORM directly for its own template.
    projects = [
        item.object
        for item in serializers.deserialize(
            'json', get_projects_json(request).content
        )
    ]
    all_projects = Project.objects.all()
    context = build_context(
        active_page='projects',
        project_list=projects,
        project_count=all_projects.count(),
        released_count=all_projects.filter(status='released').count(),
        featured_count=all_projects.filter(featured=True).count(),
        title_query=request.GET.get('title', '').strip(),
    )
    return render(request, 'projects.html', context)


def get_projects_json(request):
    projects = Project.objects.all()
    title_query = request.GET.get('title', '').strip()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    return HttpResponse(
        serializers.serialize('json', projects),
        content_type='application/json',
    )


def show_project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    context = build_context(
        active_page='projects',
        project=project,
    )
    return render(request, 'project_detail.html', context)


@staff_member_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        project = form.save(commit=False)
        base_slug = slugify(project.title) or 'project'
        slug = base_slug
        suffix = 2
        while Project.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1
        project.slug = slug
        project.save()
        messages.success(request, f'Project "{project.title}" berhasil ditambahkan.')
        return redirect('main:show_projects')

    context = build_context(
        active_page='projects',
        form=form,
    )
    return render(request, 'projects_form.html', context)


@staff_member_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    title = project.title
    project.delete()
    messages.success(request, f'Project "{title}" berhasil dihapus.')
    return redirect('main:show_projects')
