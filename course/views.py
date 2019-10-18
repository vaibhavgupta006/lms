from django.shortcuts import render, reverse
from .forms import CourseCreationForm
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView
)
from .models import Course
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist


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
            return self.request.user.enrolled_courses.get(id=course_id)
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
        context['students'] = context['object'].students.all()
        return context

    def get_template_names(self):
        course_type = self.kwargs.get('course_type')
        if course_type == 'all':
            return 'course/detail_all.html'
        elif course_type == 'my-courses':
            return 'course/detail_my_courses.html'
        elif course_type == 'enrolled-courses':
            return 'course/detail_enrolled_courses.html'

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


def enrollView(request, *args, **kwargs):
    course = Course.objects.get(id=kwargs.get('course_id'))
    request.enrolled_courses.add(course)


class CourseUpdateView(UpdateView):
    template_name = 'course/update.html'
    form_class = CourseCreationForm

    def get_object(self, queryset=None):
        course_id = self.kwargs.get('course_id')
        try:
            return self.request.user.hosted_courses.get(id=course_id)
        except ObjectDoesNotExist:
            raise Http404
