import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
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

    def test_experience_create_form_is_accessible(self):
        response = self.client.get(reverse('main:create_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experience_form.html')
        self.assertContains(response, 'Save experience')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_create_experience_saves_valid_form(self):
        response = self.client.post(
            reverse('main:create_experience'),
            {
                'title': 'Teaching Assistant',
                'description': 'Helped students learn Django.',
                'category': 'part-time',
                'thumbnail': 'https://example.com/assistant.png',
                'ended_at': '',
            },
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertTrue(
            Experience.objects.filter(title='Teaching Assistant').exists()
        )

    def test_create_experience_rejects_invalid_form(self):
        response = self.client.post(
            reverse('main:create_experience'),
            {'title': '', 'description': '', 'category': 'organization'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Experience.objects.count(), 1)


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

    def test_create_form_requires_staff(self):
        url = reverse('main:create_project')
        self.assertEqual(self.client.get(url).status_code, 302)
        self.assertEqual(self.client.post(url, {}).status_code, 302)

    def test_staff_can_create_project_with_unique_slug(self):
        user = get_user_model().objects.create_user(
            username='portfolio-admin', password='test-password', is_staff=True
        )
        self.client.force_login(user)
        url = reverse('main:create_project')
        self.assertContains(self.client.get(url), 'Save project')
        payload = {
            'title': self.project.title,
            'summary': 'A second project with the same title.',
            'category': 'game',
            'status': 'released',
            'role': 'Game Developer',
            'technologies': 'Godot, Python',
            'project_url': 'https://example.com/game',
            'thumbnail_url': '',
            'featured': 'on',
        }

        response = self.client.post(url, payload)

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertTrue(Project.objects.filter(slug='cipher-quest-2').exists())
        self.assertEqual(Project.objects.count(), 2)

    def test_create_form_rejects_invalid_project(self):
        user = get_user_model().objects.create_user(
            username='portfolio-admin', password='test-password', is_staff=True
        )
        self.client.force_login(user)

        response = self.client.post(reverse('main:create_project'), {'title': ''})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Project.objects.count(), 1)

    def test_json_endpoint_returns_model_data(self):
        response = self.client.get(reverse('main:get_projects_json'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pk'], str(self.project.id))
        self.assertEqual(data[0]['fields']['title'], self.project.title)

    def test_json_title_filter_is_case_insensitive(self):
        response = self.client.get(
            reverse('main:get_projects_json'), {'title': '  CIPHER  '}
        )
        missing = self.client.get(
            reverse('main:get_projects_json'), {'title': 'missing'}
        )

        self.assertEqual(len(json.loads(response.content)), 1)
        self.assertEqual(json.loads(missing.content), [])

    def test_project_search_uses_json_results(self):
        response = self.client.get(
            reverse('main:show_projects'), {'title': 'missing'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['project_list'], [])
        self.assertContains(response, 'Tidak ada proyek dengan judul')
        self.assertNotContains(response, self.project.summary)

    def test_delete_controls_are_visible_only_to_staff(self):
        url = reverse('main:show_projects')
        self.assertNotContains(self.client.get(url), 'data-delete-dialog')
        user = get_user_model().objects.create_user(
            username='portfolio-admin', password='test-password', is_staff=True
        )
        self.client.force_login(user)

        response = self.client.get(url)

        self.assertContains(response, 'data-delete-dialog')
        self.assertContains(
            response,
            reverse('main:delete_project', args=[self.project.id]),
        )

    def test_delete_requires_staff_and_post(self):
        url = reverse('main:delete_project', args=[self.project.id])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())
        user = get_user_model().objects.create_user(
            username='portfolio-admin', password='test-password', is_staff=True
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(url).status_code, 405)

        response = self.client.post(url)

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_post_requires_csrf_token(self):
        user = get_user_model().objects.create_user(
            username='portfolio-admin', password='test-password', is_staff=True
        )
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(user)

        response = csrf_client.post(
            reverse('main:delete_project', args=[self.project.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())


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
