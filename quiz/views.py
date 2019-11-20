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
from .models import Quiz
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
        try:
            quiz_id = self.kwargs.get('quiz_id')
            quiz = Quiz.objects.get(id=quiz_id)
        except ObjectDoesNotExist:
            raise Http404
        # if datetime.now().date() > quiz.deadline:
        #     return HttpResponseRedirect(
        #         reverse('assignment:detail', kwargs=self.kwargs)
        #     )
        # else:
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        quiz_id = self.kwargs.get('quiz_id')
        course_type = self.kwargs.get('course_type')
        try:
            if course_type == 'my-courses':
                course = self.request.user.hosted_courses.get(id=course_id)
            elif course_type == 'enrolled-courses':
                course = self.request.user.enrolled_courses.get(
                    course__id=course_id
                ).course
            quiz = course.quizzes.get(id=quiz_id)
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

    def form_valid(self, forms):
        for form in forms:
            form.instance.question = form.question
            form.instance.user = self.request.user
            form.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('quiz:detail', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['formset'] = kwargs.pop('form')
        kwargs['course_type'] = self.kwargs.get('course_type')
        kwargs['course_id'] = self.kwargs.get('course_id')
        kwargs['quiz_id'] = self.kwargs.get('quiz_id')
        return kwargs
