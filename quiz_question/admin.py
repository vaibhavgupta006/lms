from django.contrib import admin
from .models import Question, Option, Media, Submission

# Register your models here.

admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Media)
admin.site.register(Submission)
