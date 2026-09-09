from django.shortcuts import render

from main.models import Experience


def show_main(request):
    context = {
        'name': 'Muhammad Farel Ammar',
        'npm': '2506585731',
        'study_program': 'S1 Ilmu Komputer',
        'bio': (
            'Computer Science student at Universitas Indonesia who is building '
            'a personal portfolio while learning Django, HTML5, and CSS3 '
            'through PBP, because they told me to.'
        ),
    }
    return render(request, 'index.html', context)


def show_experience(request):
    context = {
        'name': 'Muhammad Farel Ammar',
        'experience_list': Experience.objects.all(),
    }
    return render(request, 'experience.html', context)
