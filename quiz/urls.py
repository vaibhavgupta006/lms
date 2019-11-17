from django.urls import path
from .views import (
    QuizCreationView,
    QuizListView,
    QuizDetailView,
    QuizUpdateView,
)

app_name = 'quiz'
urlpatterns = [
    path('<int:course_id>/quizzes/',
         QuizListView.as_view(), name='all'),

    path('<int:course_id>/quizzes/create/',
         QuizCreationView.as_view(), name='create-quiz'),

    path('<int:course_id>/quizzes/<int:quiz_id>/',
         QuizDetailView.as_view(), name='detail'),

    path('<int:course_id>/quizzes/<int:quiz_id>/update/',
         QuizUpdateView.as_view(), name='update'),

    # path('<int:course_id>/assignments/<int:assignment_id>/submit/',
    #      SubmitView.as_view(), name='upload-solution'),

    # path('<int:course_id>/assignments/<int:assignment_id>/submissions/',
    #      SubmissionView.as_view(), name='submissions'),

    # path('<int:course_id>/assignments/<int:assignment_id>/submissions/all-submissions-pdf',
    #      AllSubmissionPDFView.as_view(), name='all-submissions-pdf'),
]
