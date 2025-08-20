from modeltranslation.translator import translator, TranslationOptions
from .models import Category, Ad

class CategoryTranslationOptions(TranslationOptions):
    fields = ('name_uz', 'name_ru')

class AdTranslationOptions(TranslationOptions):
    fields = ('name_uz', 'name_ru', 'description_uz', 'description_ru')

translator.register(Category, CategoryTranslationOptions)
translator.register(Ad, AdTranslationOptions)
