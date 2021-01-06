
import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User, Follow, Comment
from posts.tests.test_forms import URL_LOGIN

USERNAME_1 = 'testuser'
USERNAME_2 = 'testuser2'
GROUP_TITLE = 'test title post'
GROUP_SLUG = 'test_slug_post'
GROUP_DESCRIPTION = 'test description post'
POST_TEXT = 'test text'

URL_INDEX = reverse('index')
URL_GROUP = reverse('group', args=(GROUP_SLUG,))
URL_NEW_POST = reverse('new_post')
URL_PROFILE_1 = reverse('profile', args=(USERNAME_1,))
URL_FOLLOW_2 = reverse('follow_index')
URL_PROFILE_FOLLOW_2_TO_1 = reverse('profile_follow', args=(USERNAME_1,))
URL_PROFILE_UNFOLLOW_2_FROM_1 = reverse('profile_unfollow', args=(USERNAME_1,))


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(
            username=USERNAME_1,
        )
        cls.user_for_subscription = User.objects.create(
            username=USERNAME_2,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.URL_POST_EDIT = reverse(
            'post_edit',
            args=(USERNAME_1, cls.post.id)
        )
        cls.URL_POST = reverse(
            'post',
            args=(USERNAME_1, cls.post.id)
        )
        cls.URL_ADD_COMMENT = reverse(
            'add_comment',
            args=(USERNAME_1, cls.post.id,)
        )
        cls.URL_COMMENT_REDIRECT = (
            URL_LOGIN +
            '?next=' +
            cls.URL_ADD_COMMENT)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user_for_client = self.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_for_client)
        self.authorized_client_for_subscription = Client()
        self.authorized_client_for_subscription.force_login(
            self.user_for_subscription
        )

    def test_pages_shows_correct_context(self):
        """Страница сформирована с корректным контекстом
        """
        Follow.objects.create( 
            user=self.user_for_subscription, 
            author=self.user_for_client, 
        )
        context_url_names = [
            [URL_INDEX, self.authorized_client],
            [URL_GROUP, self.authorized_client],
            [URL_PROFILE_1, self.authorized_client],
            [self.URL_POST, self.authorized_client],
            [URL_FOLLOW_2, self.authorized_client_for_subscription],
        ]
        for url, client in context_url_names:
            with self.subTest():
                response = client.get(url)
                if 'page' in response.context:
                    post = response.context['page'][0]
                    self.assertTrue(1 == len(response.context['page']))
                else:
                    post = response.context['post']
                self.assertTrue(self.post == post)

    def test_pages_shows_correct_author(self):
        """Контекстная переменная author содержит корректные данные
        """
        context_url_names = [
            URL_PROFILE_1,
            self.URL_POST,
        ]
        for url in context_url_names:
            with self.subTest():
                response = self.authorized_client.get(url)
                author = response.context['author']
                self.assertTrue(self.user == author)

    def test_index_cache(self):
        """Кэширование страницы выполняется корректно
        """
        page_before = self.authorized_client.get(URL_INDEX)
        content_before = page_before.content
        Post.objects.create(
            text='cache',
            author=self.user,
            group=self.group,
        )
        cache_page = self.authorized_client.get(URL_INDEX)
        cache_content = cache_page.content
        cache.clear()
        page_after = self.authorized_client.get(URL_INDEX)
        content_after = page_after.content
        self.assertTrue(content_before == cache_content)
        self.assertFalse(content_before == content_after)

    def test_subscription_works_correctly(self):
        """Новая запись пользователя не появляется в ленте тех, кто не
        подписан на него.
        """
        Follow.objects.create( 
            user=self.user_for_subscription, 
            author=self.user_for_client, 
        )
        response_for_client = self.authorized_client.get(URL_FOLLOW_2)
        context_for_client = response_for_client.context['page']
        self.assertNotIn(self.post, context_for_client)

    def test_subscription_management_is_correct(self):
        """Авторизованный пользователь может подписываться на других
        пользователей
        """
        response_for_follow = self.authorized_client_for_subscription.get(
            URL_PROFILE_FOLLOW_2_TO_1
        )
        follow = Follow.objects.filter(
            user=self.user_for_subscription,
            author=self.user_for_client,
        ).exists()
        self.assertTrue(follow==True)
        self.assertRedirects(response_for_follow, URL_PROFILE_1)

    def test_unsubscribing_works_correctly(self):
        """Авторизованный пользователь может удалять других пользователей из
        подписок
        """
        Follow.objects.create( 
            user=self.user_for_subscription, 
            author=self.user_for_client, 
        )
        response_for_unfollow = self.authorized_client_for_subscription.get(
            URL_PROFILE_UNFOLLOW_2_FROM_1
        )
        unfollow = Follow.objects.filter(
            user=self.user_for_subscription,
            author=self.user_for_client,
        ).exists()
        self.assertFalse(unfollow==True)
        self.assertRedirects(response_for_unfollow, URL_PROFILE_1)

    def test_authorized_client_can_comment(self):
        """Авторизированный пользователь может комментировать посты
        """
        comments = Comment.objects.all()
        comments.delete()
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'comment',
        }
        response_for_client = self.authorized_client_for_subscription.post(
            self.URL_ADD_COMMENT,
            data=form_data,
            follow=True,
        )
        comments_count_after_authorized_client = Comment.objects.count()
        comment = Comment.objects.first()
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user_for_subscription)
        self.assertEqual(comment.post, self.post)
        self.assertTrue(comments_count_after_authorized_client ==
                        comments_count + 1)
        self.assertRedirects(response_for_client, self.URL_POST)

    def test_guest_cannot_comment(self):
        """Неавторизированный пользователь не может комментировать посты
        """
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'comment',
        }
        response_for_guest = self.guest_client.post(
            self.URL_ADD_COMMENT,
            data=form_data,
            follow=True,
        )
        comments_count_after_guest_client = Comment.objects.count()
        self.assertTrue(comments_count ==
                        comments_count_after_guest_client)
        self.assertRedirects(response_for_guest, self.URL_COMMENT_REDIRECT)
