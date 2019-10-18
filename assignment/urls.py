from django.urls import path
from .views import (
    CreateAssignmentView,
    AssignmentDetailView,
    CreateQuestionView,
    AssignmentListView,
    SubmitView
)


app_name = 'assignment'
urlpatterns = [
    path('<int:course_id>/assignments/',
         AssignmentListView.as_view(), name='all'),

    path('<int:course_id>/assignments/create/',
         CreateAssignmentView.as_view(), name='create-assignment'),

    path('<int:course_id>/assignments/<int:assignment_id>/',
         AssignmentDetailView.as_view(), name='detail'),

    path('<int:course_id>/assignments/<int:assignment_id>/add-question/',
         CreateQuestionView.as_view(), name='create-question'),

    path('<int:course_id>/assignments/<int:assignment_id>/submit/',
         SubmitView.as_view(), name='upload-solution'),
]
