from modeltranslation.translator import register, TranslationOptions
from .models import Esigenza, Domanda, Risposta, Area, Text

@register(Esigenza)
class EsigenzaTranslationOptions(TranslationOptions):
    fields = ('nome',)

@register(Domanda)
class DomandaTranslationOptions(TranslationOptions):
    fields = ('domanda',)

@register(Risposta)
class RispostaTranslationOptions(TranslationOptions):
    fields = ('risposta',)

@register(Area)
class AreaTranslationOptions(TranslationOptions):
    fields = ('nome',)

@register(Text)
class TextTranslationOptions(TranslationOptions):
    fields = ('text', 'rich_text')