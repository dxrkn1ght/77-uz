from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class AuthenticatedUserThrottle(UserRateThrottle):
    """Rate limiting for authenticated users"""
    scope = 'authenticated_user'
    rate = '1000/hour'

class AnonymousUserThrottle(AnonRateThrottle):
    """Rate limiting for anonymous users"""
    scope = 'anonymous_user'
    rate = '100/hour'

class LoginThrottle(AnonRateThrottle):
    """Special rate limiting for login attempts"""
    scope = 'login'
    rate = '10/hour'

class RegistrationThrottle(AnonRateThrottle):
    """Rate limiting for registration attempts"""
    scope = 'registration'
    rate = '5/hour'
