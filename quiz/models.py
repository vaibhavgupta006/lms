from django.db import models
from course.models import Course
from django.shortcuts import reverse
from authentication.models import User
# from quiz_question.models import Submission as QuizQuestionSubmission
# Create your models here.


class Quiz(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='quizzes'
    )
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.CharField(
        max_length=500,
        blank=False,
        null=False,
        default='No description provided by teacher'
    )
    quiz_date = models.DateField(blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    total_grade = models.IntegerField(default=0, null=False, blank=False)

    def __str__(self):
        return f'course {self.course.id} quiz {self.id}'

    def get_absolute_url(self):
        return reverse(
            'quiz_question:create-quiz-question',
            kwargs={
                'course_type': 'my-courses',
                'course_id': self.course.id,
                'quiz_id': self.id
            }
        )


class Submission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_submissions'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    grade = models.IntegerField(default=0, null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'quiz'),)
