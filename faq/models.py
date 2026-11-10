import logging

import nh3
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


#: Tags an answer may use. Deliberately narrow: enough for formatted prose and
#: links, with no media, forms, styles or anything script-adjacent.
ALLOWED_TAGS = {
    "p", "br", "strong", "b", "em", "i", "u", "s", "code", "pre", "blockquote",
    "ul", "ol", "li", "h2", "h3", "h4", "a", "span",
}
#: `rel` is deliberately absent: nh3 manages it via its `link_rel` setting,
#: which defaults to "noopener noreferrer" and so protects against reverse
#: tabnabbing on its own. Listing it here is rejected outright by nh3, and
#: overriding it would mean hand-maintaining that protection.
ALLOWED_ATTRIBUTES = {"a": {"href", "title"}}


def sanitize_html(value):
    """Strip anything script-adjacent from an answer.

    Applied on save as well as on render. Sanitising only at render time means
    the database holds whatever was submitted, so one view that forgets to clean
    is a stored-XSS bug; sanitising on the way in makes the stored value safe by
    construction and leaves the render-time pass as defence in depth.
    """
    if not value:
        return value
    return nh3.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)


class FAQ(models.Model):
    # Answers are HTML. These were ckeditor RichTextFields, but
    # django-ckeditor bundles CKEditor 4.22.1, which is end-of-life with
    # unfixed security issues — its own maintainers emit a Django system check
    # saying so (ckeditor.W001). RichTextField is a TextField with a custom
    # admin widget, so dropping it costs the WYSIWYG toolbar and nothing else:
    # the column type, the stored HTML and the API responses are unchanged.
    question = models.TextField()
    answer = models.TextField(help_text="HTML is allowed; it is sanitised on save.")
    question_hi = models.TextField(blank=True, null=True)
    question_bn = models.TextField(blank=True, null=True)
    answer_hi = models.TextField(blank=True, null=True)
    answer_bn = models.TextField(blank=True, null=True)

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
        # Sanitise every answer field on the way in, so the stored value is
        # safe regardless of which view renders it later.
        for name in ("answer", "answer_hi", "answer_bn"):
            setattr(self, name, sanitize_html(getattr(self, name)))
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
