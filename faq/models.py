from django.db import models
from ckeditor.fields import RichTextField

class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()  # WYSIWYG editor
    question_hi = models.TextField(blank=True, null=True)
    question_bn = models.TextField(blank=True, null=True)
    answer_hi = RichTextField(blank=True, null=True)
    answer_bn = RichTextField(blank=True, null=True)