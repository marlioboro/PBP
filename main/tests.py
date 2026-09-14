from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


class MainTest(TestCase):
    def setUp(self):
        Experience.objects.all().delete()
        self.experience = Experience.objects.create(
            title='RISTEK Fasilkom UI',
            description=(
                'Participated in the Game Development Special Interest Group '
                'and learned to turn gameplay ideas into prototypes.'
            ),
            category='organization',
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse('main:show_main'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertNotContains(response, self.experience.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_experience")}"',
        )
        self.assertContains(response, 'data-theme-toggle')
        self.assertNotContains(response, 'SELECTED OUTPUT')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get('/halaman-yang-tidak-ada/')

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), 'RISTEK Fasilkom UI')
        self.assertEqual(self.experience.category, 'organization')
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse('main:show_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experience.html')
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, 'Organization')
        self.assertContains(response, 'Sedang berlangsung')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse('main:show_experience'))

        self.assertContains(response, 'Belum ada pengalaman yang ditambahkan.')

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse('main:show_experience'))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, 'Selesai')
        self.assertNotContains(response, 'Sedang berlangsung')


class ProjectTest(TestCase):
    def setUp(self):
        # Keep these tests independent from the portfolio records seeded by the
        # data migration so each expected result is explicit.
        Project.objects.all().delete()
        self.project = Project.objects.create(
            title='Cipher Quest',
            slug='cipher-quest',
            summary='A security puzzle about tracing clues through a virtual city.',
            category='security',
            status='prototype',
            role='Solo Developer',
            technologies='Python, Django, Cryptography',
            project_url='https://example.com/cipher-quest',
            featured=True,
        )

    def test_project_url_uses_expected_template(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects.html')

    def test_project_data_is_rendered_from_database(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.summary)
        self.assertContains(response, 'Cybersecurity &amp; CTF')
        self.assertContains(response, 'Prototype')
        self.assertContains(response, 'Cryptography')
        self.assertContains(
            response,
            f'href="{reverse("main:show_project_detail", args=[self.project.slug])}"',
        )

    def test_empty_project_page_has_clear_message(self):
        Project.objects.all().delete()
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Belum ada proyek yang ditambahkan.')

    def test_project_model_helpers(self):
        self.assertEqual(str(self.project), 'Cipher Quest')
        self.assertEqual(
            self.project.technology_list,
            ['Python', 'Django', 'Cryptography'],
        )

    def test_project_detail_page_renders_selected_project(self):
        response = self.client.get(
            reverse('main:show_project_detail', args=[self.project.slug])
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_detail.html')
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.summary)
        self.assertContains(response, self.project.role)

    def test_unknown_project_detail_returns_404(self):
        response = self.client.get(
            reverse('main:show_project_detail', args=['not-a-real-project'])
        )

        self.assertEqual(response.status_code, 404)

    def test_project_page_is_linked_but_separate_from_profile(self):
        response = self.client.get(reverse('main:show_main'))

        self.assertNotContains(response, self.project.title)
        self.assertContains(
            response,
            f'href="{reverse("main:show_projects")}"',
        )


class CuratedPortfolioDataTest(TestCase):
    def test_organization_experiences_are_seeded(self):
        ristek = Experience.objects.get(title='RISTEK Fasilkom UI')
        bem = Experience.objects.get(
            title='BEM Fasilkom UI — Departemen Pengabdian Masyarakat'
        )

        self.assertEqual(ristek.category, 'organization')
        self.assertEqual(bem.category, 'organization')

    def test_sortify_is_a_project_instead_of_an_experience(self):
        sortify = Project.objects.get(slug='sortify-ai')

        self.assertFalse(Experience.objects.filter(title='Sortify AI').exists())
        self.assertEqual(sortify.category, 'data')
        self.assertEqual(sortify.role, 'Computer Vision Developer')
        self.assertEqual(sortify.project_url, '')
