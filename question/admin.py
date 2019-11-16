from django.contrib import admin
from .models import Question, Submission, Media

# Register your models here.

admin.site.register(Question)
admin.site.register(Submission)
admin.site.register(Media)
