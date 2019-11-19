from quiz.models import Quiz
from .models import Question
from django.forms import inlineformset_factory, formset_factory

from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect

from django.views.generic import (
    FormView
)

from .forms import (
    QuestionCreationForm,
    QuestionCreationFormset,
    QuestionMediaForm,
    # UploadSolutionForm,
    # UploadSolutionFormset
)

# Create your views here.


class CreateQuestionView(FormView):
    template_name = 'quiz_question/create_questions.html'

    def get_instance(self, request=None):
        request = self.request if request is None else request
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')

        try:
            course = request.user.hosted_courses.get(id=course_id)
            quiz = course.quizzes.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Http404

        return quiz

    def get_form(self):
        FormSet = inlineformset_factory(
            Quiz, Question,
            form=QuestionCreationForm,
            extra=1,
            can_delete=False,
            formset=QuestionCreationFormset
        )
        form = FormSet(
            self.request.POST or None,
            self.request.FILES or None,
            instance=self.get_instance()
        )
        return form

    def form_valid(self, formset):
        formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['formset'] = kwargs.pop('form')
        kwargs['course_id'] = self.kwargs.get('course_id')
        kwargs['quiz_id'] = self.kwargs.get('quiz_id')
        return kwargs

    def get_success_url(self, *args, **kwargs):
        course_id = self.kwargs.get("course_id")
        course_type = self.kwargs.get('course_type')
        quiz_id = self.kwargs.get('quiz_id')
        kwargs = {
            "course_id": course_id,
            'course_type': course_type,
            'quiz_id': quiz_id
        }
        return reverse_lazy('quiz:detail', kwargs=kwargs)
