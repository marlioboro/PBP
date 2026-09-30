import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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
        self.owner = get_user_model().objects.create_user(
            username='portfolio-owner',
            is_superuser=True,
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
        self.client.force_login(self.owner)
        response = self.client.get(reverse('main:create_experience'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experience_form.html')
        self.assertContains(response, 'Save experience')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_create_experience_saves_valid_form(self):
        self.client.force_login(self.owner)
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
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('main:create_experience'),
            {'title': '', 'description': '', 'category': 'organization'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Experience.objects.count(), 1)

    def test_experience_json_endpoint_returns_model_data(self):
        response = self.client.get(reverse('main:get_experiences_json'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['Content-Type'].startswith('application/json'))
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['pk'], str(self.experience.id))
        self.assertEqual(data[0]['fields']['title'], self.experience.title)

    def test_experience_json_filter_is_case_insensitive(self):
        response = self.client.get(
            reverse('main:get_experiences_json'), {'title': '  ristek  '}
        )
        missing = self.client.get(
            reverse('main:get_experiences_json'), {'title': 'missing'}
        )

        self.assertEqual(len(json.loads(response.content)), 1)
        self.assertEqual(json.loads(missing.content), [])

    def test_experience_page_displays_deserialized_json_results(self):
        response = self.client.get(
            reverse('main:show_experience'), {'title': 'missing'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['experience_list'], [])
        self.assertContains(response, 'Tidak ada pengalaman dengan judul')
        self.assertNotContains(response, self.experience.description)

    def test_update_experience_edits_existing_object(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse('main:update_experience', args=[self.experience.id]),
            {
                'title': 'RISTEK Fasilkom UI — Game Development SIG',
                'description': self.experience.description,
                'category': 'organization',
                'thumbnail': '',
                'ended_at': '',
            },
        )

        self.assertRedirects(response, reverse('main:show_experience'))
        self.experience.refresh_from_db()
        self.assertEqual(
            self.experience.title,
            'RISTEK Fasilkom UI — Game Development SIG',
        )
        self.assertEqual(Experience.objects.count(), 1)

    def test_update_form_contains_current_experience_values(self):
        self.client.force_login(self.owner)
        self.experience.ended_at = timezone.datetime(
            2026,
            9,
            22,
            10,
            30,
            tzinfo=timezone.get_current_timezone(),
        )
        self.experience.save()

        response = self.client.get(
            reverse('main:update_experience', args=[self.experience.id])
        )

        self.assertContains(response, self.experience.title)
        self.assertContains(response, '2026-09-22T10:30')

    def test_update_unknown_experience_returns_404(self):
        self.client.force_login(self.owner)
        response = self.client.get(
            reverse(
                'main:update_experience',
                args=['00000000-0000-0000-0000-000000000000'],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_experience_accepts_post_only(self):
        self.client.force_login(self.owner)
        url = reverse('main:delete_experience', args=[self.experience.id])
        self.assertEqual(self.client.get(url).status_code, 405)

        response = self.client.post(url)

        self.assertRedirects(response, reverse('main:show_experience'))
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_delete_experience_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.owner)

        response = csrf_client.post(
            reverse('main:delete_experience', args=[self.experience.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())


class ExperiencePermissionTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title='BEM Fasilkom UI',
            description='Community service department.',
            category='organization',
        )
        self.regular_user = get_user_model().objects.create_user(
            username='regular-user'
        )
        self.editor = get_user_model().objects.create_user(username='editor-user')
        self.editor_group, _ = Group.objects.get_or_create(name='Editor')
        self.editor.groups.add(self.editor_group)
        self.owner = get_user_model().objects.create_user(
            username='portfolio-owner',
            is_superuser=True,
        )

    def test_editor_group_is_created_by_migration(self):
        self.assertTrue(Group.objects.filter(name='Editor').exists())

    def test_create_is_available_only_to_superuser(self):
        url = reverse('main:create_experience')
        self.assertRedirects(
            self.client.get(url),
            f'{reverse("main:login")}?next={url}',
        )

        for user in (self.regular_user, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_update_is_available_to_editor_and_superuser(self):
        url = reverse('main:update_experience', args=[self.experience.id])
        self.assertRedirects(
            self.client.get(url),
            f'{reverse("main:login")}?next={url}',
        )

        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(url).status_code, 403)

        for user in (self.editor, self.owner):
            self.client.force_login(user)
            self.assertEqual(self.client.get(url).status_code, 200)

    def test_delete_is_available_only_to_superuser(self):
        url = reverse('main:delete_experience', args=[self.experience.id])
        self.assertRedirects(
            self.client.post(url),
            f'{reverse("main:login")}?next={url}',
        )

        for user in (self.regular_user, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.client.post(url).status_code, 403)
            self.assertTrue(Experience.objects.filter(id=self.experience.id).exists())

        self.client.force_login(self.owner)
        self.assertRedirects(
            self.client.post(url),
            reverse('main:show_experience'),
        )
        self.assertFalse(Experience.objects.filter(id=self.experience.id).exists())

    def test_action_controls_match_each_role(self):
        list_url = reverse('main:show_experience')
        edit_url = reverse(
            'main:update_experience',
            args=[self.experience.id],
        )

        for user in (None, self.regular_user):
            if user:
                self.client.force_login(user)
            else:
                self.client.logout()
            response = self.client.get(list_url)
            self.assertNotContains(response, '+ Add experience')
            self.assertNotContains(response, f'href="{edit_url}"')
            self.assertNotContains(response, 'data-delete-dialog')

        self.client.force_login(self.editor)
        editor_response = self.client.get(list_url)
        self.assertNotContains(editor_response, '+ Add experience')
        self.assertContains(editor_response, f'href="{edit_url}"')
        self.assertNotContains(editor_response, 'data-delete-dialog')

        self.client.force_login(self.owner)
        owner_response = self.client.get(list_url)
        self.assertContains(owner_response, '+ Add experience')
        self.assertContains(owner_response, f'href="{edit_url}"')
        self.assertContains(owner_response, 'data-delete-dialog')

    def test_regular_user_can_toggle_experience_star(self):
        url = reverse('main:toggle_experience_star', args=[self.experience.id])
        self.client.force_login(self.regular_user)

        self.assertRedirects(
            self.client.post(url),
            reverse('main:show_experience'),
        )
        self.assertTrue(
            self.experience.starred_by.filter(id=self.regular_user.id).exists()
        )

        self.client.post(url)
        self.assertFalse(
            self.experience.starred_by.filter(id=self.regular_user.id).exists()
        )

    def test_experience_star_requires_login_post_and_csrf(self):
        url = reverse('main:toggle_experience_star', args=[self.experience.id])
        self.assertRedirects(
            self.client.post(url),
            f'{reverse("main:login")}?next={url}',
        )

        self.client.force_login(self.regular_user)
        self.assertEqual(self.client.get(url).status_code, 405)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.regular_user)
        self.assertEqual(csrf_client.post(url).status_code, 403)

    def test_experience_json_uses_user_natural_key(self):
        self.experience.starred_by.add(self.regular_user)

        response = self.client.get(reverse('main:get_experiences_json'))
        records = json.loads(response.content)
        record = next(
            item for item in records if item['pk'] == str(self.experience.id)
        )

        self.assertEqual(record['fields']['starred_by'], [['regular-user']])


class AuthenticationTest(TestCase):
    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse('main:register'),
            {
                'username': 'new-player',
                'password1': 'Strong-pass-2026!',
                'password2': 'Strong-pass-2026!',
            },
        )

        self.assertRedirects(response, reverse('main:login'))
        self.assertTrue(
            get_user_model().objects.filter(username='new-player').exists()
        )

    def test_login_sets_session_and_last_login_cookie(self):
        user = get_user_model().objects.create_user(
            username='player', password='Strong-pass-2026!'
        )

        response = self.client.post(
            reverse('main:login'),
            {'username': user.username, 'password': 'Strong-pass-2026!'},
        )

        self.assertRedirects(response, reverse('main:show_main'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertIn('last_login', response.cookies)

    def test_invalid_login_renders_form_error(self):
        response = self.client.post(
            reverse('main:login'),
            {'username': 'missing', 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Please enter a correct username and password')

    def test_logout_clears_session_and_last_login_cookie(self):
        user = get_user_model().objects.create_user(
            username='player', password='Strong-pass-2026!'
        )
        self.client.force_login(user)
        self.client.cookies['last_login'] = '2026-09-28 12:00:00'

        response = self.client.get(reverse('main:logout'))

        self.assertRedirects(response, reverse('main:show_main'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.cookies['last_login']['max-age'], 0)

    def test_navbar_reflects_authentication_status(self):
        anonymous = self.client.get(reverse('main:show_main'))
        self.assertContains(anonymous, reverse('main:login'))
        self.assertContains(anonymous, reverse('main:register'))

        user = get_user_model().objects.create_user(username='player')
        self.client.force_login(user)
        authenticated = self.client.get(reverse('main:show_main'))
        self.assertContains(authenticated, user.username)
        self.assertContains(authenticated, reverse('main:logout'))


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

    def test_project_page_loads_data_with_ajax(self):
        response = self.client.get(reverse('main:show_projects'))

        self.assertContains(response, 'id="project-grid"')
        self.assertContains(response, reverse('main:get_projects_json'))
        self.assertNotContains(response, self.project.summary)

        data = self.client.get(reverse('main:get_projects_json')).json()
        self.assertEqual(data[0]['fields']['summary'], self.project.summary)
        self.assertEqual(data[0]['fields']['category'], 'Cybersecurity & CTF')
        self.assertEqual(data[0]['fields']['technologies'], ['Python', 'Django', 'Cryptography'])
        self.assertEqual(data[0]['fields']['slug'], self.project.slug)

    def test_empty_project_page_has_clear_message(self):
        Project.objects.all().delete()
        response = self.client.get(reverse('main:show_projects'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Belum ada proyek yang ditambahkan atau ditemukan.')

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

    def test_create_form_requires_superuser(self):
        url = reverse('main:create_project')
        anonymous = self.client.get(url)
        self.assertRedirects(anonymous, f'{reverse("main:login")}?next={url}')

        regular_user = get_user_model().objects.create_user(username='player')
        self.client.force_login(regular_user)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_superuser_can_create_project_with_unique_slug(self):
        user = get_user_model().objects.create_user(
            username='portfolio-admin',
            password='test-password',
            is_superuser=True,
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
            username='portfolio-admin',
            password='test-password',
            is_superuser=True,
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
        self.assertContains(response, 'value="missing"')
        self.assertNotContains(response, self.project.summary)
        self.assertEqual(self.client.get(reverse('main:get_projects_json'), {'title': 'missing'}).json(), [])

    def test_delete_controls_are_visible_only_to_superuser(self):
        url = reverse('main:show_projects')
        self.assertNotContains(self.client.get(url), 'id="project-form"')
        user = get_user_model().objects.create_user(
            username='portfolio-admin',
            password='test-password',
            is_superuser=True,
        )
        self.client.force_login(user)

        response = self.client.get(url)

        self.assertContains(response, 'id="project-form"')
        self.assertContains(
            response,
            reverse('main:delete_project', args=['00000000-0000-0000-0000-000000000000']),
        )

    def test_delete_requires_superuser_and_post(self):
        url = reverse('main:delete_project', args=[self.project.id])
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

        regular_user = get_user_model().objects.create_user(username='player')
        self.client.force_login(regular_user)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

        user = get_user_model().objects.create_user(
            username='portfolio-admin',
            password='test-password',
            is_superuser=True,
        )
        self.client.force_login(user)
        self.assertEqual(self.client.get(url).status_code, 405)

        response = self.client.post(url)

        self.assertRedirects(response, reverse('main:show_projects'))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_delete_post_requires_csrf_token(self):
        user = get_user_model().objects.create_user(
            username='portfolio-admin',
            password='test-password',
            is_superuser=True,
        )
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(user)

        response = csrf_client.post(
            reverse('main:delete_project', args=[self.project.id])
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_registered_user_can_toggle_star_once(self):
        user = get_user_model().objects.create_user(username='player')
        self.client.force_login(user)
        url = reverse('main:toggle_star', args=[self.project.id])

        first_response = self.client.post(url)

        self.assertRedirects(first_response, reverse('main:show_projects'))
        self.assertTrue(self.project.starred_by.filter(id=user.id).exists())
        self.assertEqual(self.project.starred_by.count(), 1)

        second_response = self.client.post(url)

        self.assertRedirects(second_response, reverse('main:show_projects'))
        self.assertFalse(self.project.starred_by.filter(id=user.id).exists())
        self.assertEqual(self.project.starred_by.count(), 0)

    def test_star_requires_login_post_and_csrf(self):
        url = reverse('main:toggle_star', args=[self.project.id])
        self.assertRedirects(
            self.client.post(url),
            f'{reverse("main:login")}?next={url}',
        )

        user = get_user_model().objects.create_user(username='player')
        self.client.force_login(user)
        self.assertEqual(self.client.get(url).status_code, 405)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(user)
        self.assertEqual(csrf_client.post(url).status_code, 403)

    def test_project_json_shows_star_count_and_state(self):
        user = get_user_model().objects.create_user(username='player')
        self.project.starred_by.add(user)
        self.client.force_login(user)

        response = self.client.get(reverse('main:get_projects_json'))

        fields = response.json()[0]['fields']
        self.assertTrue(fields['is_starred'])
        self.assertEqual(fields['star_count'], 1)
        self.assertEqual(fields['starred_by_names'], 'player')

    def test_json_does_not_expose_user_natural_key_for_stars(self):
        user = get_user_model().objects.create_user(username='player')
        self.project.starred_by.add(user)

        response = self.client.get(reverse('main:get_projects_json'))
        fields = json.loads(response.content)[0]['fields']

        self.assertEqual(fields['star_count'], 1)
        self.assertNotIn('starred_by', fields)

    def test_ajax_create_requires_superuser_post_and_csrf(self):
        url = reverse('main:create_project_ajax')
        payload = {
            'title': 'New Quest', 'summary': 'A playable adventure.',
            'category': 'game', 'status': 'released', 'role': 'Developer',
            'technologies': 'Godot', 'project_url': '', 'thumbnail_url': '',
        }
        self.assertEqual(self.client.get(url).status_code, 405)
        self.assertEqual(self.client.post(url, payload).status_code, 403)
        regular = get_user_model().objects.create_user(username='player')
        self.client.force_login(regular)
        self.assertEqual(self.client.post(url, payload).status_code, 403)

        owner = get_user_model().objects.create_user(username='owner', is_superuser=True)
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(owner)
        self.assertEqual(csrf_client.post(url, payload).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

        self.client.force_login(owner)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()['counts']['total'], 2)
        self.assertTrue(Project.objects.filter(slug='new-quest').exists())

    def test_ajax_create_validates_and_strips_html(self):
        owner = get_user_model().objects.create_user(username='owner', is_superuser=True)
        self.client.force_login(owner)
        url = reverse('main:create_project_ajax')
        payload = {
            'title': '<img src=x onerror=alert(1)>',
            'summary': 'A summary', 'category': 'game', 'status': 'released',
            'role': 'Developer', 'technologies': 'Godot',
        }
        rejected = self.client.post(url, payload)
        self.assertEqual(rejected.status_code, 400)
        self.assertIn('title', rejected.json()['errors'])

        payload['title'] = '<b>Safe Quest</b>'
        payload['summary'] = '<i>Great</i> game'
        created = self.client.post(url, payload)
        self.assertEqual(created.status_code, 201)
        project = Project.objects.get(slug='safe-quest')
        self.assertEqual(project.title, 'Safe Quest')
        self.assertEqual(project.summary, 'Great game')


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
