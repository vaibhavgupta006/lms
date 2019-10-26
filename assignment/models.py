from django.db import models
from course.models import Course
from django.urls import reverse
from authentication.models import User
from docx.enum.style import WD_STYLE_TYPE
from django.conf import settings

import os
import sys
import subprocess
import docx


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
    run = header.paragraphs[0].add_run(f'{header_text}')
    run.font.color.rgb = docx.shared.RGBColor(100, 100, 100)
    header.paragraphs[0].style = input_doc.styles['Heading']
    header.add_paragraph()
    input_doc.save(input_file)


def convert_image_word(input_file, output_file_dir, file_name):
    doc = docx.Document()
    doc.add_picture(input_file, width=docx.shared.Inches(6))
    doc.styles.add_style("Heading", docx.enum.style.WD_STYLE_TYPE.PARAGRAPH)
    doc_path = os.path.join(output_file_dir, f'{file_name}.docx')
    doc.save(doc_path)

    return doc_path


def convert_word_pdf(input_file, output_file, header_text):

    add_header(input_file, header_text)

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

        input_file_path_list = input_file.split(os.sep)
        file_name = input_file_path_list[-1].replace(f'.{file_format}', '', 1)

        output_file_dir = os.sep.join(input_file_path_list[0:-1])

        output_relative_media = input_file.replace(settings.MEDIA_URL, '', 1)
        output_relative_media = output_relative_media.replace(
            f'{file_name}.{file_format}',
            f'{file_name}.pdf',
            1
        )

        timeout = 10

        supported_file_format = ['doc', 'docx', 'jpg', 'jpeg', 'png']
        image_file_format = ['jpg', 'jpeg', 'png']
        is_image = True if file_format in image_file_format else False

        if file_format == 'pdf':
            self.solution_pdf = self.solution
            return
        elif file_format in supported_file_format:
            if is_image:
                input_file = convert_image_word(
                    input_file, output_file_dir, file_name
                )
            convert_word_pdf(
                input_file,
                output_file_dir,
                self.question.question,
            )
            self.solution_pdf = output_relative_media
            if is_image:
                os.remove(input_file)
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
