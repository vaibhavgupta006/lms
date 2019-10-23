from django.shortcuts import render, reverse, render_to_response
from .forms import CourseCreationForm
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView
)
from .models import Course, EnrolledCourse
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

# Create your views here.


class CourseCreateView(CreateView):
    template_name = 'course/create.html'
    form_class = CourseCreationForm

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        return super().form_valid(form)


class CourseDetailView(DetailView):
    model = Course
    template_name = 'course/detail.html'

    def get_my_course(self, course_id, only_validate=False):
        try:
            return self.request.user.hosted_courses.get(id=course_id)
        except ObjectDoesNotExist:
            if not only_validate:
                raise Http404
            else:
                return False

    def get_enrolled_course(self, course_id, only_validate=False):
        try:
            return self.request.user.enrolled_courses.get(course__id=course_id).course
        except ObjectDoesNotExist:
            if not only_validate:
                raise Http404
            else:
                return False

    def get_course(self, course_id):
        try:
            return Course.objects.get(id=course_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        course_type = self.kwargs.get('course_type')
        course_id = self.kwargs.get("id")
        course = None
        if course_type == 'my-courses':
            course = self.get_my_course(course_id)
        elif course_type == 'enrolled-courses':
            course = self.get_enrolled_course(course_id)
        else:
            course = self.get_course(course_id)
        return course

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_type = self.kwargs.get('course_type')
        context['course_type'] = course_type
        context['is_student'] = False
        context['is_tutor'] = False
        if course_type == 'my-courses':
            context['is_tutor'] = True
        elif course_type == 'enrolled-courses':
            context['is_student'] = True
        return context

    def get(self, request, *args, **kwargs):
        course_type = self.kwargs.get('course_type')
        course_id = self.kwargs.get('id')
        kwargs = {
            'course_type': course_type,
            'id': course_id
        }
        if course_type == 'all' and self.get_enrolled_course(course_id, only_validate=True):
            kwargs['course_type'] = 'enrolled-courses'
            return HttpResponseRedirect(reverse('course:detail', kwargs=kwargs))
        elif course_type == 'all' and self.get_my_course(course_id, only_validate=True):
            kwargs['course_type'] = 'my-courses'
            return HttpResponseRedirect(reverse('course:detail', kwargs=kwargs))
        else:
            return super().get(request, *args, **kwargs)


class CourseListView(ListView):

    template_name = 'course/list.html'

    def get_queryset(self):
        course_type = self.kwargs.get('course_type')
        if(course_type == 'all'):
            return Course.objects.all()
        if(course_type == 'my-courses'):
            return self.request.user.hosted_courses.all()
        if(course_type == 'enrolled-courses'):
            return self.request.user.enrolled_courses.all()

    def get_context_data(self, *args, **kwargs):
        course_type = self.kwargs.get('course_type')
        context = super().get_context_data(*args, **kwargs)
        if course_type == 'all':
            context['filter'] = 'All courses'
        elif course_type == 'my-courses':
            context['filter'] = 'My courses'
        elif course_type == 'enrolled-courses':
            context['filter'] = 'Enrolled courses'
        return context


class CourseUpdateView(UpdateView):
    template_name = 'course/update.html'
    form_class = CourseCreationForm

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        try:
            return self.request.user.hosted_courses.get(id=course_id)
        except ObjectDoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['course_id'] = self.kwargs.get('course_id')
        return kwargs


def enrollView(request, *args, **kwargs):
    if request.method == "POST":
        course = Course.objects.get(id=kwargs.get('course_id'))
        user = request.user
        try:
            user.hosted_courses.get(id=course.id)
            raise HttpResponseBadRequest
        except ObjectDoesNotExist:
            pass

        new_enrollment = EnrolledCourse()
        new_enrollment.user = user
        new_enrollment.course = course
        new_enrollment.save()
        return render_to_response('course/student_actions.html')
    else:
        raise Http404


def unenrollView(request, *args, **kwargs):
    if request.method == "POST":
        course = Course.objects.get(id=kwargs.get('course_id'))
        user = request.user
        try:
            enrolled_course = EnrolledCourse.objects.get(
                Q(user=user) & Q(course=course)
            )
            enrolled_course.delete()
            return render_to_response('course/user_actions.html')
        except ObjectDoesNotExist:
            raise Http404

    else:
        raise Http404
