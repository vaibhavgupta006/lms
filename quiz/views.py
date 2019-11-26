from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    FormView
)
from .forms import QuizCreationForm
from quiz_question.forms import SubmissionForm, SubmissionFormSet

from django.forms import formset_factory
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from datetime import datetime
from django.shortcuts import reverse
from .models import Quiz, Submission as QuizSubmission
from quiz_question.models import Submission, Option
from django.db.models import Q
from django.db import IntegrityError
# Create your views here.


class QuizCreationView(CreateView):
    form_class = QuizCreationForm
    template_name = 'quiz/create.html'

    def check_validity(self):
        course_id = self.kwargs.get('course_id')

        try:
            course = self.request.user.hosted_courses.get(id=course_id)
            if self.kwargs.get('course_type') != 'my-courses':
                raise Http404
        except ObjectDoesNotExist:
            raise Http404

        return course

    def get(self, request, *args, **kwargs):
        self.check_validity()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        course = self.check_validity()
        form.instance.course = course
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs.get('course_id')
        return context


class QuizListView(ListView):
    template_name = 'quiz/list.html'

    def get_queryset(self):
        course_type = self.kwargs.get('course_type')
        courseId = self.kwargs.get("course_id")
        if course_type == 'my-courses':
            return self.request.user.hosted_courses.get(id=courseId).quizzes.all().order_by('-date_created')
        elif course_type == 'enrolled-courses':
            return self.request.user.enrolled_courses.get(course__id=courseId).course.quizzes.all().order_by('-date_created')

    def get_context_data(self, **kwargs):
        course_type = self.kwargs.get('course_type')
        context = super().get_context_data(**kwargs)
        context['is_tutor'] = True if course_type == 'my-courses' else False
        context['is_student'] = True if course_type == 'enrolled-courses' else False
        context['course_type'] = course_type
        context['course_id'] = self.kwargs.get('course_id')
        return context


class QuizDetailView(DetailView):
    template_name = 'quiz/detail.html'

    def get_my_course_quiz(self, course_id, quiz_id):
        try:
            course = self.request.user.hosted_courses.get(id=course_id)
            return course.quizzes.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_enrolled_course_quiz(self, course_id, quiz_id):
        try:
            course = self.request.user.enrolled_courses.get(
                course__id=course_id).course
            return course.quizzes.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')
        course_type = self.kwargs.get('course_type')
        if course_type == 'my-courses':
            return self.get_my_course_quiz(course_id, quiz_id)
        elif course_type == 'enrolled-courses':
            return self.get_enrolled_course_quiz(course_id, quiz_id)

    def is_locked(self, object):
        current_datetime = datetime.now()
        if current_datetime.date() < object.quiz_date:
            return True
        if current_datetime.date() == object.quiz_date and current_datetime.time() < object.start_time:
            return True
        return False

    def is_ongoing(self, object):
        current_datetime = datetime.now()
        if current_datetime.date() == object.quiz_date and current_datetime.time() >= object.start_time and current_datetime.time() < object.end_time:
            return True
        else:
            return False

    def is_expired(self, object):
        current_datetime = datetime.utcnow()
        if current_datetime.date() > object.quiz_date:
            return True
        print(current_datetime.time() > object.end_time)
        print(object.end_time)
        print(current_datetime.time())
        if current_datetime.date() == object.quiz_date and current_datetime.time() > object.end_time:
            return True
        return False

    def submitted(self, object):
        objects = QuizSubmission.objects.filter(
            Q(user=self.request.user)
            &
            Q(quiz=object)
        )
        return (True, objects.first()) if objects.count() > 0 else (False, None)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_type = self.kwargs.get('course_type')
        questions = context.get('object').questions.all()
        context['questions'] = questions
        context['question_count'] = questions.count()
        context['is_tutor'] = True if self.kwargs.get(
            'course_type') == 'my-courses' else False
        context['is_student'] = True if self.kwargs.get(
            'course_type') == 'enrolled-courses' else False
        context['course_type'] = course_type
        context['course_id'] = self.kwargs.get('course_id')
        context['locked'] = self.is_locked(context['object'])
        context['ongoing'] = self.is_ongoing(context['object'])
        context['expired'] = self.is_expired(context['object'])
        if course_type == 'enrolled-courses':
            context['submitted'], context['submission_object'] = self.submitted(
                context['object'])

        return context


class QuizUpdateView(UpdateView):
    template_name = 'quiz/update.html'
    form_class = QuizCreationForm

    def get_success_url(self):
        return reverse('quiz:detail', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404
        else:
            return super().get(request, *args, **kwargs)

    def get_my_course_quiz(self, course_id, quiz_id):
        try:
            course = self.request.user.hosted_courses.get(id=course_id)
            return course.quizzes.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')
        course_type = self.kwargs.get('course_type')
        return self.get_my_course_quiz(course_id, quiz_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course_id'] = self.kwargs.get('course_id')
        context['quiz_id'] = self.kwargs.get("quiz_id")
        return context


class QuizSubmissionView(FormView):
    template_name = 'quiz/upload_solution.html'

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') == 'my-courses':
            raise Http404

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') == 'my-courses':
            raise Http404

        return super().post(request, *args, **kwargs)

    def is_expired(self, object):
        current_datetime = datetime.utcnow()
        if current_datetime.date() > object.quiz_date:
            return True
        print(current_datetime.time() > object.end_time)
        print(object.end_time)
        print(current_datetime.time())
        if current_datetime.date() == object.quiz_date and current_datetime.time() > object.end_time:
            return True
        return False

    def is_locked(self, object):
        current_datetime = datetime.now()
        if current_datetime.date() < object.quiz_date:
            return True
        if current_datetime.date() == object.quiz_date and current_datetime.time() < object.start_time:
            return True
        return False

    def submitted(self, object):
        objects = QuizSubmission.objects.filter(
            Q(user=self.request.user)
            &
            Q(quiz=object)
        )
        return True if objects.count() > 0 else False

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')
        course_type = self.kwargs.get('course_type')
        try:
            course = self.request.user.enrolled_courses.get(
                course__id=course_id
            ).course
            quiz = course.quizzes.get(id=quiz_id)
            if self.is_expired(quiz) or self.is_locked(quiz) or self.submitted(quiz):
                raise Http404
            else:
                return quiz.questions.all()
        except ObjectDoesNotExist:
            raise Http404

    def get_form(self, form_class=None):
        queryset = self.get_queryset()
        num = len(queryset)
        FormSet = formset_factory(
            SubmissionForm,
            min_num=num,
            max_num=num,
            extra=0,
            formset=SubmissionFormSet,
            can_delete=False,
        )
        form = FormSet(
            self.request.POST or None,
            self.request.FILES or None,
            form_kwarg_queryset=queryset,
            user=self.request.user
        )
        return form

    def form_valid(self, formset):
        try:
            submission = QuizSubmission()
            submission.user = self.request.user
            submission.quiz = formset[0].question.quiz
            submission.save()
            self.submission_id = submission.id
        except IntegrityError:
            pass
        except IndexError:
            pass

        for form in formset:
            if form.has_changed():
                form.instance.question = form.question
                form.instance.user = self.request.user
                form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        self.kwargs['submission_id'] = self.submission_id
        return reverse('quiz:submission-detail', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['formset'] = kwargs.pop('form')
        kwargs['course_type'] = self.kwargs.get('course_type')
        kwargs['course_id'] = self.kwargs.get('course_id')
        kwargs['quiz_id'] = self.kwargs.get('quiz_id')
        return kwargs


class ViewSubmissionView(ListView):
    template_name = 'quiz/submission.html'

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('course_type') != 'my-courses':
            raise Http404

        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_id')
        course_id = self.kwargs.get('course_id')

        try:
            self.request.user.hosted_courses.get(id=course_id)
        except ObjectDoesNotExist:
            raise Http404

        return QuizSubmission.objects.filter(quiz__id=quiz_id)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_id'] = self.kwargs.get('course_id')
        kwargs['quiz_id'] = self.kwargs.get('quiz_id')
        kwargs['course_type'] = self.kwargs.get('course_type')
        return kwargs


class SubmissionDetailView(ListView):
    template_name = 'quiz/submission_detail.html'
    # def get(self, request, *args, **kwargs):
    #     try:
    #         course_id = self.kwargs.get('course_id')
    #         request.user.enrolled_courses.get(id=course_id)
    #     except ObjectDoesNotExist:
    #         raise Http404

    #     super().get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     try:
    #         course_id = self.kwargs.get('course_id')
    #         request.user.enrolled_courses.get(id=course_id)
    #     except ObjectDoesNotExist:
    #         raise Http404

    #     super().post(request, *args, **kwargs)

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')
        submission_id = self.kwargs.get('submission_id')
        course_type = self.kwargs.get('course_type')

        course, quiz = None, None
        try:
            if course_type == 'my-courses':
                course = self.request.user.hosted_courses.get(id=course_id)
            elif course_type == 'enrolled-courses':
                course = self.request.user.enrolled_courses.get(
                    course__id=course_id).course
            quiz = course.quizzes.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Http404

        if course_type == 'enrolled-courses':
            return Submission.objects.filter(
                Q(user=self.request.user)
                &
                Q(question__quiz=quiz)
            )
        elif course_type == 'my-courses':
            return Submission.objects.filter(question__quiz=quiz)

    def get_options(self, object_list):
        for object in object_list:
            object.options = Option.objects.filter(question=object.question)

    def get_submission_object(self):
        submission_id = self.kwargs.get('submission_id')
        return QuizSubmission.objects.get(id=submission_id)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['is_tutor'] = True if self.kwargs.get(
            'course_type') == 'my-courses' else False
        context['is_student'] = True if self.kwargs.get(
            'course_type') == 'enrolled-courses' else False
        context['course_type'] = self.kwargs.get('course_type')
        context['submission'] = self.get_submission_object()
        self.get_options(context['object_list'])
        return context
