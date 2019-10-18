from django import forms
from .models import Assignment, Question, Submission
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class DateField(forms.DateInput):
    input_type = 'date'


class AssignmentCreationForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea())
    deadline = forms.CharField(widget=DateField)

    class Meta:
        model = Assignment
        fields = [
            'name',
            'description',
            'deadline',
        ]

    def clean(self, *args, **kwargs):
        description = self.cleaned_data.get('description')
        if not description:
            self.cleaned_data['description'] = 'No description provided by teacher'

        return super().clean(*args, **kwargs)


class QuestionCreationForm(forms.ModelForm):
    question = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Question
        fields = [
            'question',
        ]


class UploadSolutionForm(forms.ModelForm):

    solution = forms.FileField(
        required=False, widget=forms.FileInput())

    def __init__(self, *args, question=None, **kwargs):
        self.question = question
        super().__init__(*args, **kwargs)

    class Meta:
        model = Submission
        fields = ['solution']


class MyFormSet(forms.BaseFormSet):
    def __init__(self, *args, form_kwarg_queryset=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_kwarg_queryset = form_kwarg_queryset
        self.user = user

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['question'] = self.form_kwarg_queryset[index]
        try:
            instance = Submission.objects.get(
                Q(question=self.form_kwarg_queryset[index]) &
                Q(user=self.user)
            )
            kwargs['instance'] = instance
        except:
            pass

        return kwargs
