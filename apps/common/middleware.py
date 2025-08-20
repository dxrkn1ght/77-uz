import time
import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # Content Security Policy
        if not settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self';"
            )
        
        return response

class RateLimitMiddleware(MiddlewareMixin):
    """Rate limiting middleware"""
    
    def process_request(self, request):
        if self.should_skip_rate_limit(request):
            return None
            
        client_ip = self.get_client_ip(request)
        user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None
        
        # Different limits for authenticated vs anonymous users
        if user_id:
            rate_limit_key = f"rate_limit_user_{user_id}"
            max_requests = 1000  # 1000 requests per hour for authenticated users
        else:
            rate_limit_key = f"rate_limit_ip_{client_ip}"
            max_requests = 100   # 100 requests per hour for anonymous users
        
        current_requests = cache.get(rate_limit_key, 0)
        
        if current_requests >= max_requests:
            logger.warning(f"Rate limit exceeded for {'user ' + str(user_id) if user_id else 'IP ' + client_ip}")
            return JsonResponse(
                {'error': 'Rate limit exceeded. Try again later.'},
                status=429
            )
        
        # Increment counter
        cache.set(rate_limit_key, current_requests + 1, 3600)  # 1 hour expiry
        
        return None
    
    def should_skip_rate_limit(self, request):
        """Skip rate limiting for certain paths"""
        skip_paths = ['/admin/', '/api/docs/', '/api/schema/']
        return any(request.path.startswith(path) for path in skip_paths)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RequestLoggingMiddleware(MiddlewareMixin):
    """Log API requests for security monitoring"""
    
    def process_request(self, request):
        request.start_time = time.time()
        
        # Log suspicious requests
        if self.is_suspicious_request(request):
            logger.warning(
                f"Suspicious request: {request.method} {request.path} "
                f"from {self.get_client_ip(request)} "
                f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
            )
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests
            if duration > 2.0:  # Log requests taking more than 2 seconds
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s"
                )
        
        return response
    
    def is_suspicious_request(self, request):
        """Detect potentially suspicious requests"""
        suspicious_patterns = [
            'script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
            '<script', '</script>', 'eval(', 'document.cookie'
        ]
        
        # Check query parameters and POST data
        query_string = request.META.get('QUERY_STRING', '').lower()
        
        return any(pattern in query_string for pattern in suspicious_patterns)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
