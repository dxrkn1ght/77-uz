"""
API Usage Examples for 77.uz Marketplace

This file contains example requests and responses for the API endpoints.
"""

# Authentication Examples
LOGIN_EXAMPLE = {
    "request": {
        "phone_number": "+998901234567",
        "password": "mySecurePassword123"
    },
    "response": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 123,
            "full_name": "Aliyev Vali Karimovich",
            "phone_number": "+998901234567",
            "role": "user"
        }
    }
}

REGISTER_EXAMPLE = {
    "request": {
        "full_name": "Aliyev Vali Karimovich",
        "phone_number": "+998901234567",
        "password": "mySecurePassword123",
        "password_confirm": "mySecurePassword123"
    },
    "response": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id": 124,
            "full_name": "Aliyev Vali Karimovich",
            "phone_number": "+998901234567",
            "role": "user"
        }
    }
}

# Ad Examples
AD_CREATE_EXAMPLE = {
    "request": {
        "name_uz": "Samsung Galaxy S24 Ultra 512GB",
        "name_ru": "Samsung Galaxy S24 Ultra 512GB",
        "category": 15,
        "description_uz": "Eng so'nggi Samsung Galaxy S24 Ultra, 512GB xotira, S Pen bilan.",
        "description_ru": "Новейший Samsung Galaxy S24 Ultra, 512GB памяти, с S Pen.",
        "price": 12500000,
        "photos": ["base64_image_data_1", "base64_image_data_2"]
    },
    "response": {
        "id": 12345,
        "name": "Samsung Galaxy S24 Ultra 512GB",
        "slug": "samsung-galaxy-s24-ultra-512gb",
        "description": "Eng so'nggi Samsung Galaxy S24 Ultra...",
        "price": 12500000,
        "category": {
            "id": 15,
            "name": "Telefonlar"
        },
        "seller": {
            "id": 456,
            "full_name": "Karimov Akmal",
            "phone_number": "+998901234567"
        },
        "photos": [
            "https://admin.77.uz/media/ads/samsung_s24_1.jpg",
            "https://admin.77.uz/media/ads/samsung_s24_2.jpg"
        ],
        "is_liked": False,
        "view_count": 0,
        "published_at": "2024-01-15T10:30:00Z"
    }
}

# Category Examples
CATEGORIES_EXAMPLE = {
    "response": [
        {
            "id": 1,
            "name": "Elektronika",
            "slug": "elektronika",
            "icon": "https://admin.77.uz/media/categories/electronics.png",
            "children": [
                {
                    "id": 15,
                    "name": "Telefonlar",
                    "slug": "telefonlar",
                    "icon": None
                },
                {
                    "id": 16,
                    "name": "Kompyuterlar",
                    "slug": "kompyuterlar",
                    "icon": None
                }
            ]
        }
    ]
}
