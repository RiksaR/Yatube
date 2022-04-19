from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User
from posts.tests.test_forms import URL_LOGIN

USERNAME_1 = 'testuser'
USERNAME_2 = 'testuser2'
USERNAME_3 = 'otheruser'
GROUP_TITLE = 'test title post'
GROUP_SLUG = 'test_slug_post'
GROUP_SLUG_STATUS_404 = 'test_slug_pos'
GROUP_DESCRIPTION = 'test description post'
POST_TEXT = 'test text'

URL_INDEX = reverse('index')
URL_GROUP = reverse('group', args=(GROUP_SLUG,))
URL_STATUS_404 = reverse('group', args=(GROUP_SLUG_STATUS_404,))
URL_NEW_POST = reverse('new_post')
URL_FOLLOW = reverse('follow_index')
URL_PROFILE_1 = reverse('profile', args=(USERNAME_1,))
URL_NEW_POST_REDIRECT = (URL_LOGIN + '?next=' + URL_NEW_POST)
URL_FOLLOW_REDIRECT = (URL_LOGIN + '?next=' + URL_FOLLOW)


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=USERNAME_1,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post_1 = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            text=POST_TEXT,
            author=User.objects.create(username=USERNAME_2),
            group=cls.group,
        )
        cls.URL_POST_EDIT_1 = reverse(
            'post_edit',
            args=(USERNAME_1, cls.post_1.id)
        )
        cls.URL_POST_1 = reverse(
            'post',
            args=(USERNAME_1, cls.post_1.id)
        )
        cls.URL_POST_REDIRECT_2 = reverse('post', args=(
            USERNAME_2,
            cls.post_2.id
            )
        )
        cls.URL_POST_EDIT_REDIRECT_2 = reverse(
            'post_edit', args=(
                USERNAME_2,
                cls.post_2.id
            )
        )
        cls.URL_OTHER_USER_3 = reverse(
            'post_edit',
            args=(USERNAME_3, cls.post_1.id)
        )
        cls.URL_OTHER_USER_REDIRECT_3 = (
            URL_LOGIN +
            '?next=' +
            cls.URL_OTHER_USER_3
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_client = self.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_client)

    def test_urls_exists_at_desired_location(self):
        """Страница по заданному адресу возвращает ожидаемый status_code
        """
        expected_status_code = [
            [URL_INDEX, 200, self.guest_client],
            [URL_GROUP, 200, self.guest_client],
            [URL_NEW_POST, 302, self.guest_client],
            [URL_PROFILE_1, 200, self.guest_client],
            [URL_FOLLOW, 302, self.guest_client],
            [self.URL_POST_1, 200, self.guest_client],
            [self.URL_POST_EDIT_1, 302, self.guest_client],
            [URL_STATUS_404, 404, self.guest_client],
            [URL_INDEX, 200, self.authorized_client],
            [URL_GROUP, 200, self.authorized_client],
            [URL_NEW_POST, 200, self.authorized_client],
            [URL_PROFILE_1, 200, self.authorized_client],
            [URL_FOLLOW, 200, self.authorized_client],
            [self.URL_POST_1, 200, self.authorized_client],
            [self.URL_POST_EDIT_1, 200, self.authorized_client],
            [URL_STATUS_404, 404, self.authorized_client],
        ]
        for url, status_code, client in expected_status_code:
            with self.subTest():
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон
        """
        templates_url_names = {
            URL_INDEX: 'index.html',
            URL_GROUP: 'group.html',
            URL_NEW_POST: 'new.html',
            self.URL_POST_EDIT_1: 'new.html',
            self.URL_POST_1: 'post.html',
            URL_PROFILE_1: 'profile.html',
            URL_FOLLOW: 'follow.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Redirect корректно срабатывает для авторизованного
        и неавторизованного пользователя
        """
        expected_redirect = [
            [
                URL_NEW_POST,
                URL_NEW_POST_REDIRECT,
                self.guest_client
            ],
            [
                self.URL_OTHER_USER_3,
                self.URL_OTHER_USER_REDIRECT_3,
                self.guest_client,
            ],
            [
                self.URL_POST_EDIT_REDIRECT_2,
                self.URL_POST_REDIRECT_2,
                self.authorized_client,
            ],
            [
                URL_FOLLOW,
                URL_FOLLOW_REDIRECT,
                self.guest_client
            ],
        ]
        for url, redirect, client in expected_redirect:
            with self.subTest():
                response = client.get(url, follow=True)
                self.assertRedirects(
                    response, redirect)
