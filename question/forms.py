from django import forms
from .models import Question, Submission, Media
from assignment.models import Assignment
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


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


class QuestionMediaForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput())

    class Meta:
        model = Media
        fields = ['file']


class QuestionCreationFormset(forms.BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        FormSet = forms.inlineformset_factory(
            Question, Media,
            form=QuestionMediaForm,
            extra=1,
            can_delete=False,
        )
        form.nested_forms = [
            FormSet(
                instance=form.instance, prefix=f'question-{index}-media',
                data=form.data if form.is_bound else None,
                files=form.files if form.is_bound else None
            )
        ]

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        for form in self.forms:
            for nested_form in form.nested_forms:
                if nested_form.is_valid():
                    nested_form.save(*args, **kwargs)

        return result


class UploadSolutionFormset(forms.BaseFormSet):
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
