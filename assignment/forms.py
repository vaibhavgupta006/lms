from django import forms
from .models import Assignment
# from question.models import Submission
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
