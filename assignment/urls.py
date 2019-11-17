from django.urls import path
from .views import (
    CreateAssignmentView,
    AssignmentDetailView,
    #     CreateQuestionView,
    AssignmentListView,
    SubmitView,
    SubmissionView,
    AssignmentUpdateView,
    AllSubmissionPDFView,
    RecentAssignmentView
)


app_name = 'assignment'
urlpatterns = [
    path('recent-assignments/',
         RecentAssignmentView.as_view(), name='recent_assignments'),

    path('<int:course_id>/assignments/',
         AssignmentListView.as_view(), name='all'),

    path('<int:course_id>/assignments/create/',
         CreateAssignmentView.as_view(), name='create-assignment'),

    path('<int:course_id>/assignments/<int:assignment_id>/',
         AssignmentDetailView.as_view(), name='detail'),

    path('<int:course_id>/assignments/<int:assignment_id>/update',
         AssignmentUpdateView.as_view(), name='update'),

    path('<int:course_id>/assignments/<int:assignment_id>/submit/',
         SubmitView.as_view(), name='upload-solution'),

    path('<int:course_id>/assignments/<int:assignment_id>/submissions/',
         SubmissionView.as_view(), name='submissions'),

    path('<int:course_id>/assignments/<int:assignment_id>/submissions/all-submissions-pdf',
         AllSubmissionPDFView.as_view(), name='all-submissions-pdf'),
]
