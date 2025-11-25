import os
import tempfile
import shutil

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import User, Role


class UsersAPITest(TestCase):
    def setUp(self):
        self._old_media_root = settings.MEDIA_ROOT
        self.tmp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.tmp_media

        self.role = Role.objects.create(name='Officer', description='Test role')

        image_content = b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4C\x01\x00\x3B"
        uploaded = SimpleUploadedFile('avatar.gif', image_content, content_type='image/gif')

        self.user = User.objects.create(
            name='Test User',
            email='test.user@example.com',
            password_hash='noop',
            status='Active',
            role=self.role,
        )
        self.user.picture.save('avatar.gif', uploaded, save=True)

        self.client = APIClient()

    def tearDown(self):
        settings.MEDIA_ROOT = self._old_media_root
        try:
            shutil.rmtree(self.tmp_media)
        except Exception:
            pass

    def test_users_list_contains_status_and_absolute_picture(self):
        resp = self.client.get('/users/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        users = data.get('data')
        self.assertIsInstance(users, list)
        self.assertGreaterEqual(len(users), 1)

        user_data = None
        for u in users:
            if u.get('email') == self.user.email:
                user_data = u
                break

        self.assertIsNotNone(user_data, 'Created user not found in response')
        self.assertIn('status', user_data)
        self.assertEqual(user_data.get('status'), 'Active')

        picture = user_data.get('picture')
        self.assertIsNotNone(picture)
        self.assertTrue(picture.startswith('http://testserver'))
        self.assertIn('/media/', picture)

    def test_patch_user_status(self):
        url = f'/users/{self.user.id}/'
        resp = self.client.patch(url, {'status': 'Inactive'}, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        updated = data.get('data')
        self.assertEqual(updated.get('status'), 'Inactive')

        self.user.refresh_from_db()
        self.assertEqual(self.user.status, 'Inactive')
