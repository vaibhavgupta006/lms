from django import forms
from .models import Course


class CourseCreationForm(forms.ModelForm):
    description = forms.CharField(required=False, widget=forms.Textarea())
    image = forms.FileField(required=False, widget=forms.FileInput())

    class Meta:
        model = Course
        fields = [
            'name',
            'description',
            'image',
        ]

    def clean(self):
        courseDescription = self.cleaned_data.get('description')
        image = self.cleaned_data.get('image')

        if not courseDescription:
            self.cleaned_data['description'] = 'No description provide by teacher'

        if not image:
            raise forms.ValidationError({"image": "This field is required"})

        return super().clean()
