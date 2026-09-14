from django.shortcuts import get_object_or_404, render

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
    projects = Project.objects.all()
    context = build_context(
        active_page='projects',
        project_list=projects,
        project_count=projects.count(),
        released_count=projects.filter(status='released').count(),
        featured_count=projects.filter(featured=True).count(),
    )
    return render(request, 'projects.html', context)


def show_project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    context = build_context(
        active_page='projects',
        project=project,
    )
    return render(request, 'project_detail.html', context)
