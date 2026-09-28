import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.permissions import can_update_portfolio, is_editor


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
        last_login=request.COOKIES.get(
            'last_login',
            'Belum ada sesi login / Cookie tidak ditemukan',
        ),
    )
    return render(request, 'index.html', context)


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Akun berhasil dibuat. Silakan login.')
        return redirect('main:login')

    context = build_context(
        active_page='register',
        form=form,
    )
    return render(request, 'register.html', context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        response = redirect('main:show_main')
        response.set_cookie(
            'last_login',
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        )
        return response

    context = build_context(
        active_page='login',
        form=form,
    )
    return render(request, 'login.html', context)


def logout_user(request):
    logout(request)
    response = redirect('main:show_main')
    response.delete_cookie('last_login')
    return response


def show_experience(request):
    experiences = [
        item.object
        for item in serializers.deserialize(
            'json', get_experiences_json(request).content
        )
    ]
    context = build_context(
        active_page='experience',
        experience_list=experiences,
        title_query=request.GET.get('title', '').strip(),
        is_editor=is_editor(request.user),
    )
    return render(request, 'experience.html', context)


def get_experiences_json(request):
    experiences = Experience.objects.all().order_by('-started_at')
    title_query = request.GET.get('title', '').strip()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)
    return HttpResponse(
        serializers.serialize(
            'json',
            experiences,
            use_natural_foreign_keys=True,
        ),
        content_type='application/json',
    )


@login_required(login_url='/login/')
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        experience = form.save()
        messages.success(
            request,
            f'Experience "{experience.title}" berhasil ditambahkan.',
        )
        return redirect('main:show_experience')

    context = build_context(
        active_page='experience',
        form=form,
        form_title='Add experience',
        form_label='// NEW_JOURNEY',
        submit_label='Save experience',
    )
    return render(request, 'experience_form.html', context)


@login_required(login_url='/login/')
def update_experience(request, experience_id):
    if not can_update_portfolio(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, id=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == 'POST' and form.is_valid():
        experience = form.save()
        messages.success(
            request,
            f'Experience "{experience.title}" berhasil diperbarui.',
        )
        return redirect('main:show_experience')

    context = build_context(
        active_page='experience',
        form=form,
        experience=experience,
        form_title='Edit experience',
        form_label='// UPDATE_JOURNEY',
        submit_label='Update experience',
    )
    return render(request, 'experience_form.html', context)


@login_required(login_url='/login/')
@require_POST
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, id=experience_id)
    title = experience.title
    experience.delete()
    messages.success(request, f'Experience "{title}" berhasil dihapus.')
    return redirect('main:show_experience')


@login_required(login_url='/login/')
@require_POST
def toggle_experience_star(request, experience_id):
    experience = get_object_or_404(Experience, id=experience_id)
    if experience.starred_by.filter(id=request.user.id).exists():
        experience.starred_by.remove(request.user)
    else:
        experience.starred_by.add(request.user)
    return redirect('main:show_experience')


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
        serializers.serialize(
            'json',
            projects,
            use_natural_foreign_keys=True,
        ),
        content_type='application/json',
    )


def show_project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    context = build_context(
        active_page='projects',
        project=project,
    )
    return render(request, 'project_detail.html', context)


@login_required(login_url='/login/')
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

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


@login_required(login_url='/login/')
@require_POST
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, id=project_id)
    title = project.title
    project.delete()
    messages.success(request, f'Project "{title}" berhasil dihapus.')
    return redirect('main:show_projects')


@login_required(login_url='/login/')
@require_POST
def toggle_star(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if project.starred_by.filter(id=request.user.id).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    return redirect('main:show_projects')
