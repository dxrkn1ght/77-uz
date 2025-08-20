from .base import *  # noqa

ALLOWED_HOSTS = ["*"]
DEBUG = True
CORS_ALLOW_ALL_ORIGINS = True

SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "[Bearer {JWT}]": {
            "name": "Authorization",
            "type": "apiKey",
            "in": "header",
        }
    },
    "USE_SESSION_AUTH": False,
    "APIS_SORTER": "alpha",
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "delete", "patch"],
    "OPERATIONS_SORTER": "alpha",
}


INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405