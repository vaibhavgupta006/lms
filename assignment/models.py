from django.db import models
from course.models import Course
from django.urls import reverse
from authentication.models import User
import os
import sys
import subprocess
import docx
from docx.enum.style import WD_STYLE_TYPE
from django.conf import settings


# Create your models here.

def get_upload_location(instance, filename):
    assignment_name = f"assignment_{instance.question.assignment.id}"
    course_name = f"course_{instance.question.assignment.course.id}"
    return os.path.join(os.path.join(assignment_name, course_name), filename)


def add_header(input_file, header_text):
    input_doc = docx.Document(input_file)
    header = input_doc.sections[0].header
    for run in header.paragraphs[0].runs:
        run.text = ''
    run = header.paragraphs[0].add_run(f'Question: ')
    run.font.color.rgb = docx.shared.RGBColor(0x4c, 0x2f, 0xc9)
    run = header.paragraphs[0].add_run(f'Question: {header_text}')
    run.font.color.rgb = docx.shared.RGBColor(100, 100, 100)
    header.paragraphs[0].style = input_doc.styles['Heading']
    header.add_paragraph()
    input_doc.save(input_file)


def convert_word_pdf(input_file, output_file, header):
    add_header(input_file, header)
    args = [
        'libreoffice',
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_file, input_file,
    ]
    process = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10
    )


class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='assignments')
    name = models.CharField(max_length=20, null=False, blank=False)
    description = models.CharField(
        max_length=500,
        null=False,
        blank=False,
        default='no description provided by tutor',
    )
    deadline = models.DateField(null=False, blank=False)
    date_created = models.DateTimeField(null=False, auto_now_add=True)

    def get_absolute_url(self):
        return reverse('assignment:create-question', kwargs={
            "course_id": self.course.id,
            "assignment_id": self.id,
            "course_type": "my-courses"
        })

    def __str__(self):
        return f'course {self.course.id} assignment: {self.id}'


class Question(models.Model):
    question = models.CharField(max_length=1000, blank=False, null=False)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='questions')

    def __str__(self):
        return f'assignment {self.assignment.id} question {self.id}'


class Submission(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='all_submissions'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    solution = models.FileField(
        upload_to=get_upload_location,
        null=True
    )
    solution_pdf = models.FileField(
        null=True
    )
    date_created = models.DateTimeField(auto_now_add=True, null=False)

    def add_pdf_solution(self):
        file_format = self.solution.url.rsplit('.')[-1]
        input_file = self.solution.path

        output_file = input_file.split(os.sep)[0:-1]
        output_file = os.sep.join(output_file)

        output_relative_media = self.solution.url.split(os.sep)[2:]
        output_relative_media = (os.sep.join(output_relative_media)).split('.')
        output_relative_media[-1] = 'pdf'
        output_relative_media = ".".join(output_relative_media)

        timeout = 10

        if file_format == 'pdf':
            self.solution_pdf = self.solution
            return
        elif file_format == 'doc' or file_format == 'docx':
            convert_word_pdf(
                input_file,
                output_file,
                self.question.question,
            )
            self.solution_pdf = output_relative_media
        else:
            pass

    def save(self, *args, add_pdf=True, **kwargs):
        super().save()
        if add_pdf and self.solution != None:
            self.add_pdf_solution()
            self.save(add_pdf=False)
            return
        return

    def __str__(self):
        return f"solution to question {self.question.id} by {self.user.username}"
