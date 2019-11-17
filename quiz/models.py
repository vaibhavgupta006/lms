from django.db import models
from course.models import Course
from django.shortcuts import reverse
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

    def __str__(self):
        return f'course {self.course.id} quiz {self.id}'

    # def get_absolute_url(self):
    #     return reverse("model_detail", kwargs={"pk": self.pk})
