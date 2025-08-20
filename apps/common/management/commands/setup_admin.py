from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.common.models import Address
from apps.store.models import Category

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup initial admin user and sample data'

    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, help='Admin phone number', default='+998901234567')
        parser.add_argument('--password', type=str, help='Admin password', default='admin123')

    def handle(self, *args, **options):
        phone = options['phone']
        password = options['password']

        # Create super admin user
        if not User.objects.filter(phone_number=phone).exists():
            admin_address = Address.objects.create(
                name="Toshkent shahar, Chilonzor tumani / г. Ташкент, Чиланзарский район"
            )
            
            admin_user = User.objects.create_user(
                phone_number=phone,
                password=password,
                full_name="Super Administrator",
                role='super_admin',
                is_staff=True,
                is_superuser=True,
                is_verified=True,
                address=admin_address
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Super admin created: {phone} / {password}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'User with phone {phone} already exists')
            )

        # Create sample categories
        categories_data = [
            {
                'name_uz': 'Elektronika',
                'name_ru': 'Электроника',
                'children': [
                    {'name_uz': 'Telefonlar', 'name_ru': 'Телефоны'},
                    {'name_uz': 'Kompyuterlar', 'name_ru': 'Компьютеры'},
                    {'name_uz': 'Televizorlar', 'name_ru': 'Телевизоры'},
                ]
            },
            {
                'name_uz': 'Kiyim-kechak',
                'name_ru': 'Одежда',
                'children': [
                    {'name_uz': 'Erkaklar kiyimi', 'name_ru': 'Мужская одежда'},
                    {'name_uz': 'Ayollar kiyimi', 'name_ru': 'Женская одежда'},
                    {'name_uz': 'Bolalar kiyimi', 'name_ru': 'Детская одежда'},
                ]
            },
            {
                'name_uz': 'Uy-joy',
                'name_ru': 'Дом и сад',
                'children': [
                    {'name_uz': 'Mebel', 'name_ru': 'Мебель'},
                    {'name_uz': 'Maishiy texnika', 'name_ru': 'Бытовая техника'},
                    {'name_uz': 'Dekoratsiya', 'name_ru': 'Декор'},
                ]
            }
        ]

        for cat_data in categories_data:
            parent_cat, created = Category.objects.get_or_create(
                name_uz=cat_data['name_uz'],
                defaults={
                    'name_ru': cat_data['name_ru'],
                    'slug': cat_data['name_uz'].lower().replace(' ', '-'),
                    'is_active': True,
                    'order': 0
                }
            )
            
            if created:
                self.stdout.write(f'Created category: {parent_cat.name_uz}')
            
            for i, child_data in enumerate(cat_data['children']):
                child_cat, created = Category.objects.get_or_create(
                    name_uz=child_data['name_uz'],
                    parent=parent_cat,
                    defaults={
                        'name_ru': child_data['name_ru'],
                        'slug': child_data['name_uz'].lower().replace(' ', '-'),
                        'is_active': True,
                        'order': i
                    }
                )
                
                if created:
                    self.stdout.write(f'  Created subcategory: {child_cat.name_uz}')

        self.stdout.write(
            self.style.SUCCESS('Setup completed successfully!')
        )
