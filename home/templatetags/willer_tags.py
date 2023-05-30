from django.utils.translation import get_language
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def translate_label(context, label):
    from home.models import Translation
    translation = Translation.objects.filter(label=label).first()
    if translation:
        if get_language() == 'it':
            return translation.label_it or label
        else:
            return translation.label_en or label

    return label