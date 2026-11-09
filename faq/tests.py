from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import FAQ


def fake_translate(text, dest_lang):
    return f"[{dest_lang}] {text}"


@mock.patch("faq.models.translate_text", side_effect=fake_translate)
class FAQModelTest(TestCase):
    def test_translations_filled_on_save(self, _):
        faq = FAQ.objects.create(question="What is Django?", answer="<p>A web framework.</p>")
        self.assertEqual(faq.question_hi, "[hi] What is Django?")
        self.assertEqual(faq.answer_bn, "[bn] <p>A web framework.</p>")
        self.assertEqual(faq.get_translated_question("hi"), faq.question_hi)
        self.assertEqual(faq.get_translated_answer("hi"), faq.answer_hi)

    def test_unknown_language_falls_back_to_english(self, _):
        faq = FAQ.objects.create(question="Q", answer="A")
        self.assertEqual(faq.get_translated_question("fr"), "Q")
        self.assertEqual(faq.get_translated_answer("en"), "A")

    def test_manual_translation_is_kept(self, _):
        faq = FAQ.objects.create(question="Q", answer="A", question_hi="मैनुअल")
        self.assertEqual(faq.question_hi, "मैनुअल")

    def test_editing_english_refreshes_untouched_translations(self, _):
        faq = FAQ.objects.create(question="Old", answer="A")
        faq.question = "New"
        faq.save()
        self.assertEqual(faq.question_hi, "[hi] New")
        self.assertEqual(faq.answer_hi, "[hi] A")


@mock.patch("faq.models.translate_text", return_value=None)
class FailedTranslationTest(TestCase):
    def test_failed_translation_falls_back_and_is_retried(self, translate):
        faq = FAQ.objects.create(question="Q", answer="A")
        self.assertIsNone(faq.question_hi)
        self.assertEqual(faq.get_translated_question("hi"), "Q")
        translate.return_value = "अनुवाद"
        faq.save()
        self.assertEqual(faq.question_hi, "अनुवाद")


@mock.patch("faq.models.translate_text", side_effect=fake_translate)
class FAQApiTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_list_in_requested_language(self, _):
        FAQ.objects.create(question="Q1", answer="A1")
        response = self.client.get(reverse("faq-list"), {"lang": "bn"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["question"], "[bn] Q1")

    def test_invalid_language_returns_english(self, _):
        FAQ.objects.create(question="Q1", answer="A1")
        response = self.client.get(reverse("faq-list"), {"lang": "../../etc"})
        self.assertEqual(response.json()[0]["question"], "Q1")

    def test_cache_is_invalidated_on_save_and_delete(self, _):
        FAQ.objects.create(question="Q1", answer="A1")
        self.assertEqual(len(self.client.get(reverse("faq-list")).json()), 1)
        faq = FAQ.objects.create(question="Q2", answer="A2")
        self.assertEqual(len(self.client.get(reverse("faq-list")).json()), 2)
        faq.delete()
        self.assertEqual(len(self.client.get(reverse("faq-list")).json()), 1)

    def test_answer_html_is_sanitized(self, _):
        FAQ.objects.create(question="Q", answer='<p onclick="x()">ok</p><script>alert(1)</script>')
        answer = self.client.get(reverse("faq-list")).json()[0]["answer"]
        self.assertNotIn("script", answer)
        self.assertNotIn("onclick", answer)

    def test_api_is_read_only(self, _):
        response = self.client.post(reverse("faq-list"), {"question": "x", "answer": "y"})
        self.assertEqual(response.status_code, 405)

    def test_home_page_renders(self, _):
        FAQ.objects.create(question="Q1", answer="A1")
        response = self.client.get(reverse("home"), {"lang": "hi"})
        self.assertContains(response, "[hi] Q1")

    def test_home_empty_state(self, _):
        self.assertContains(self.client.get(reverse("home")), "No FAQs yet")
