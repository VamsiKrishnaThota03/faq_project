import logging

from ckeditor.fields import RichTextField
from deep_translator import GoogleTranslator
from django.db import models

logger = logging.getLogger(__name__)

# Languages served by the API, besides the English source text.
TRANSLATED_LANGUAGES = ("hi", "bn")
SUPPORTED_LANGUAGES = ("en",) + TRANSLATED_LANGUAGES
TRANSLATED_FIELDS = ("question", "answer")


def translate_text(text, dest_lang):
    """Translate ``text`` into ``dest_lang``.

    Returns ``None`` when translation fails, so the field stays empty and is
    retried on the next save instead of permanently storing English text.
    """
    if not text:
        return text
    try:
        return GoogleTranslator(source="auto", target=dest_lang).translate(text)
    except Exception:  # network errors, rate limits, unsupported input...
        logger.warning("Translation to %s failed", dest_lang, exc_info=True)
        return None


class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()
    question_hi = models.TextField(blank=True, null=True)
    question_bn = models.TextField(blank=True, null=True)
    answer_hi = RichTextField(blank=True, null=True)
    answer_bn = RichTextField(blank=True, null=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def _clear_stale_translations(self):
        """If the English source changed but a translation was left untouched,
        clear it so it is regenerated from the new text."""
        if not self.pk:
            return
        previous = FAQ.objects.filter(pk=self.pk).first()
        if previous is None:
            return
        for field in TRANSLATED_FIELDS:
            if getattr(previous, field) == getattr(self, field):
                continue
            for lang in TRANSLATED_LANGUAGES:
                name = f"{field}_{lang}"
                if getattr(previous, name) == getattr(self, name):
                    setattr(self, name, None)

    def save(self, *args, **kwargs):
        self._clear_stale_translations()
        for field in TRANSLATED_FIELDS:
            for lang in TRANSLATED_LANGUAGES:
                name = f"{field}_{lang}"
                if not getattr(self, name):
                    setattr(self, name, translate_text(getattr(self, field), lang))
        super().save(*args, **kwargs)

    def _translated(self, field, lang):
        if lang in TRANSLATED_LANGUAGES:
            value = getattr(self, f"{field}_{lang}")
            if value:
                return value
        # English, an unsupported language, or a missing translation.
        return getattr(self, field)

    def get_translated_question(self, lang="en"):
        """Return the question in ``lang``, falling back to English."""
        return self._translated("question", lang)

    def get_translated_answer(self, lang="en"):
        """Return the answer in ``lang``, falling back to English."""
        return self._translated("answer", lang)

    def __str__(self):
        return self.question
