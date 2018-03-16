from django.test import TestCase
from AeroMembersApp.models import *
# Create your tests here.

class ForumThreadTests(TestCase):
	def test_threadreply_can_reply_threads(self):
		thread = Thread(title="Thread Title",content="thread content")
		thread.save()
		threadReply = ThreadReply(content="thread reply content",parent=thread)
		thread.save()
		self.assertIs(threadReply.parent,thread)
		self.assertIs(thread.replies.all(),ThreadReply.objects.all())