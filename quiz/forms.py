from django import forms
from .models import Quiz


class DateField(forms.DateInput):
    input_type = 'date'


class TimeField(forms.TimeInput):
    input_type = 'time'


class QuizCreationForm(forms.ModelForm):
    quiz_date = forms.CharField(widget=DateField)
    start_time = forms.CharField(widget=TimeField)
    end_time = forms.CharField(widget=TimeField)
    description = forms.CharField(widget=forms.Textarea(), required=False)

    class Meta:
        model = Quiz
        fields = [
            'name',
            'description',
            'quiz_date',
            'start_time',
            'end_time'
        ]

    def clean(self):
        if self.cleaned_data['description'] == '':
            self.cleaned_data['description'] = 'No description provided by tutor'
        return super().clean()
