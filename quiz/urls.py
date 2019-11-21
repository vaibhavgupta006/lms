from django.urls import path
from .views import (
    QuizCreationView,
    QuizListView,
    QuizDetailView,
    QuizUpdateView,
    QuizSubmissionView,
    ViewSubmissionView,
    SubmissionDetailView
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

    path('<int:course_id>/quizzes/<int:quiz_id>/submit/',
         QuizSubmissionView.as_view(), name='submit-quiz'),

    path('<int:course_id>/quizzes/<int:quiz_id>/submissions/',
         ViewSubmissionView.as_view(), name='submissions'),

    path('<int:course_id>/quizzes/<int:quiz_id>/submissions/<int:submission_id>/detail/',
         SubmissionDetailView.as_view(), name='submission-detail'),
]
