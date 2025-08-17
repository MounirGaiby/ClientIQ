"""
Translation services for managing multi-language content.
"""

from django.core.cache import cache
from django.db import transaction
from apps.translations.models import Translation, TranslationKey, Language


class TranslationService:
    """Service for managing translations."""
    
    @staticmethod
    def get_translation(tenant, key, language_code, fallback_to_english=True):
        """Get a single translation value."""
        try:
            translation_key = TranslationKey.objects.get(key=key)
            language = Language.objects.get(code=language_code, is_active=True)
            
            # Try to get tenant-specific translation
            translation = Translation.objects.filter(
                tenant=tenant,
                translation_key=translation_key,
                language=language,
                is_active=True
            ).first()
            
            if translation:
                return translation.value
            
            # Fallback to English if requested
            if fallback_to_english and language_code != 'en':
                english_language = Language.objects.filter(code='en', is_active=True).first()
                if english_language:
                    english_translation = Translation.objects.filter(
                        tenant=tenant,
                        translation_key=translation_key,
                        language=english_language,
                        is_active=True
                    ).first()
                    
                    if english_translation:
                        return english_translation.value
            
            # Fallback to default value
            return translation_key.default_value
            
        except (TranslationKey.DoesNotExist, Language.DoesNotExist):
            # Return key as fallback
            return key
    
    @staticmethod
    def get_bulk_translations(tenant, keys, language_code):
        """Get multiple translations at once."""
        result = {}
        
        for key in keys:
            result[key] = TranslationService.get_translation(
                tenant=tenant,
                key=key,
                language_code=language_code
            )
        
        return result
    
    @staticmethod
    def set_translation(tenant, key, language_code, value):
        """Set a translation value."""
        try:
            with transaction.atomic():
                # Get or create translation key
                translation_key, _ = TranslationKey.objects.get_or_create(
                    key=key,
                    defaults={
                        'description': f'Auto-created key: {key}',
                        'default_value': value
                    }
                )
                
                # Get language
                language = Language.objects.get(code=language_code, is_active=True)
                
                # Create or update translation
                translation, created = Translation.objects.update_or_create(
                    tenant=tenant,
                    translation_key=translation_key,
                    language=language,
                    defaults={'value': value, 'is_active': True}
                )
                
                return {
                    'success': True,
                    'created': created,
                    'translation': translation
                }
                
        except Language.DoesNotExist:
            return {
                'success': False,
                'error': f'Language {language_code} not found or not active'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def import_translations(tenant, translations_data):
        """Import translations from a dictionary structure."""
        imported_count = 0
        errors = []
        
        try:
            with transaction.atomic():
                for key, language_values in translations_data.items():
                    for language_code, value in language_values.items():
                        result = TranslationService.set_translation(
                            tenant=tenant,
                            key=key,
                            language_code=language_code,
                            value=value
                        )
                        
                        if result['success']:
                            imported_count += 1
                        else:
                            errors.append(f"{key}:{language_code} - {result['error']}")
                
                return {
                    'success': len(errors) == 0,
                    'imported_count': imported_count,
                    'errors': errors
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'imported_count': imported_count
            }
    
    @staticmethod
    def export_translations(tenant, language_code):
        """Export translations for a specific language."""
        try:
            language = Language.objects.get(code=language_code, is_active=True)
            
            translations = Translation.objects.filter(
                tenant=tenant,
                language=language,
                is_active=True
            ).select_related('translation_key')
            
            result = {}
            for translation in translations:
                result[translation.translation_key.key] = translation.value
            
            return result
            
        except Language.DoesNotExist:
            return {}
    
    @staticmethod
    def get_supported_languages(tenant):
        """Get languages that have translations for this tenant."""
        # Get languages with translations for this tenant
        translated_languages = Language.objects.filter(
            translations__tenant=tenant,
            translations__is_active=True,
            is_active=True
        ).distinct()
        
        # Always include English as a supported language
        english = Language.objects.filter(code='en', is_active=True).first()
        
        languages = list(translated_languages)
        if english and english not in languages:
            languages.insert(0, english)
        
        return [
            {
                'code': lang.code,
                'name': lang.name,
                'native_name': lang.native_name,
                'is_rtl': lang.is_rtl
            }
            for lang in languages
        ]
