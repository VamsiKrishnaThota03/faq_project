"""
Tests for answer sanitisation.

Context: answers are HTML. They used to be edited with django-ckeditor, which
bundles CKEditor 4.22.1 — end-of-life with unfixed security issues, reported by
its own maintainers through a Django system check (ckeditor.W001). The
dependency is gone; answers are now plain TextFields sanitised with nh3.

Sanitising moved from render-time only to **save-time as well**. That matters:
cleaning only on the way out means the database holds whatever was submitted,
so any view that forgets to clean becomes a stored-XSS bug. Cleaning on the way
in makes the stored value safe by construction, and the render-time pass stays
as defence in depth.
"""

from unittest import mock

from django.test import TestCase

from .models import FAQ, sanitize_html


def _no_translation(text, dest_lang):
    """Stub so tests never make a network call to the translation service."""
    return None


@mock.patch('faq.models.translate_text', _no_translation)
class SanitizeHtmlTests(TestCase):
    def test_strips_script_tags(self):
        cleaned = sanitize_html('<p>Hello</p><script>alert(1)</script>')
        self.assertIn('Hello', cleaned)
        self.assertNotIn('script', cleaned.lower())

    def test_strips_event_handlers(self):
        cleaned = sanitize_html('<p onclick="steal()">Text</p>')
        self.assertNotIn('onclick', cleaned.lower())
        self.assertIn('Text', cleaned)

    def test_strips_img_onerror_payloads(self):
        # img is not in the allowed tag set at all, so the whole element goes.
        cleaned = sanitize_html('<img src=x onerror=alert(1)>')
        self.assertNotIn('onerror', cleaned.lower())
        self.assertNotIn('<img', cleaned.lower())

    def test_strips_javascript_urls(self):
        cleaned = sanitize_html('<a href="javascript:alert(1)">click</a>')
        self.assertNotIn('javascript:', cleaned.lower())

    def test_strips_iframes_objects_and_forms(self):
        for payload in (
            '<iframe src="https://evil.example"></iframe>',
            '<object data="evil.swf"></object>',
            '<form action="https://evil.example"><input name="x"></form>',
            '<style>body{display:none}</style>',
        ):
            cleaned = sanitize_html(payload)
            self.assertNotRegex(
                cleaned.lower(),
                r'<(iframe|object|form|input|style)',
                f'{payload} should have been stripped',
            )

    def test_keeps_formatting_tags_and_links(self):
        html = (
            '<p>Read the <strong>docs</strong> and the <em>guide</em>.</p>'
            '<ul><li>one</li><li>two</li></ul>'
            '<a href="https://example.com" title="Example">link</a>'
        )
        cleaned = sanitize_html(html)
        for fragment in ('<strong>', '<em>', '<ul>', '<li>', 'href="https://example.com"'):
            self.assertIn(fragment, cleaned)

    def test_adds_noopener_noreferrer_to_links(self):
        # nh3 manages rel itself, which is why `rel` is not in the allowed
        # attribute set: it protects against reverse tabnabbing automatically.
        cleaned = sanitize_html('<a href="https://example.com">link</a>')
        self.assertIn('noopener', cleaned)
        self.assertIn('noreferrer', cleaned)

    def test_passes_through_empty_values_unchanged(self):
        self.assertEqual(sanitize_html(''), '')
        self.assertIsNone(sanitize_html(None))


@mock.patch('faq.models.translate_text', _no_translation)
class SaveTimeSanitizationTests(TestCase):
    def test_a_script_tag_never_reaches_the_database(self):
        faq = FAQ.objects.create(
            question='Is the answer sanitised?',
            answer='<p>Yes</p><script>alert(1)</script>',
        )
        faq.refresh_from_db()
        # The point of sanitising on save: the stored value is safe, so a view
        # that forgets to clean cannot become a stored-XSS bug.
        self.assertNotIn('script', faq.answer.lower())
        self.assertIn('Yes', faq.answer)

    def test_translated_answer_fields_are_sanitised_too(self):
        faq = FAQ(
            question='Q',
            answer='<p>ok</p>',
            answer_hi='<p>hi</p><script>alert(1)</script>',
            answer_bn='<img src=x onerror=alert(1)>',
        )
        faq.save()
        faq.refresh_from_db()
        self.assertNotIn('script', (faq.answer_hi or '').lower())
        self.assertNotIn('onerror', (faq.answer_bn or '').lower())

    def test_sanitisation_is_idempotent(self):
        # Saving twice must not progressively mangle valid markup.
        faq = FAQ.objects.create(question='Q', answer='<p>Keep <strong>this</strong></p>')
        first = FAQ.objects.get(pk=faq.pk).answer
        faq.save()
        self.assertEqual(FAQ.objects.get(pk=faq.pk).answer, first)

    def test_the_model_no_longer_depends_on_ckeditor(self):
        # Regression guard: reintroducing RichTextField would pull the
        # end-of-life CKEditor 4 bundle back in.
        from django.db import models as django_models

        for name in ('answer', 'answer_hi', 'answer_bn'):
            field = FAQ._meta.get_field(name)
            self.assertIs(
                type(field),
                django_models.TextField,
                f'{name} should be a plain TextField, not {type(field).__name__}',
            )
