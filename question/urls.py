from django.urls import path

from .views import (
    CreateAssignmentQuestionView,
)


app_name = 'question'
urlpatterns = [
    path('<int:course_id>/assignments/<int:assignment_id>/add-question/',
         CreateAssignmentQuestionView.as_view(), name='create-assignment-question'),

    # path('<int:course_id>/assignments/<int:assignment_id>/submit/',
    #      SubmitView.as_view(), name='upload-solution'),
]
