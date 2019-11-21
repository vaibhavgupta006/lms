from django.db import models
from course.models import Course
from django.urls import reverse
from authentication.models import User


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


# class Submission(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='assignment_submissions'
#     )
#     assignment = models.ForeignKey(
#         Assignment,
#         on_delete=models.CASCADE,
#         related_name='submissions'
#     )
#     date_created = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = (('user', 'assignment'),)
