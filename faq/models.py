from django.db import models
from ckeditor.fields import RichTextField

class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()
    question_hi = models.TextField(blank=True, null=True)  # Hindi translation
    question_bn = models.TextField(blank=True, null=True)  # Bengali translation
    answer_hi = RichTextField(blank=True, null=True)  # Hindi translation
    answer_bn = RichTextField(blank=True, null=True)  # Bengali translation

    def get_translated_question(self, lang):
        return getattr(self, f'question_{lang}', self.question)

    def get_translated_answer(self, lang):
        return getattr(self, f'answer_{lang}', self.answer)

    def __str__(self):
        return self.question