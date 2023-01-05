import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Question


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = Question(question_text="Quién es el mejor programador?")

    def test_was_published_recently_with_future_questions(self):
        """was_published_recently"""
        time = timezone.now() + datetime.timedelta(days=30)
        self.question.pub_date = time
        self.assertIs(self.question.was_published_recently(), False)

    def test_was_published_recently_with_present_questions(self):
        time = timezone.now()
        self.question.pub_date = time
        self.assertIs(self.question.was_published_recently(), True)

    def test_was_published_recently_with_past_questions(self):
        time = timezone.now() - datetime.timedelta(days=3)
        self.question.pub_date = time
        self.assertIs(self.question.was_published_recently(), False)


def create_question(text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse("polls:index"))

    def test_no_questions(self):
        """If no question exist, show a message"""
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, "No polls are available")
        self.assertQuerysetEqual(self.response.context["latest_question_list"], [])

    def test_future_questions(self):
        create_question("future question", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(self.response, "No polls are available")
        self.assertQuerysetEqual(self.response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """"Test adding future questions and past questions, only past questions must be showed"""
        question_future = create_question("future question", 30)
        question_past = create_question("past question", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question_past])

    def test_two_past_question(self):
        """display multiple questions"""
        question_past_a = create_question("past question A", -30)
        question_past_b = create_question("past question B", -40)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question_past_a, question_past_b])


class QuestionDetailViewTest(TestCase):
    def test_future_question(self):
        """Detail view of a question with a date of pub in the future returns 404 not found"""
        question_future = create_question("future question", 30)
        url = reverse("polls:detail", args=(question_future.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """Display question if pub date is in the past"""
        question_past = create_question("past question", -30)
        url = reverse("polls:detail", args=(question_past.id,))
        response = self.client.get(url)
        self.assertContains(response, question_past.question_text)
