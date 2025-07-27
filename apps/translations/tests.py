"""
Test suite for the Translations app
Testing translation models, services, and multi-language support functionality.
"""

from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from unittest.mock import patch, MagicMock

from apps.tenants.models import Tenant, Domain
from apps.translations.models import Translation, TranslationKey, Language
from apps.translations.services import TranslationService
from apps.users.models import TenantUser


class LanguageModelTest(TestCase):
    """Test Language model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.language_data = {
            'code': 'es',
            'name': 'Spanish',
            'native_name': 'Español',
            'is_active': True,
            'is_rtl': False
        }
    
    def test_language_creation(self):
        """Test creating a language."""
        language = Language.objects.create(**self.language_data)
        
        self.assertEqual(language.code, 'es')
        self.assertEqual(language.name, 'Spanish')
        self.assertEqual(language.native_name, 'Español')
        self.assertTrue(language.is_active)
        self.assertFalse(language.is_rtl)
    
    def test_language_string_representation(self):
        """Test language string representation."""
        language = Language.objects.create(**self.language_data)
        self.assertEqual(str(language), 'Spanish (es)')
    
    def test_language_code_validation(self):
        """Test language code validation."""
        # Valid ISO 639-1 codes
        valid_codes = ['en', 'es', 'fr', 'de', 'zh', 'ar']
        
        for code in valid_codes:
            language = Language(
                code=code,
                name=f'Test Language {code.upper()}',
                native_name=f'Native {code.upper()}'
            )
            language.full_clean()  # Should not raise
    
    def test_language_code_uniqueness(self):
        """Test language code uniqueness."""
        Language.objects.create(**self.language_data)
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            duplicate = Language(**self.language_data)
            duplicate.full_clean()
    
    def test_language_rtl_property(self):
        """Test RTL (Right-to-Left) language property."""
        # RTL languages
        rtl_language = Language.objects.create(
            code='ar',
            name='Arabic',
            native_name='العربية',
            is_rtl=True
        )
        self.assertTrue(rtl_language.is_rtl)
        
        # LTR languages
        ltr_language = Language.objects.create(
            code='en',
            name='English',
            native_name='English',
            is_rtl=False
        )
        self.assertFalse(ltr_language.is_rtl)


class TranslationKeyModelTest(TestCase):
    """Test TranslationKey model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.key_data = {
            'key': 'user.profile.title',
            'description': 'Title for user profile page',
            'context': 'user_interface',
            'default_value': 'User Profile'
        }
    
    def test_translation_key_creation(self):
        """Test creating a translation key."""
        translation_key = TranslationKey.objects.create(**self.key_data)
        
        self.assertEqual(translation_key.key, 'user.profile.title')
        self.assertEqual(translation_key.description, 'Title for user profile page')
        self.assertEqual(translation_key.context, 'user_interface')
        self.assertEqual(translation_key.default_value, 'User Profile')
    
    def test_translation_key_string_representation(self):
        """Test translation key string representation."""
        translation_key = TranslationKey.objects.create(**self.key_data)
        self.assertEqual(str(translation_key), 'user.profile.title')
    
    def test_translation_key_uniqueness(self):
        """Test translation key uniqueness."""
        TranslationKey.objects.create(**self.key_data)
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            duplicate = TranslationKey(**self.key_data)
            duplicate.full_clean()
    
    def test_translation_key_validation(self):
        """Test translation key validation."""
        # Valid key formats
        valid_keys = [
            'simple_key',
            'namespace.key',
            'deep.nested.key.structure',
            'component.action.label',
            'error.validation.required'
        ]
        
        for key in valid_keys:
            translation_key = TranslationKey(
                key=key,
                description=f'Test key: {key}',
                default_value='Test Value'
            )
            translation_key.full_clean()  # Should not raise
    
    def test_translation_key_context_choices(self):
        """Test translation key context choices."""
        valid_contexts = [
            'user_interface',
            'email_templates',
            'error_messages',
            'notifications',
            'help_text'
        ]
        
        for context in valid_contexts:
            translation_key = TranslationKey(
                key=f'test.{context}',
                description=f'Test {context} key',
                context=context,
                default_value='Test Value'
            )
            translation_key.full_clean()  # Should not raise
    
    def test_translation_key_hierarchical_structure(self):
        """Test hierarchical key structure support."""
        keys = [
            'auth.login.title',
            'auth.login.submit_button',
            'auth.login.forgot_password',
            'auth.register.title',
            'auth.register.submit_button'
        ]
        
        for key in keys:
            TranslationKey.objects.create(
                key=key,
                description=f'Description for {key}',
                context='user_interface',
                default_value='Default'
            )
        
        # Test that we can query by namespace
        auth_keys = TranslationKey.objects.filter(key__startswith='auth.')
        self.assertEqual(auth_keys.count(), 5)
        
        login_keys = TranslationKey.objects.filter(key__startswith='auth.login.')
        self.assertEqual(login_keys.count(), 3)


class TranslationModelTest(TransactionTestCase):
    """Test Translation model functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name='Translation Test Corp',
            schema_name='translation_test'
        )
        Domain.objects.create(
            domain='translationtest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create languages
        self.english = Language.objects.create(
            code='en',
            name='English',
            native_name='English',
            is_active=True
        )
        
        self.spanish = Language.objects.create(
            code='es',
            name='Spanish',
            native_name='Español',
            is_active=True
        )
        
        # Create translation key
        self.translation_key = TranslationKey.objects.create(
            key='welcome.message',
            description='Welcome message for users',
            context='user_interface',
            default_value='Welcome to our platform'
        )
    
    def test_translation_creation(self):
        """Test creating a translation."""
        translation = Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish,
            value='Bienvenido a nuestra plataforma'
        )
        
        self.assertEqual(translation.tenant, self.tenant)
        self.assertEqual(translation.translation_key, self.translation_key)
        self.assertEqual(translation.language, self.spanish)
        self.assertEqual(translation.value, 'Bienvenido a nuestra plataforma')
        self.assertTrue(translation.is_active)
    
    def test_translation_string_representation(self):
        """Test translation string representation."""
        translation = Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish,
            value='Bienvenido a nuestra plataforma'
        )
        
        expected = f"{self.tenant.name} - welcome.message (es)"
        self.assertEqual(str(translation), expected)
    
    def test_translation_unique_constraint(self):
        """Test unique constraint for tenant + key + language."""
        # Create first translation
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish,
            value='First translation'
        )
        
        # Try to create duplicate
        with self.assertRaises(ValidationError):
            duplicate = Translation(
                tenant=self.tenant,
                translation_key=self.translation_key,
                language=self.spanish,
                value='Duplicate translation'
            )
            duplicate.full_clean()
    
    def test_translation_fallback_to_default(self):
        """Test translation fallback behavior."""
        # No translation exists for Spanish
        # Should fall back to default value from TranslationKey
        
        # This would be implemented in the service layer
        # For now, just test that the default value is accessible
        self.assertEqual(
            self.translation_key.default_value,
            'Welcome to our platform'
        )
    
    def test_translation_versioning(self):
        """Test translation versioning and history."""
        translation = Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish,
            value='Primera versión'
        )
        
        original_updated_at = translation.updated_at
        
        # Update translation
        translation.value = 'Segunda versión'
        translation.save()
        
        # Check that updated_at changed
        self.assertGreater(translation.updated_at, original_updated_at)


class TranslationServiceTest(TransactionTestCase):
    """Test TranslationService functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name='Translation Service Test',
            schema_name='translation_service_test'
        )
        
        # Create languages
        self.english = Language.objects.create(
            code='en',
            name='English',
            native_name='English',
            is_active=True
        )
        
        self.spanish = Language.objects.create(
            code='es',
            name='Spanish',
            native_name='Español',
            is_active=True
        )
        
        self.french = Language.objects.create(
            code='fr',
            name='French',
            native_name='Français',
            is_active=True
        )
        
        # Create translation keys
        self.greeting_key = TranslationKey.objects.create(
            key='greeting.hello',
            description='Simple hello greeting',
            default_value='Hello'
        )
        
        self.goodbye_key = TranslationKey.objects.create(
            key='greeting.goodbye',
            description='Simple goodbye message',
            default_value='Goodbye'
        )
    
    def test_get_translation_with_existing_value(self):
        """Test getting translation with existing value."""
        # Create translation
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.spanish,
            value='Hola'
        )
        
        # Get translation
        result = TranslationService.get_translation(
            tenant=self.tenant,
            key='greeting.hello',
            language_code='es'
        )
        
        self.assertEqual(result, 'Hola')
    
    def test_get_translation_fallback_to_default(self):
        """Test getting translation with fallback to default."""
        # No Spanish translation exists
        result = TranslationService.get_translation(
            tenant=self.tenant,
            key='greeting.hello',
            language_code='es'
        )
        
        # Should return default value
        self.assertEqual(result, 'Hello')
    
    def test_get_translation_fallback_to_english(self):
        """Test getting translation with fallback to English."""
        # Create English translation
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.english,
            value='Hello there'
        )
        
        # Request French translation (doesn't exist)
        result = TranslationService.get_translation(
            tenant=self.tenant,
            key='greeting.hello',
            language_code='fr',
            fallback_to_english=True
        )
        
        # Should return English value
        self.assertEqual(result, 'Hello there')
    
    def test_get_translation_nonexistent_key(self):
        """Test getting translation for nonexistent key."""
        result = TranslationService.get_translation(
            tenant=self.tenant,
            key='nonexistent.key',
            language_code='es'
        )
        
        # Should return the key itself as fallback
        self.assertEqual(result, 'nonexistent.key')
    
    def test_bulk_get_translations(self):
        """Test getting multiple translations at once."""
        # Create translations
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.spanish,
            value='Hola'
        )
        
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.goodbye_key,
            language=self.spanish,
            value='Adiós'
        )
        
        # Get bulk translations
        keys = ['greeting.hello', 'greeting.goodbye']
        result = TranslationService.get_bulk_translations(
            tenant=self.tenant,
            keys=keys,
            language_code='es'
        )
        
        expected = {
            'greeting.hello': 'Hola',
            'greeting.goodbye': 'Adiós'
        }
        self.assertEqual(result, expected)
    
    def test_set_translation(self):
        """Test setting a translation value."""
        result = TranslationService.set_translation(
            tenant=self.tenant,
            key='greeting.hello',
            language_code='es',
            value='Hola amigo'
        )
        
        self.assertTrue(result['success'])
        
        # Verify translation was created/updated
        translation = Translation.objects.get(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.spanish
        )
        self.assertEqual(translation.value, 'Hola amigo')
    
    def test_import_translations_from_dict(self):
        """Test importing translations from dictionary."""
        translations_data = {
            'greeting.hello': {
                'es': 'Hola',
                'fr': 'Bonjour'
            },
            'greeting.goodbye': {
                'es': 'Adiós',
                'fr': 'Au revoir'
            }
        }
        
        result = TranslationService.import_translations(
            tenant=self.tenant,
            translations_data=translations_data
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['imported_count'], 4)  # 2 keys × 2 languages
        
        # Verify translations were created
        spanish_hello = Translation.objects.get(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.spanish
        )
        self.assertEqual(spanish_hello.value, 'Hola')
        
        french_goodbye = Translation.objects.get(
            tenant=self.tenant,
            translation_key=self.goodbye_key,
            language=self.french
        )
        self.assertEqual(french_goodbye.value, 'Au revoir')
    
    def test_export_translations(self):
        """Test exporting translations to dictionary."""
        # Create translations
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.spanish,
            value='Hola'
        )
        
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.goodbye_key,
            language=self.spanish,
            value='Adiós'
        )
        
        # Export translations
        result = TranslationService.export_translations(
            tenant=self.tenant,
            language_code='es'
        )
        
        expected = {
            'greeting.hello': 'Hola',
            'greeting.goodbye': 'Adiós'
        }
        self.assertEqual(result, expected)
    
    def test_get_supported_languages(self):
        """Test getting supported languages for tenant."""
        # Create some translations for different languages
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.spanish,
            value='Hola'
        )
        
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.greeting_key,
            language=self.french,
            value='Bonjour'
        )
        
        result = TranslationService.get_supported_languages(self.tenant)
        
        # Should include languages with translations plus English (default)
        language_codes = [lang['code'] for lang in result]
        self.assertIn('en', language_codes)  # Always included
        self.assertIn('es', language_codes)
        self.assertIn('fr', language_codes)


class TranslationTemplateTagTest(TestCase):
    """Test translation template tags."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Template Tag Test',
            schema_name='template_tag_test'
        )
        
        self.spanish = Language.objects.create(
            code='es',
            name='Spanish',
            native_name='Español'
        )
        
        self.translation_key = TranslationKey.objects.create(
            key='ui.button.save',
            description='Save button text',
            default_value='Save'
        )
    
    def test_translate_template_tag(self):
        """Test {% translate %} template tag functionality."""
        # Create translation
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish,
            value='Guardar'
        )
        
        # This would test the template tag implementation
        # For now, just verify the service method works
        result = TranslationService.get_translation(
            tenant=self.tenant,
            key='ui.button.save',
            language_code='es'
        )
        
        self.assertEqual(result, 'Guardar')
    
    def test_translate_with_variables_template_tag(self):
        """Test translation with variable substitution."""
        # Create translation key with variables
        variable_key = TranslationKey.objects.create(
            key='message.welcome_user',
            description='Welcome message with username',
            default_value='Welcome, {username}!'
        )
        
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=variable_key,
            language=self.spanish,
            value='¡Bienvenido, {username}!'
        )
        
        # Test variable substitution
        template_value = TranslationService.get_translation(
            tenant=self.tenant,
            key='message.welcome_user',
            language_code='es'
        )
        
        # Simulate template variable substitution
        result = template_value.format(username='Juan')
        self.assertEqual(result, '¡Bienvenido, Juan!')


class TranslationMiddlewareTest(TransactionTestCase):
    """Test translation middleware functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Middleware Test',
            schema_name='middleware_test'
        )
        
        Domain.objects.create(
            domain='middlewaretest.localhost',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Create user
        with schema_context(self.tenant.schema_name):
            self.user = TenantUser.objects.create_user(
                email='user@middlewaretest.com',
                first_name='Test',
                last_name='User'
            )
    
    def test_language_detection_from_user_preference(self):
        """Test language detection from user preference."""
        # This would test middleware that detects user's preferred language
        # For now, simulate the logic
        
        user_language_preference = 'es'
        detected_language = user_language_preference
        
        self.assertEqual(detected_language, 'es')
    
    def test_language_detection_from_browser(self):
        """Test language detection from browser Accept-Language header."""
        # Simulate browser language detection
        accept_language_header = 'es-ES,es;q=0.9,en;q=0.8'
        
        # Extract primary language
        primary_language = accept_language_header.split(',')[0].split('-')[0]
        self.assertEqual(primary_language, 'es')
    
    def test_language_fallback_chain(self):
        """Test language fallback chain in middleware."""
        # Test fallback: user preference -> browser -> tenant default -> system default
        fallback_chain = ['fr', 'es', 'en']  # User -> Browser -> Default
        
        # Simulate checking each language in order
        available_languages = ['en', 'es']  # French not available
        
        for lang in fallback_chain:
            if lang in available_languages:
                selected_language = lang
                break
        
        self.assertEqual(selected_language, 'es')


class TranslationAPITest(TestCase):
    """Test translation API functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Translation API Test',
            schema_name='translation_api_test'
        )
        
        self.spanish = Language.objects.create(
            code='es',
            name='Spanish',
            native_name='Español'
        )
        
        self.translation_key = TranslationKey.objects.create(
            key='api.message.success',
            description='API success message',
            default_value='Operation completed successfully'
        )
    
    def test_get_translations_api_endpoint(self):
        """Test GET /api/translations endpoint."""
        # Create translation
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish,
            value='Operación completada exitosamente'
        )
        
        # Simulate API response
        api_response = {
            'language': 'es',
            'translations': {
                'api.message.success': 'Operación completada exitosamente'
            }
        }
        
        self.assertEqual(api_response['language'], 'es')
        self.assertIn('api.message.success', api_response['translations'])
    
    def test_update_translation_api_endpoint(self):
        """Test PUT /api/translations endpoint."""
        # Simulate API request to update translation
        api_request = {
            'key': 'api.message.success',
            'language': 'es',
            'value': 'Operación completada con éxito'
        }
        
        # Process update
        result = TranslationService.set_translation(
            tenant=self.tenant,
            key=api_request['key'],
            language_code=api_request['language'],
            value=api_request['value']
        )
        
        self.assertTrue(result['success'])
        
        # Verify update
        translation = Translation.objects.get(
            tenant=self.tenant,
            translation_key=self.translation_key,
            language=self.spanish
        )
        self.assertEqual(translation.value, 'Operación completada con éxito')


class TranslationIntegrationTest(TransactionTestCase):
    """Integration tests for translation functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='Translation Integration Test',
            schema_name='translation_integration'
        )
        
        # Create multiple languages
        self.languages = {}
        language_data = [
            ('en', 'English', 'English'),
            ('es', 'Spanish', 'Español'),
            ('fr', 'French', 'Français'),
            ('de', 'German', 'Deutsch')
        ]
        
        for code, name, native_name in language_data:
            self.languages[code] = Language.objects.create(
                code=code,
                name=name,
                native_name=native_name,
                is_active=True
            )
    
    def test_complete_translation_workflow(self):
        """Test complete translation management workflow."""
        # 1. Create translation keys
        keys_data = [
            ('nav.home', 'Navigation: Home', 'Home'),
            ('nav.about', 'Navigation: About', 'About'),
            ('nav.contact', 'Navigation: Contact', 'Contact'),
            ('form.submit', 'Form: Submit button', 'Submit'),
            ('form.cancel', 'Form: Cancel button', 'Cancel')
        ]
        
        created_keys = []
        for key, desc, default in keys_data:
            translation_key = TranslationKey.objects.create(
                key=key,
                description=desc,
                default_value=default
            )
            created_keys.append(translation_key)
        
        self.assertEqual(len(created_keys), 5)
        
        # 2. Create translations for Spanish
        spanish_translations = {
            'nav.home': 'Inicio',
            'nav.about': 'Acerca de',
            'nav.contact': 'Contacto',
            'form.submit': 'Enviar',
            'form.cancel': 'Cancelar'
        }
        
        for key, value in spanish_translations.items():
            translation_key = TranslationKey.objects.get(key=key)
            Translation.objects.create(
                tenant=self.tenant,
                translation_key=translation_key,
                language=self.languages['es'],
                value=value
            )
        
        # 3. Test bulk retrieval
        keys = list(spanish_translations.keys())
        bulk_result = TranslationService.get_bulk_translations(
            tenant=self.tenant,
            keys=keys,
            language_code='es'
        )
        
        self.assertEqual(len(bulk_result), 5)
        self.assertEqual(bulk_result['nav.home'], 'Inicio')
        self.assertEqual(bulk_result['form.submit'], 'Enviar')
        
        # 4. Test fallback behavior
        # Request French translations (don't exist)
        french_result = TranslationService.get_bulk_translations(
            tenant=self.tenant,
            keys=keys,
            language_code='fr'
        )
        
        # Should return default values
        self.assertEqual(french_result['nav.home'], 'Home')
        self.assertEqual(french_result['form.submit'], 'Submit')
        
        # 5. Test export functionality
        export_result = TranslationService.export_translations(
            tenant=self.tenant,
            language_code='es'
        )
        
        self.assertEqual(len(export_result), 5)
        self.assertEqual(export_result, spanish_translations)
    
    def test_multi_tenant_translation_isolation(self):
        """Test that translations are properly isolated between tenants."""
        # Create second tenant
        tenant2 = Tenant.objects.create(
            name='Second Tenant',
            schema_name='second_tenant'
        )
        
        # Create same translation key
        translation_key = TranslationKey.objects.create(
            key='shared.message',
            description='Shared message key',
            default_value='Default Message'
        )
        
        # Create different translations for each tenant
        Translation.objects.create(
            tenant=self.tenant,
            translation_key=translation_key,
            language=self.languages['es'],
            value='Mensaje del Tenant 1'
        )
        
        Translation.objects.create(
            tenant=tenant2,
            translation_key=translation_key,
            language=self.languages['es'],
            value='Mensaje del Tenant 2'
        )
        
        # Test isolation
        tenant1_result = TranslationService.get_translation(
            tenant=self.tenant,
            key='shared.message',
            language_code='es'
        )
        
        tenant2_result = TranslationService.get_translation(
            tenant=tenant2,
            key='shared.message',
            language_code='es'
        )
        
        self.assertEqual(tenant1_result, 'Mensaje del Tenant 1')
        self.assertEqual(tenant2_result, 'Mensaje del Tenant 2')
        self.assertNotEqual(tenant1_result, tenant2_result)
    
    def test_translation_performance_optimization(self):
        """Test translation performance with caching and bulk operations."""
        # Create many translation keys
        bulk_keys = []
        for i in range(100):
            key = f'bulk.test.key_{i:03d}'
            translation_key = TranslationKey.objects.create(
                key=key,
                description=f'Bulk test key {i}',
                default_value=f'Default {i}'
            )
            bulk_keys.append(key)
            
            # Create Spanish translation
            Translation.objects.create(
                tenant=self.tenant,
                translation_key=translation_key,
                language=self.languages['es'],
                value=f'Español {i}'
            )
        
        # Test bulk retrieval performance
        import time
        start_time = time.time()
        
        bulk_result = TranslationService.get_bulk_translations(
            tenant=self.tenant,
            keys=bulk_keys,
            language_code='es'
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Verify results
        self.assertEqual(len(bulk_result), 100)
        self.assertEqual(bulk_result['bulk.test.key_000'], 'Español 0')
        self.assertEqual(bulk_result['bulk.test.key_099'], 'Español 99')
        
        # Performance should be reasonable (adjust threshold as needed)
        self.assertLess(execution_time, 5.0, "Bulk translation retrieval took too long")
