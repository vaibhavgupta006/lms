from django.db import models
from authentication.models import User
from django.urls import reverse_lazy
import os
# Create your models here.


def get_upload_location(instance, filename):
    return os.path.join(
        os.path.join(
            'courses', f'course_{instance.id}'
        ),
        filename
    )


class Course(models.Model):
    tutor = models.ForeignKey(
        User, on_delete=models.CASCADE, null=False, related_name='hosted_courses'
    )
    name = models.CharField(
        max_length=50, blank=False,
        null=False, unique=True
    )
    description = models.CharField(
        max_length=1000,
        default='No description provide by teacher'
    )
    image = models.ImageField(
        null=False,
        blank=False,
        upload_to=get_upload_location
    )

    def get_absolute_url(self):
        return reverse_lazy('course:detail', kwargs={"id": self.id, 'course_type': 'my-courses'})

    def __str__(self):
        return f"course {self.id}"


class EnrolledCourse(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrolled_courses'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='students'
    )

    def __str__(self):
        return f"{self.user.username} enrolled in course {self.course.id}"
