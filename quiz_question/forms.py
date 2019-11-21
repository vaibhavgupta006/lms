from django import forms
from .models import Question, Option, Media, Submission
from quiz.models import Quiz
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q


class QuestionCreationForm(forms.ModelForm):
    question = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Question
        fields = [
            'question',
        ]


class SubmissionForm(forms.ModelForm):

    option_selected = forms.ModelChoiceField(
        label='Option', queryset=Option.objects.all(),
        widget=forms.RadioSelect(),
        empty_label=None
    )

    def __init__(self, *args, question=None, **kwargs):
        self.question = question
        super().__init__(*args, **kwargs)
        self.fields['option_selected'].queryset = Option.objects.filter(
            question=self.question
        )
        self.fields['option_selected'].label_from_instance = lambda obj: f'{obj.value}'

    class Meta:
        model = Submission
        fields = ['option_selected']


class QuestionMediaForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.FileInput())

    class Meta:
        model = Media
        fields = ['file']


class QuestionOptionForm(forms.ModelForm):
    value = forms.CharField(widget=forms.Textarea(), label='Option')

    class Meta:
        model = Option
        fields = ['value', 'correct_choice']


class QuestionCreationFormset(forms.BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)
        FormSet = forms.inlineformset_factory(
            Question, Media,
            form=QuestionMediaForm,
            extra=1,
            can_delete=False,
        )
        optionFormSet = forms.inlineformset_factory(
            Question, Option,
            form=QuestionOptionForm,
            extra=1,
            can_delete=False,
        )
        form.nested_forms = [
            # FormSet(
            #     instance=form.instance, prefix=f'question-{index}-media',
            #     data=form.data if form.is_bound else None,
            #     files=form.files if form.is_bound else None
            # ),
            optionFormSet(
                instance=form.instance, prefix=f'question-{index}-option',
                data=form.data if form.is_bound else None,
                files=form.files if form.is_bound else None
            )

        ]

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        for form in self.forms:
            for nested_form in form.nested_forms:
                if nested_form.is_valid() and nested_form.has_changed():
                    nested_form.save(*args, **kwargs)

        return result


class SubmissionFormSet(forms.BaseFormSet):
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
