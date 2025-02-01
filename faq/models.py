from django.db import models
from ckeditor.fields import RichTextField
from deep_translator import GoogleTranslator

def translate_text(text, dest_lang):
    """ Synchronous translation function using deep-translator """
    try:
        translator = GoogleTranslator(source="auto", target=dest_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback to original text

class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()
    question_hi = models.TextField(blank=True, null=True)
    question_bn = models.TextField(blank=True, null=True)
    answer_hi = RichTextField(blank=True, null=True)
    answer_bn = RichTextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.question_hi:
            self.question_hi = translate_text(self.question, 'hi')
        if not self.question_bn:
            self.question_bn = translate_text(self.question, 'bn')
        if not self.answer_hi:
            self.answer_hi = translate_text(self.answer, 'hi')
        if not self.answer_bn:
            self.answer_bn = translate_text(self.answer, 'bn')
        super().save(*args, **kwargs)

    def get_translated_question(self, lang='en'):
        """ Returns the translated question based on the language """
        return getattr(self, f'question_{lang}', self.question)

    def get_translated_answer(self, lang='en'):
        """ Returns the translated answer based on the language """
        return getattr(self, f'answer_{lang}', self.answer)

    def __str__(self):
        return self.question
