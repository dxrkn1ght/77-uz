import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from apps.common.models import Address
from apps.store.models import Category, Ad, AdPhoto
from apps.accounts.models import SellerProfile


User = get_user_model()

class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address
    
    name = factory.Faker('address')
    lat = factory.Faker('latitude')
    long = factory.Faker('longitude')

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    phone_number = factory.Sequence(lambda n: f'+99890123456{n:02d}')
    full_name = factory.Faker('name')
    role = 'user'
    is_active = True
    address = factory.SubFactory(AddressFactory)

class AdminUserFactory(UserFactory):
    role = 'admin'
    is_staff = True

class SuperAdminUserFactory(UserFactory):
    role = 'super_admin'
    is_staff = True
    is_superuser = True

class SellerUserFactory(UserFactory):
    role = 'seller'

class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
    
    name_uz = factory.Faker('word')
    name_ru = factory.Faker('word')
    slug = factory.LazyAttribute(lambda obj: obj.name_uz.lower())
    is_active = True
    order = factory.Sequence(lambda n: n)

class SubCategoryFactory(CategoryFactory):
    parent = factory.SubFactory(CategoryFactory)

class SellerProfileFactory(DjangoModelFactory):
    class Meta:
        model = SellerProfile
    
    user = factory.SubFactory(SellerUserFactory)
    project_name = factory.Faker('company')
    category = factory.SubFactory(CategoryFactory)
    is_approved = True

class AdFactory(DjangoModelFactory):
    class Meta:
        model = Ad
    
    name_uz = factory.Faker('sentence', nb_words=3)
    name_ru = factory.Faker('sentence', nb_words=3)
    slug = factory.LazyAttribute(lambda obj: obj.name_uz.lower().replace(' ', '-'))
    description_uz = factory.Faker('text')
    description_ru = factory.Faker('text')
    price = factory.Faker('random_int', min=10000, max=10000000)
    category = factory.SubFactory(CategoryFactory)
    seller = factory.SubFactory(SellerUserFactory)
    is_active = True

class AdPhotoFactory(DjangoModelFactory):
    class Meta:
        model = AdPhoto
    
    ad = factory.SubFactory(AdFactory)
    image = factory.django.ImageField()
    order = factory.Sequence(lambda n: n)
