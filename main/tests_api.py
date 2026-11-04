import json
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from main.models import Experience, Project


class PortfolioAPITest(TestCase):
    def setUp(self):
        Project.objects.all().delete()
        Experience.objects.all().delete()
        user_model = get_user_model()
        self.owner = user_model.objects.create_user('owner', password='test-password', is_superuser=True)
        self.editor = user_model.objects.create_user('editor', password='test-password')
        self.regular = user_model.objects.create_user('regular', password='test-password')
        group, _ = Group.objects.get_or_create(name='Editor')
        self.editor.groups.add(group)
        self.project = Project.objects.create(
            title='Cipher Quest', slug='cipher-quest', summary='A security puzzle.',
            category='security', status='prototype', role='Developer',
            technologies='Python, Django', project_url='', thumbnail_url='',
        )
        self.experience = Experience.objects.create(
            title='RISTEK Fasilkom UI', description='Game Development SIG.',
            category='organization',
        )
        self.project_payload = {
            'title': 'New Quest', 'summary': 'A small game.', 'category': 'game',
            'status': 'released', 'role': 'Solo Developer',
            'technologies': 'Godot, Python', 'project_url': '',
            'thumbnail_url': '', 'featured': False,
        }
        self.experience_payload = {
            'title': 'Teaching Assistant', 'description': 'Helped students.',
            'category': 'part-time', 'thumbnail': '', 'ended_at': None,
        }

    def post_json(self, url, data, client=None):
        return (client or self.client).post(url, json.dumps(data), content_type='application/json')

    def patch_json(self, url, data, client=None):
        return (client or self.client).patch(url, json.dumps(data), content_type='application/json')

    def test_public_project_list_search_and_empty_result(self):
        url = reverse('api:project-list')
        response = self.client.get(url, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['title'], self.project.title)
        self.assertEqual(response.json()[0]['technology_list'], ['Python', 'Django'])
        self.assertFalse(response.json()[0]['is_starred'])
        self.assertNotIn('starred_by', response.json()[0])
        self.assertEqual(len(self.client.get(url, {'title': ' CIPHER '}).json()), 1)
        self.assertEqual(self.client.get(url, {'title': 'missing'}).json(), [])

    def test_project_detail_and_unknown_uuid(self):
        url = reverse('api:project-detail', args=[self.project.id])
        self.assertEqual(self.client.get(url).json()['slug'], 'cipher-quest')
        missing = reverse('api:project-detail', args=[uuid.uuid4()])
        self.assertEqual(self.client.get(missing).status_code, 404)

    def test_owner_can_create_project_with_unique_slug_and_read_only_star_fields(self):
        self.client.force_login(self.owner)
        payload = dict(self.project_payload, id=str(uuid.uuid4()), star_count=99, is_starred=True)
        url = reverse('api:project-list')
        first = self.post_json(url, payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(first.json()['slug'], 'new-quest')
        self.assertEqual(first.json()['star_count'], 0)
        self.assertNotEqual(first.json()['id'], payload['id'])
        second = self.post_json(url, payload)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(second.json()['slug'], 'new-quest-2')

    def test_only_owner_can_create_project(self):
        url = reverse('api:project-list')
        self.assertEqual(self.post_json(url, self.project_payload).status_code, 403)
        for user in (self.regular, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.post_json(url, self.project_payload).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_project_serializer_rejects_invalid_input_and_strips_tags(self):
        self.client.force_login(self.owner)
        url = reverse('api:project-list')
        invalid = self.post_json(url, dict(self.project_payload, title='<img src=x onerror=alert(1)>'))
        self.assertEqual(invalid.status_code, 400)
        self.assertIn('title', invalid.json())
        bad_url = self.post_json(url, dict(self.project_payload, project_url='javascript:alert(1)'))
        self.assertEqual(bad_url.status_code, 400)
        self.assertIn('project_url', bad_url.json())
        valid = self.post_json(url, dict(self.project_payload, title='<b>Clean Quest</b>'))
        self.assertEqual(valid.status_code, 201)
        self.assertEqual(valid.json()['title'], 'Clean Quest')

    def test_owner_can_put_patch_and_delete_project(self):
        self.client.force_login(self.owner)
        url = reverse('api:project-detail', args=[self.project.id])
        incomplete = self.client.put(url, json.dumps({'title': 'Only title'}), content_type='application/json')
        self.assertEqual(incomplete.status_code, 400)
        patched = self.patch_json(url, {'title': 'Updated Quest'})
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.json()['summary'], 'A security puzzle.')
        replaced = self.client.put(url, json.dumps(self.project_payload), content_type='application/json')
        self.assertEqual(replaced.status_code, 200)
        self.assertEqual(replaced.json()['title'], 'New Quest')
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_non_owner_cannot_update_or_delete_project(self):
        url = reverse('api:project-detail', args=[self.project.id])
        self.assertEqual(self.patch_json(url, {'title': 'Nope'}).status_code, 403)
        for user in (self.regular, self.editor):
            self.client.force_login(user)
            self.assertEqual(self.patch_json(url, {'title': 'Nope'}).status_code, 403)
            self.assertEqual(self.client.delete(url).status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Cipher Quest')

    def test_project_star_requires_login_and_toggles_current_user(self):
        url = reverse('api:project-star', args=[self.project.id])
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_login(self.regular)
        self.assertEqual(self.client.get(url).status_code, 405)
        first = self.post_json(url, {'user_id': self.owner.id})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()['star_count'], 1)
        self.assertTrue(first.json()['is_starred'])
        self.assertFalse(self.project.starred_by.filter(pk=self.owner.pk).exists())
        self.assertEqual(self.client.post(url).json()['star_count'], 0)

    def test_authenticated_project_mutation_requires_csrf(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)
        url = reverse('api:project-list')
        self.assertEqual(self.post_json(url, self.project_payload, client).status_code, 403)
        client.get(reverse('main:show_projects'))
        token = client.cookies['csrftoken'].value
        response = client.post(
            url, json.dumps(self.project_payload), content_type='application/json',
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 201)

    def test_public_experience_list_filter_and_detail(self):
        url = reverse('api:experience-list')
        self.assertEqual(self.client.get(url).json()[0]['category_display'], 'Organization')
        self.assertEqual(self.client.get(url, {'category': 'research'}).json(), [])
        self.assertEqual(len(self.client.get(url, {'title': 'ristek'}).json()), 1)
        detail = reverse('api:experience-detail', args=[self.experience.id])
        self.assertTrue(self.client.get(detail).json()['is_ongoing'])
        self.assertEqual(self.client.get(reverse('api:experience-detail', args=[uuid.uuid4()])).status_code, 404)

    def test_owner_can_create_experience_and_serializer_cleans_input(self):
        self.client.force_login(self.owner)
        url = reverse('api:experience-list')
        invalid = self.post_json(url, dict(self.experience_payload, title='<img src=x onerror=alert(1)>'))
        self.assertEqual(invalid.status_code, 400)
        self.assertIn('title', invalid.json())
        cleaned = self.post_json(url, dict(self.experience_payload, title='<b>Teaching Assistant</b>'))
        self.assertEqual(cleaned.status_code, 201)
        self.assertEqual(cleaned.json()['title'], 'Teaching Assistant')

    def test_editor_can_patch_experience_but_not_create_or_delete(self):
        list_url = reverse('api:experience-list')
        detail_url = reverse('api:experience-detail', args=[self.experience.id])
        self.assertEqual(self.post_json(list_url, self.experience_payload).status_code, 403)
        self.client.force_login(self.regular)
        self.assertEqual(self.patch_json(detail_url, {'title': 'Nope'}).status_code, 403)
        self.client.force_login(self.editor)
        self.assertEqual(self.post_json(list_url, self.experience_payload).status_code, 403)
        self.assertEqual(self.client.delete(detail_url).status_code, 403)
        patched = self.patch_json(detail_url, {'title': 'Updated RISTEK'})
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.json()['title'], 'Updated RISTEK')
        self.assertEqual(self.client.get(detail_url).status_code, 200)

    def test_owner_can_delete_experience_and_regular_can_star(self):
        star_url = reverse('api:experience-star', args=[self.experience.id])
        self.assertEqual(self.client.post(star_url).status_code, 403)
        self.client.force_login(self.regular)
        self.assertEqual(self.client.post(star_url).json()['star_count'], 1)
        self.assertEqual(self.client.post(star_url).json()['star_count'], 0)
        self.client.force_login(self.owner)
        detail_url = reverse('api:experience-detail', args=[self.experience.id])
        self.assertEqual(self.client.delete(detail_url).status_code, 204)
        self.assertEqual(self.client.get(detail_url).status_code, 404)
