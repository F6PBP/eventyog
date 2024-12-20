from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from modules.main.models import Forum, ForumReply, UserProfile
from django.utils import timezone

class YogforumViewsTest(TestCase):

    def setUp(self):
        # Initialize test user and client
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')

        # Create a forum post and reply for testing
        self.forum_post = Forum.objects.create(title='Test Post', content='Test content', user=self.user_profile)
        self.forum_reply = ForumReply.objects.create(forum=self.forum_post, content='Test reply', user=self.user_profile)

    def test_like_post(self):
        response = self.client.post(reverse('yogforum:like_post', args=[self.forum_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('liked'))
        self.assertEqual(response.json().get('total_likes'), 1)

    def test_dislike_post(self):
        response = self.client.post(reverse('yogforum:dislike_post', args=[self.forum_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('disliked'))
        self.assertEqual(response.json().get('total_dislikes'), 1)

    def test_like_reply(self):
        response = self.client.post(reverse('yogforum:like_reply', args=[self.forum_reply.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('liked'))
        self.assertEqual(response.json().get('total_likes'), 1)

    def test_dislike_reply(self):
        response = self.client.post(reverse('yogforum:dislike_reply', args=[self.forum_reply.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('disliked'))
        self.assertEqual(response.json().get('total_dislikes'), 1)

    def test_viewforum(self):
        response = self.client.get(reverse('yogforum:viewforum', args=[self.forum_post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'viewforum.html')  # Use the actual template used in your project
        self.assertContains(response, self.forum_post.title)


    def test_add_post(self):
        response = self.client.post(reverse('yogforum:add_post'), {'title': 'New Post', 'content': 'New Content'})
        self.assertEqual(response.status_code, 302)  # Redirects after successful post creation

    def test_delete_post(self):
        response = self.client.post(reverse('yogforum:delete_post', args=[self.forum_post.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Forum.objects.filter(id=self.forum_post.id).exists())

    def test_add_reply(self):
        response = self.client.post(reverse('yogforum:add_reply', args=[self.forum_post.id]), {'content': 'Another reply'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ForumReply.objects.filter(content='Another reply').exists())

    def test_delete_reply(self):
        response = self.client.post(reverse('yogforum:delete_reply', args=[self.forum_reply.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ForumReply.objects.filter(id=self.forum_reply.id).exists())

    def test_view_reply_as_post(self):
        response = self.client.get(reverse('yogforum:view_reply_as_post', args=[self.forum_reply.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'components/view_reply_as_post.html')
        self.assertContains(response, self.forum_reply.content)

    def test_forum_detail_json(self):
        response = self.client.get(reverse('yogforum:forum_detail_json', args=[self.forum_post.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], self.forum_post.title)
        self.assertEqual(data['total_likes'], self.forum_post.totalLike())