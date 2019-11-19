from django.test import SimpleTestCase
from course.views import CourseDetailView
from django.urls import reverse, resolve


class TestUrls(SimpleTestCase):

    def test_course_detail_url_is_resolved(self):
        for id in range(100):
            for course_type in ['none', 'my-courses', 'enrolled-courses']:
                url = reverse(
                    'course:detail',
                    kwargs={
                        "course_type": course_type,
                        'id': id
                    }
                )
                self.assertEquals(
                    resolve(url).func.view_class,
                    CourseDetailView
                )
