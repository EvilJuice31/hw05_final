import time

from django.core import mail
from django.core.files import File
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from .models import Follow, Group, Post, User


class TestStringMethods(TestCase):
    def test_length(self):
        self.assertEqual(len("yatube"), 6)

    #def test_show_msg(self):
        # действительно ли первый аргумент — True?
        #self.assertTrue(False, msg="Важная проверка на истинность")


class TestPost(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='mike', password='12345'
        )

    def test_redirect_new(self):
        """
        Проверка редиректа на страницу аутентефикации не залогиненного пользователя
        """
        response = self.client.get(reverse('new_post'))
        self.assertRedirects(response, '/auth/login/?next=/new/')

    def test_post_create(self):
        self.client.login(username='mike', password='12345')

        #Добавление нового поста с помощью POST запроса.
        response = self.client.post(
            reverse("new_post"), {'text': 'My first post'}, follow=True)
        self.assertEqual(response.status_code, 200)

        #проверка что новый пост добален на главную страницу.
        self.client.get(reverse('index'))
        time.sleep(16)
        resp = self.client.get(reverse('index'))
        self.assertContains(resp, "My first post")

        #проверка что новый пост добален в профиль.
        resp = self.client.post(
            reverse('profile', args=[f'{self.user.username}']))
        self.assertContains(resp, "My first post")

        #Проверка наличия поста по его id.
        resp = self.client.post(
            reverse('post', args=[f'{self.user.username}', '1']))
        self.assertContains(resp, "My first post")

    def test_post_edit(self):
        """
        Проверка корректного редактирования поста.
        """
        self.client.login(username='mike', password='12345')
        

        resp = self.client.post(
            reverse("new_post"), {'text': 'My first post'}, follow=True)
        self.assertEqual(resp.status_code, 200)

        self.client.post(reverse('post_edit', args=['mike', '1']), {
                         'text': 'My second post'}, follow=True)

        #проверка исправленного поста на главной странице.
        time.sleep(16)
        resp = self.client.get(reverse('index'))
        self.assertContains(resp, "My second post")

        #проверка исправленного поста в профиле.
        resp = self.client.post(
            reverse('profile', args=[f'{self.user.username}']))
        self.assertContains(resp, "My second post")

        #Проверка исправленного поста по его id.
        resp = self.client.post(
            reverse('post', args=[f'{self.user.username}', '1']))
        self.assertContains(resp, "My second post")


class EmailTest(TestCase):
    def test_send_email(self):
        self.client = Client()
        user = {
            'username': 'test',
            'password1': 'NOSVDydYJN',
            'password2': 'NOSVDydYJN',
            'email': 'test@ya.ru'
        }
        self.client.post(reverse('signup'), user, follow=True)

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject,
                         'Подтверждение регистрации Yatube')


class Test404(TestCase):
    def test404(self):
        self.addTypeEqualityFuncclient = Client()
        resp = self.client.get('/404/')
        self.assertEqual(resp.status_code, 404)


class TestImg(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='mike', password='12345'
        )
        self.client.login(username='mike', password='12345')
        self.group = Group.objects.create(
            title='cat', slug='cats', description='цитаты о котиках')
        with open('1.jpg', 'rb') as fp:
            self.client.post(
                reverse("new_post"), {'group': 1, 'text': 'My first post', 'image': fp}, follow=True)

    def test_img(self):
        time.sleep(16)
        resp = self.client.get(reverse('index'))
        self.assertIn('img', resp.content.decode())

        #проверка что новый пост добален в профиль.
        resp = self.client.post(
            reverse('profile', args=[f'{self.user.username}']))
        self.assertIn('img', resp.content.decode())

        resp = self.client.post(reverse('slug', args=['cats']))
        #print(resp.content.decode())
        self.assertIn('img', resp.content.decode())


class TestCache(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='mike', password='12345'
        )
        self.client.login(username='mike', password='12345')
        self.client.get(reverse('index'))

        #Добавление нового поста с помощью POST запроса.
        self.client.post(
            reverse("new_post"), {'text': 'My post'}, follow=True)
        self.client.get(reverse('index'))

    def test_notContains(self):
        resp = self.client.get(reverse('index'))
        self.assertNotContains(resp, "My post")


class TestFollow(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='mike', password='12345'
        )
        self.user = User.objects.create_user(
            username='nike', password='12345'
        )
        self.client.login(username='mike', password='12345')
        self.client.get(reverse('index'))
        self.author = get_object_or_404(User, username='nike')
        self.user = get_object_or_404(User, username='mike')

    def test_follow(self):
        self.client.post(reverse('profile_follow', args=['nike']))
        self.assertEqual(
            Follow.objects.filter(user=self.user, author=self.author).exists(), True)

    def test_unfollow(self):
        self.client.post(reverse('profile_unfollow', args=['nike']))
        self.assertEqual(
            Follow.objects.filter(user=self.user, author=self.author).exists(), False)


class TestComment(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='mike', password='12345')
        post_text = 'This my first post'
        self.post = Post.objects.create(text=post_text, author=self.user)

    def test_comment_redirect(self):
        response = self.client.get(reverse('add_comment', args=['mike', '1']))
        self.assertRedirects(response, '/auth/login/?next=/mike/1/comment/')
