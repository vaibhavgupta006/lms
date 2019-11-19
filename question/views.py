from assignment.models import Assignment
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
    UploadSolutionForm,
    UploadSolutionFormset
)


# Create your views here.


class CreateQuestionView(FormView):
    template_name = 'assignment/create_questions.html'

    def get_instance(self, request=None):
        request = self.request if request is None else request
        courseId = self.kwargs.get('course_id')
        assignmentId = self.kwargs.get('assignment_id')

        try:
            course = request.user.hosted_courses.get(id=courseId)
            assignment = course.assignments.get(id=assignmentId)
        except ObjectDoesNotExist:
            raise Http404

        return assignment

    def get_form(self):
        FormSet = inlineformset_factory(
            Assignment, Question,
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
        kwargs['assignment_id'] = self.kwargs.get('assignment_id')
        return kwargs

    def get_success_url(self, *args, **kwargs):
        course_id = self.kwargs.get("course_id")
        course_type = self.kwargs.get('course_type')
        assignment_id = self.kwargs.get('assignment_id')
        kwargs = {
            "course_id": course_id,
            'course_type': course_type,
            'assignment_id': assignment_id
        }
        return reverse_lazy('assignment:detail', kwargs=kwargs)


# class SubmitView(FormView):
#     template_name = 'assignment/upload_solution.html'

#     def get(self, request, *args, **kwargs):
#         assignment_id = self.kwargs.get('assignment_id')
#         assignment = Assignment.objects.get(id=assignment_id)
#         if datetime.now().date() > assignment.deadline:
#             return HttpResponseRedirect(
#                 reverse('assignment:detail', kwargs=self.kwargs)
#             )
#         else:
#             return super().get(request, *args, **kwargs)

#     def get_queryset(self):
#         course_id = self.kwargs.get('course_id')
#         assignment_id = self.kwargs.get('assignment_id')
#         course_type = self.kwargs.get('course_type')
#         try:
#             if course_type == 'my-courses':
#                 course = self.request.user.hosted_courses.get(id=course_id)
#             elif course_type == 'enrolled-courses':
#                 course = self.request.user.enrolled_courses.get(
#                     course__id=course_id
#                 ).course
#             assignment = course.assignments.get(id=assignment_id)
#             return assignment.questions.all()
#         except ObjectDoesNotExist:
#             raise Http404

    # def get_form(self, form_class=None):
    #     queryset = self.get_queryset()
    #     num = len(queryset)
    #     FormSet = formset_factory(
    #         UploadSolutionForm,
    #         min_num=num,
    #         max_num=num,
    #         extra=0,
    #         formset=UploadSolutionFormset,
    #         can_delete=False,
    #     )
    #     form = FormSet(
    #         self.request.POST or None,
    #         self.request.FILES or None,
    #         form_kwarg_queryset=queryset,
    #         user=self.request.user
    #     )
    #     return form

    # def form_valid(self, forms):
    #     for form in forms:
    #         if form.instance.solution != None:
    #             form.instance.question = form.question
    #             form.instance.user = self.request.user
    #             form.save()

    #     return HttpResponseRedirect(self.get_success_url())

    # def get_success_url(self):
    #     return reverse('assignment:detail', kwargs=self.kwargs)

    # def get_context_data(self, **kwargs):
    #     kwargs = super().get_context_data(**kwargs)
    #     kwargs['formset'] = kwargs.pop('form')
    #     kwargs['course_type'] = self.kwargs.get('course_type')
    #     kwargs['course_id'] = self.kwargs.get('course_id')
    #     kwargs['assignment_id'] = self.kwargs.get('assignment_id')
    #     return kwargs
