from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = JWTAuthentication
    name = 'jwtAuth'
    
    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix='Bearer',
        )
