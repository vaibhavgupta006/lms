from django.urls import path
from django.conf.urls import url
from .views import (
    CourseCreateView,
    CourseDetailView,
    CourseListView,
    CourseUpdateView,
    enrollView,
    unenrollView,
)


app_name = 'course'
urlpatterns = [
    url(
        r'^(?P<course_type>(all|my-courses|enrolled-courses))/$',
        CourseListView.as_view(), name='list'
    ),

    path(
        'all/<int:course_id>/enroll/',
        enrollView, name='enroll'
    ),

    path(
        'enrolled-courses/<int:course_id>/unenroll/',
        unenrollView, name='unenroll'
    ),

    path('create/', CourseCreateView.as_view(), name='create'),

    url(
        r'(?P<course_type>(all|my-courses|enrolled-courses))/(?P<id>\d+)/$',
        CourseDetailView.as_view(),
        name='detail'
    ),

    path(
        'my-courses/<int:course_id>/update/',
        CourseUpdateView.as_view(),
        name="update"
    )
]
