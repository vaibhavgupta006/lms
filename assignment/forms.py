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


# class QuestionCreationForm(forms.ModelForm):
#     question = forms.CharField(widget=forms.Textarea())

#     class Meta:
#         model = Question
#         fields = [
#             'question',
#         ]


# class UploadSolutionForm(forms.ModelForm):

#     solution = forms.FileField(
#         required=False, widget=forms.FileInput())

#     def __init__(self, *args, question=None, **kwargs):
#         self.question = question
#         super().__init__(*args, **kwargs)

#     class Meta:
#         model = Submission
#         fields = ['solution']


# class QuestionMediaForm(forms.ModelForm):
#     name = forms.CharField(max_length=30, required=False)
#     file = forms.FileField(required=False, widget=forms.FileInput())

#     class Meta:
#         model = Media
#         fields = ['name', 'file']


# class QuestionMediaFormset(forms.BaseModelFormSet):
#     def __init__(self, *args, question_instance=None, **kwargs):
#         super().__init__(*args, **kwargs)


# class QuestionCreationFormset(forms.BaseInlineFormSet):
#     def get_media_queryset(self, form):
#         if form.instance is not None:
#             return Media.objects.filter(question=form.instance)
#         else:
#             return None

#     def add_fields(self, form, index):
#         super().add_fields(form, index)
#         media_queryset = self.get_media_queryset(form)
#         formset = forms.modelformset_factory(
#             Media,
#             form=QuestionMediaForm,
#             formset=QuestionMediaFormset,
#             extra=1,
#             can_delete=False,
#         )
#         form.nested_forms = [
#             formset(queryset=media_queryset, prefix=f'question-{index}-media')
#         ]


# class MyFormSet(forms.BaseFormSet):
#     def __init__(self, *args, form_kwarg_queryset=None, user=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.form_kwarg_queryset = form_kwarg_queryset
#         self.user = user

#     def get_form_kwargs(self, index):
#         kwargs = super().get_form_kwargs(index)
#         kwargs['question'] = self.form_kwarg_queryset[index]
#         try:
#             instance = Submission.objects.get(
#                 Q(question=self.form_kwarg_queryset[index]) &
#                 Q(user=self.user)
#             )
#             kwargs['instance'] = instance
#         except:
#             pass

#         return kwargs
