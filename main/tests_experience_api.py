"""API tests for the Experience section (Individual Assignment 6).

Each role from Assignment 4 is covered: visitor, regular user, Editor, and
portfolio owner (superuser). Denial tests also check the database so a 403
cannot hide a write that already happened.
"""

import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITestCase(APITestCase):
    password = 'test-password-123'

    def setUp(self):
        # Migration seeds portfolio data; start every test from a known state.
        Experience.objects.all().delete()
        User = get_user_model()
        self.owner = User.objects.create_superuser('owner', password=self.password)
        self.editor = User.objects.create_user('editor', password=self.password)
        self.regular = User.objects.create_user('regular', password=self.password)
        editor_group, _ = Group.objects.get_or_create(name='Editor')
        self.editor.groups.add(editor_group)

        self.experience = Experience.objects.create(
            title='RISTEK Fasilkom UI',
            description='Game Development SIG.',
            category='organization',
        )
        self.list_url = reverse('api:experience-list')
        self.detail_url = reverse('api:experience-detail', args=[self.experience.id])
        self.star_url = reverse('api:experience-star', args=[self.experience.id])
        self.payload = {
            'title': 'Teaching Assistant',
            'description': 'Helped students in lab sessions.',
            'category': 'part-time',
            'thumbnail': '',
            'ended_at': None,
        }

    def as_user(self, user):
        self.client.force_authenticate(user=user)

    def refresh(self):
        self.experience.refresh_from_db()
        return self.experience


class ExperienceReadAndSearchTests(ExperienceAPITestCase):
    def test_visitor_can_read_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data['title'], 'RISTEK Fasilkom UI')
        self.assertTrue(detail.data['is_ongoing'])

    def test_search_uses_query_parameters(self):
        Experience.objects.create(title='BEM Fasilkom UI', description='Staff.', category='organization')
        Experience.objects.create(title='Research Lab', description='Data.', category='research')
        titles = [item['title'] for item in self.client.get(self.list_url, {'title': 'fasilkom'}).data]
        self.assertCountEqual(titles, ['RISTEK Fasilkom UI', 'BEM Fasilkom UI'])
        research = self.client.get(self.list_url, {'category': 'research'}).data
        self.assertEqual([item['title'] for item in research], ['Research Lab'])
        self.assertEqual(self.client.get(self.list_url, {'title': 'tidak-ada'}).data, [])

    def test_unknown_experience_returns_404(self):
        response = self.client.get(reverse('api:experience-detail', args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_star_fields_are_read_only_and_no_sensitive_user_data(self):
        self.experience.starred_by.add(self.regular)
        self.as_user(self.regular)
        data = self.client.get(self.detail_url).data
        self.assertEqual(data['star_count'], 1)
        self.assertTrue(data['is_starred'])
        for field in ('email', 'password', 'starred_by'):
            self.assertNotIn(field, data)

        self.as_user(self.owner)
        response = self.client.patch(self.detail_url, {'star_count': 99, 'is_starred': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.refresh().starred_by.count(), 1)


class ExperienceRolePermissionTests(ExperienceAPITestCase):
    def assert_write_denied(self, expected_status):
        create = self.client.post(self.list_url, self.payload, format='json')
        patch = self.client.patch(self.detail_url, {'title': 'Hacked'}, format='json')
        put = self.client.put(self.detail_url, self.payload, format='json')
        delete = self.client.delete(self.detail_url)
        for response in (create, patch, put, delete):
            self.assertEqual(response.status_code, expected_status)
        # Database must be unchanged after every denied request.
        self.assertEqual(Experience.objects.count(), 1)
        self.assertFalse(Experience.objects.filter(title='Teaching Assistant').exists())
        self.assertEqual(self.refresh().title, 'RISTEK Fasilkom UI')

    def test_visitor_cannot_write(self):
        self.assert_write_denied(status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_write(self):
        self.as_user(self.regular)
        self.assert_write_denied(status.HTTP_403_FORBIDDEN)

    def test_editor_can_patch_and_put(self):
        self.as_user(self.editor)
        patched = self.client.patch(self.detail_url, {'title': 'RISTEK Game Dev'}, format='json')
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(self.refresh().title, 'RISTEK Game Dev')
        self.assertEqual(self.experience.description, 'Game Development SIG.')

        put = self.client.put(self.detail_url, self.payload, format='json')
        self.assertEqual(put.status_code, status.HTTP_200_OK)
        self.assertEqual(self.refresh().title, 'Teaching Assistant')
        self.assertEqual(self.experience.category, 'part-time')

    def test_editor_cannot_create_or_delete(self):
        self.as_user(self.editor)
        create = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(create.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Experience.objects.filter(title='Teaching Assistant').exists())

        delete = self.client.delete(self.detail_url)
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_owner_can_create_update_and_delete(self):
        self.as_user(self.owner)
        create = self.client.post(self.list_url, self.payload, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=create.data['id'])
        self.assertEqual(created.title, 'Teaching Assistant')

        patch = self.client.patch(self.detail_url, {'category': 'volunteer'}, format='json')
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(self.refresh().category, 'volunteer')

        delete = self.client.delete(self.detail_url)
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_owner_gets_404_for_unknown_experience(self):
        self.as_user(self.owner)
        missing = reverse('api:experience-detail', args=[uuid.uuid4()])
        self.assertEqual(self.client.patch(missing, {'title': 'X'}, format='json').status_code, 404)
        self.assertEqual(self.client.delete(missing).status_code, 404)


class ExperienceValidationTests(ExperienceAPITestCase):
    def test_html_is_stripped_from_text_fields(self):
        self.as_user(self.owner)
        response = self.client.post(self.list_url, dict(
            self.payload,
            title='<b>Teaching</b> Assistant',
            description='<script>alert(1)</script>Helped students.',
        ), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        saved = Experience.objects.get(pk=response.data['id'])
        self.assertEqual(saved.title, 'Teaching Assistant')
        self.assertNotIn('<script>', saved.description)

    def test_tag_only_or_missing_title_is_rejected(self):
        self.as_user(self.owner)
        tag_only = self.client.post(self.list_url, dict(self.payload, title='<img src=x onerror=alert(1)>'), format='json')
        self.assertEqual(tag_only.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', tag_only.data)
        missing = self.client.post(self.list_url, {'description': 'No title.'}, format='json')
        self.assertEqual(missing.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', missing.data)
        self.assertEqual(Experience.objects.count(), 1)

    def test_invalid_category_and_url_are_rejected(self):
        self.as_user(self.editor)
        response = self.client.patch(self.detail_url, {'category': 'astronaut', 'thumbnail': 'not-a-url'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category', response.data)
        self.assertIn('thumbnail', response.data)
        self.assertEqual(self.refresh().category, 'organization')

    def test_patch_with_blank_description_is_rejected(self):
        self.as_user(self.editor)
        response = self.client.patch(self.detail_url, {'description': '<p></p>'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.refresh().description, 'Game Development SIG.')


class ExperienceStarTests(ExperienceAPITestCase):
    def test_visitor_cannot_star(self):
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_regular_user_can_star_and_unstar(self):
        self.as_user(self.regular)
        first = self.client.post(self.star_url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual((first.data['star_count'], first.data['is_starred']), (1, True))
        self.assertTrue(self.experience.starred_by.filter(pk=self.regular.pk).exists())
        second = self.client.post(self.star_url)
        self.assertEqual((second.data['star_count'], second.data['is_starred']), (0, False))
        self.assertFalse(self.experience.starred_by.exists())

    def test_star_always_uses_request_user(self):
        self.as_user(self.regular)
        self.client.post(self.star_url, {'user': self.owner.pk, 'starred_by': [self.owner.pk]}, format='json')
        self.assertEqual(list(self.experience.starred_by.all()), [self.regular])

    def test_star_counts_each_user_once(self):
        for user in (self.regular, self.editor):
            self.as_user(user)
            self.client.post(self.star_url)
        self.as_user(self.owner)
        data = self.client.get(self.detail_url).data
        self.assertEqual((data['star_count'], data['is_starred']), (2, False))

    def test_star_unknown_experience_returns_404(self):
        self.as_user(self.regular)
        response = self.client.post(reverse('api:experience-star', args=[uuid.uuid4()]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ExperienceCSRFTests(ExperienceAPITestCase):
    """force_authenticate skips CSRF, so these tests log in through a real session."""

    def setUp(self):
        super().setUp()
        self.csrf_client = APIClient(enforce_csrf_checks=True)

    def csrf_token(self):
        self.csrf_client.get(reverse('main:show_experience'))
        return self.csrf_client.cookies['csrftoken'].value

    def test_owner_request_without_csrf_token_is_rejected(self):
        self.assertTrue(self.csrf_client.login(username='owner', password=self.password))
        response = self.csrf_client.post(self.list_url, self.payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('CSRF', str(response.data['detail']))
        self.assertFalse(Experience.objects.filter(title='Teaching Assistant').exists())

        response = self.csrf_client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_owner_request_with_csrf_token_succeeds(self):
        self.assertTrue(self.csrf_client.login(username='owner', password=self.password))
        response = self.csrf_client.post(
            self.list_url, self.payload, format='json', HTTP_X_CSRFTOKEN=self.csrf_token(),
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_star_without_csrf_token_is_rejected(self):
        self.assertTrue(self.csrf_client.login(username='regular', password=self.password))
        self.assertEqual(self.csrf_client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)
        ok = self.csrf_client.post(self.star_url, HTTP_X_CSRFTOKEN=self.csrf_token())
        self.assertEqual(ok.status_code, status.HTTP_200_OK)
        self.assertEqual(self.experience.starred_by.count(), 1)


class ExperiencePageTests(ExperienceAPITestCase):
    def test_page_points_to_api_and_sets_csrf_cookie(self):
        self.client.force_login(self.regular)
        response = self.client.get(reverse('main:show_experience'))
        self.assertContains(response, self.list_url)
        self.assertIn('csrftoken', response.cookies)
        self.assertNotContains(response, 'id="experience-form-modal"')

    def test_editor_gets_edit_modal_but_no_add_button(self):
        self.client.force_login(self.editor)
        response = self.client.get(reverse('main:show_experience'))
        self.assertContains(response, 'id="experience-form-modal"')
        self.assertContains(response, 'data-can-edit="true"')
        self.assertNotContains(response, 'id="open-add-experience"')

    def test_owner_gets_add_button_and_modal(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('main:show_experience'))
        self.assertContains(response, 'id="open-add-experience"')
        self.assertContains(response, 'id="experience-form-modal"')
