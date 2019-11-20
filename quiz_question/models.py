from django.db import models
from quiz.models import Quiz
from authentication.models import User

import os

# Create your models here.


def get_question_media_location(instance, filename):
    print(instance.question.id)
    return os.path.join(
        'quix_questions',
        os.path.join(f'question_{instance.question.id}', filename)
    )


class Question(models.Model):
    question = models.CharField(max_length=1000, blank=False, null=False)
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='questions')
    grade = models.IntegerField(null=False, default=1)

    def __str__(self):
        return f'quiz {self.quiz.id} question {self.id}'


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.CharField(max_length=500, blank=False, null=False)
    correct_choice = models.BooleanField(default=False)

    def __str__(self):
        return f'question {self.question.id} option {self.id}'


class Media(models.Model):
    name = models.CharField(null=True, max_length=30, blank=True)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='media'
    )
    file = models.FileField(
        upload_to=get_question_media_location, null=True, blank=True
    )


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_selected = models.ForeignKey(
        Option, on_delete=models.CASCADE, null=True
    )
