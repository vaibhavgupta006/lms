from django.db import models
from course.models import Course
from django.urls import reverse
from authentication.models import User
import os


# Create your models here.


class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='assignments')
    name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(
        max_length=500,
        null=False,
        blank=False,
        default='no description provided by tutor',
    )
    deadline = models.DateField(null=False, blank=False)
    date_created = models.DateTimeField(null=False, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('assignment:create-question', kwargs={
            "course_id": self.course.id,
            "assignment_id": self.id,
            "course_type": "my-courses"
        })

    def __str__(self):
        return f'course {self.course.id} assignment: {self.id}'


class Question(models.Model):
    question = models.CharField(max_length=1000, blank=False, null=False)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return f'assignment {self.assignment.id} question {self.id}'


def get_upload_location(instance, filename):
    assignment_name = f"assignment_{instance.question.assignment.id}"
    course_name = f"course_{instance.question.assignment.course.id}"
    return os.path.join(os.path.join(assignment_name, course_name), filename)


class Submission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='all_submissions'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    solution = models.FileField(
        upload_to=get_upload_location,
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return f"solution to question {self.question.id} by {self.user.username}"
