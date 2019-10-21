from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import CreateView, DetailView, ListView, FormView, UpdateView
from .forms import (
    AssignmentCreationForm,
    QuestionCreationForm,
    UploadSolutionForm,
    MyFormSet,
)
from .models import Assignment, Question, Submission
from django.urls import reverse, reverse_lazy
from django.forms import inlineformset_factory, formset_factory
from datetime import datetime


# Create your views here.


class CreateAssignmentView(CreateView):
    form_class = AssignmentCreationForm
    template_name = 'assignment/create.html'

    def check_validity(self, request=None):
        request = self.request if request == None else request
        courseId = self.kwargs.get('course_id')

        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404

        try:
            course = request.user.hosted_courses.get(id=courseId)
        except ObjectDoesNotExist:
            raise Http404

        return course

    def get(self, request, *args, **kwargs):
        course = self.check_validity(request)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        course = self.check_validity()
        form.instance.course = course
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs.get('course_id')
        return context


class AssignmentDetailView(DetailView):
    template_name = 'assignment/detail.html'

    def get_my_course_assignment(self, course_id, assignment_id):
        try:
            course = self.request.user.hosted_courses.get(id=course_id)
            return course.assignments.get(id=assignment_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_enrolled_course_assignment(self, course_id, assignment_id):
        try:
            course = self.request.user.enrolled_courses.get(
                course__id=course_id).course
            return course.assignments.get(id=assignment_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        assignment_id = self.kwargs.get('assignment_id')
        course_type = self.kwargs.get('course_type')
        if course_type == 'my-courses':
            return self.get_my_course_assignment(course_id, assignment_id)
        elif course_type == 'enrolled-courses':
            return self.get_enrolled_course_assignment(course_id, assignment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_type = self.kwargs.get('course_type')
        questions = context.get('object').questions.all()
        context['questions'] = questions
        context['question_count'] = questions.count()
        context['is_tutor'] = False
        context['is_student'] = False
        context['course_type'] = course_type
        context['course_id'] = self.kwargs.get('course_id')
        if course_type == 'my-courses':
            context['is_tutor'] = True
        elif course_type == 'enrolled-courses':
            context["is_student"] = True
        context['deadline_expired'] = True if datetime.now(
        ).date() > context['object'].deadline else False
        return context


class CreateQuestionView(FormView):
    template_name = 'assignment/create_questions.html'

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404
        else:
            return super().get(request, *args, **kwargs)

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
        )
        form = FormSet(
            self.request.POST or None,
            instance=self.get_instance()
        )
        return form

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        course_id = self.kwargs.get('course_id')
        assignment_id = self.kwargs.get('assignment_id')
        return reverse('assignment:create-question', kwargs={"course_id": course_id, "assignment_id": assignment_id, 'course_type': "my-courses"})

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


class AssignmentListView(ListView):
    template_name = 'assignment/list.html'

    def get_queryset(self):
        course_type = self.kwargs.get('course_type')
        courseId = self.kwargs.get("course_id")
        if course_type == 'my-courses':
            return self.request.user.hosted_courses.get(id=courseId).assignments.all().order_by('-date_created')
        elif course_type == 'enrolled-courses':
            return self.request.user.enrolled_courses.get(course__id=courseId).course.assignments.all().order_by('-date_created')

    def get_context_data(self, **kwargs):
        course_type = self.kwargs.get('course_type')
        context = super().get_context_data(**kwargs)
        context['is_tutor'] = True if course_type == 'my-courses' else False
        context['course_type'] = course_type
        context['course_id'] = self.kwargs.get('course_id')
        return context


class SubmissionView(ListView):
    template_name = 'assignment/submission.html'

    def group_queryset(self, queryset, question_count):
        # user_count = queryset.count()//question_count
        print(queryset)
        new_queryset = []
        group = []
        try:
            prev_user = queryset[0].user
        except IndexError:
            return queryset
        for submission in queryset:
            if submission.user != prev_user:
                new_queryset.append(group)
                group = []
                prev_user = submission.user
            group.append(submission)
        new_queryset.append(group)
        return new_queryset

    def get_queryset(self, *args, **kwargs):
        assignment_id = self.kwargs.get('assignment_id')
        course_id = self.kwargs.get('course_id')
        course_type = self.kwargs.get('course_type')

        if course_type == 'my-courses':
            course = self.request.user.hosted_courses.get(id=course_id)
        elif course_type == 'enrolled-courses':
            course = self.request.user.enrolled_courses.get(
                course__id=course_id).course

        assignment = course.assignments.get(id=assignment_id)
        question_count = assignment.questions.count()
        submissions = Submission.objects.filter(
            question__assignment=assignment
        )
        submissions = submissions.order_by(
            '-user__first_name', '-user__last_name', '-user__id'
        )
        return self.group_queryset(submissions, question_count)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_id'] = self.kwargs.get('course_id')
        kwargs['assignment_id'] = self.kwargs.get('assignment_id')
        kwargs['course_type'] = self.kwargs.get('course_type')
        return kwargs


class SubmitView(FormView):
    template_name = 'assignment/upload_solution.html'

    def get(self, request, *args, **kwargs):
        assignment_id = self.kwargs.get('assignment_id')
        assignment = Assignment.objects.get(id=assignment_id)
        if datetime.now().date() > assignment.deadline:
            return HttpResponseRedirect(
                reverse('assignment:detail', kwargs=self.kwargs)
            )
        else:
            return super().get(request, *args, **kwargs)

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        assignment_id = self.kwargs.get('assignment_id')
        course_type = self.kwargs.get('course_type')
        try:
            if course_type == 'my-courses':
                course = self.request.user.hosted_courses.get(id=course_id)
            elif course_type == 'enrolled-courses':
                course = self.request.user.enrolled_courses.get(
                    course__id=course_id
                ).course
            assignment = course.assignments.get(id=assignment_id)
            return assignment.questions.all()
        except ObjectDoesNotExist:
            raise Http404

    def get_form(self, form_class=None):
        queryset = self.get_queryset()
        num = len(queryset)
        FormSet = formset_factory(
            UploadSolutionForm,
            min_num=num,
            max_num=num,
            extra=0,
            formset=MyFormSet,
            can_delete=False,
        )
        form = FormSet(
            self.request.POST or None,
            self.request.FILES or None,
            form_kwarg_queryset=queryset,
            user=self.request.user
        )
        return form

    def form_valid(self, forms):
        for form in forms:
            if form.instance.solution != None:
                form.instance.question = form.question
                form.instance.user = self.request.user
                form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('assignment:detail', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['formset'] = kwargs.pop('form')
        kwargs['course_type'] = self.kwargs.get('course_type')
        kwargs['course_id'] = self.kwargs.get('course_id')
        kwargs['assignment_id'] = self.kwargs.get('assignment_id')
        return kwargs


class AssignmentUpdateView(UpdateView):
    template_name = 'assignment/update.html'
    form_class = AssignmentCreationForm

    def get_success_url(self):
        return reverse('assignment:detail', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404
        else:
            return super().get(request, *args, **kwargs)

    def get_my_course_assignment(self, course_id, assignment_id):
        try:
            course = self.request.user.hosted_courses.get(id=course_id)
            return course.assignments.get(id=assignment_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        assignment_id = self.kwargs.get('assignment_id')
        course_type = self.kwargs.get('course_type')
        return self.get_my_course_assignment(course_id, assignment_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs.get('course_id')
        context['assignment_id'] = self.kwargs.get("assignment_id")
        return context
