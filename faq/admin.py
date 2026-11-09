from django.contrib import admin

from .models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'question_hi', 'question_bn')
    search_fields = ('question', 'question_hi', 'question_bn')
    fieldsets = (
        ('English', {'fields': ('question', 'answer')}),
        ('Translations', {
            'description': 'Leave empty to translate automatically on save.',
            'fields': ('question_hi', 'answer_hi', 'question_bn', 'answer_bn'),
        }),
    )
