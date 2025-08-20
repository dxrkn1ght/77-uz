from modeltranslation.translator import translator, TranslationOptions
from .models import Address

class AddressTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Address, AddressTranslationOptions)
