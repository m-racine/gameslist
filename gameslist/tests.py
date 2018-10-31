# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.shortcuts import reverse
# Create your tests here.

#class GameModelTests(TestCase):
#Currently no functions within the model definition
# class QuestionModelTests(TestCase):

#     def test_was_published_recently_with_future_question(self):
#         """
#         was_published_recently() returns False for questions whose pub_date
#         is in the future.
#         """
#         time = timezone.now() + datetime.timedelta(days=30)
#         future_question = Question(pub_date=time)
#         self.assertIs(future_question.was_published_recently(), False)

#     def test_was_published_recently_with_old_question(self):
#         """
#         was_published_recently() returns False for questions whose pub_date
#         is older than 1 day.
#         """
#         time = timezone.now() - datetime.timedelta(days=1, seconds=1)
#         old_question = Question(pub_date=time)
#         self.assertIs(old_question.was_published_recently(), False)

#     def test_was_published_recently_with_recent_question(self):
#         """
#         was_published_recently() returns True for questions whose pub_date
#         is within the last day.
#         """
#         time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
#         recent_question = Question(pub_date=time)
#         self.assertIs(recent_question.was_published_recently(), True)

# def create_question(question_text, days):
#     """
#     Create a question with the given `question_text` and published the
#     given number of `days` offset to now (negative for questions published
#     in the past, positive for questions that have yet to be published).
#     """
#     time = timezone.now() + datetime.timedelta(days=days)
#     return Question.objects.create(question_text=question_text, pub_date=time)

#def create_game():
    

#class WishModelTests(TestCase):

class GameIndexViewTests(TestCase):
    def test_no_games(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available.")
        self.assertQuerysetEqual(response.context['new_games_list'], [])

    # def test_purchased_game(self):
    #     """
    #     Games with a purchase_date in the past are displayed on the
    #     index page.
    #     """
    #     #create_game(question_text="Purchased game.", days=-30)
    #     response = self.client.get(reverse('gameslist:index'))
    #     self.assertQuerysetEqual(
    #         response.context['new_games_list'],
    #         ['<Game: Purchased Game.>']
    #     )

#     def test_future_question(self):
#         """
#         Questions with a pub_date in the future aren't displayed on
#         the index page.
#         """
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse('polls:index'))
#         self.assertContains(response, "No polls are available.")
#         self.assertQuerysetEqual(response.context['latest_question_list'], [])

#     def test_future_question_and_past_question(self):
#         """
#         Even if both past and future questions exist, only past questions
#         are displayed.
#         """
#         create_question(question_text="Past question.", days=-30)
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse('polls:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             ['<Question: Past question.>']
#         )

#     def test_two_past_questions(self):
#         """
#         The questions index page may display multiple questions.
#         """
#         create_question(question_text="Past question 1.", days=-30)
#         create_question(question_text="Past question 2.", days=-5)
#         response = self.client.get(reverse('polls:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             ['<Question: Past question 2.>', '<Question: Past question 1.>']
#         )

#class GameDetailViewTests(TestCase):
# class QuestionDetailViewTests(TestCase):
#     def test_future_question(self):
#         """
#         The detail view of a question with a pub_date in the future
#         returns a 404 not found.
#         """
#         future_question = create_question(question_text='Future question.', days=5)
#         url = reverse('polls:detail', args=(future_question.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)

#     def test_past_question(self):
#         """
#         The detail view of a question with a pub_date in the past
#         displays the question's text.
#         """
#         past_question = create_question(question_text='Past Question.', days=-5)
#         url = reverse('polls:detail', args=(past_question.id,))
#         response = self.client.get(url)
#         self.assertContains(response, past_question.question_text)

#Ok, so obv. needed tests
#adding a new game
#modifying an existing game
#beating a game
#abandoning a game
#metacritic fetch- a few variants
#aging calculations
#priority calculations
#aging 0 when beaten/abandoned?
#current time fetches?
#logging time
#fetching current time (steam?)
#deleting a game
#lending a game
#recommend a game (check priroity)
#pass over a game
#searching for types of games (lots of tests of different searchs)
    #ie, by platform, by played, by recommended etc

#ratings
#rate a as better than b
#rate a as more desireed (wl) than b
#check priorities based on that
#make sure only grabs 5 paris to compare
#check grabs valid pairs to compare
#what are the comparison rules:
  #less  ratings > more ratings 
  # for owned: beaten > played > unplayed > abandoned
  #for owned: 
  #for wished: older > newer

#humble wishlist fetch
#itch wishlist fetch
#gog wishlist fetch
#steam wishlist fetch
#discount comparisons?

#probably many many more in the end