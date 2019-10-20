from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import CreateView, DetailView, ListView, FormView
from .forms import AssignmentCreationForm, QuestionCreationForm, UploadSolutionForm, MyFormSet
from .models import Assignment, Question, Submission
from django.urls import reverse, reverse_lazy
from django.forms import inlineformset_factory, formset_factory


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
        if course_type == 'my-courses':
            context['is_tutor'] = True
        elif course_type == 'enrolled-courses':
            context["is_student"] = True
        return context


class CreateQuestionView(FormView):
    template_name = 'assignment/create_questions.html'

    def get_instance(self, request=None):
        request = self.request if request is None else request
        courseId = self.kwargs.get('course_id')
        assignmentId = self.kwargs.get('assignment_id')

        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404

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
        return context


class SubmissionView(ListView):
    template_name = 'assignment/submission.html'

    def group_queryset(self, queryset, question_count):
        # user_count = queryset.count()//question_count
        new_queryset = []
        group = []
        for index, submission in enumerate(queryset):
            group.append(submission)
            if (index+1) % question_count == 0:
                new_queryset.append(group)
                group = []
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
            '-first_name').order_by('-last_name').order_by('-id')
        return self.group_queryset(submissions, question_count)


class SubmitView(FormView):
    template_name = 'assignment/upload_solution.html'

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
            form.instance.question = form.question
            form.instance.user = self.request.user
            form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('assignment:detail', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['formset'] = kwargs.pop('form')
        return kwargs
