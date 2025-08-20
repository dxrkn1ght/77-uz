from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.conf import settings

@extend_schema(
    responses={
        200: OpenApiResponse(
            description='API information',
            examples={
                'application/json': {
                    'name': '77.uz Marketplace API',
                    'version': '1.0.0',
                    'description': 'Online marketplace platform API',
                    'documentation': '/api/docs/',
                    'schema': '/api/schema/',
                    'maintenance_mode': False,
                    'supported_languages': ['uz', 'ru'],
                    'contact': {
                        'email': 'info@uic.group'
                    }
                }
            }
        )
    },
    summary='API Information',
    description='Get basic API information and status',
    tags=['common']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_info(request):
    """Get API information and status"""
    return Response({
        'name': '77.uz Marketplace API',
        'version': '1.0.0',
        'description': 'Online marketplace platform API',
        'documentation': '/api/docs/',
        'schema': '/api/schema/',
        'maintenance_mode': False,
        'supported_languages': ['uz', 'ru'],
        'contact': {
            'email': 'info@uic.group'
        }
    })

@extend_schema(
    responses={
        200: OpenApiResponse(
            description='Health check status',
            examples={
                'application/json': {
                    'status': 'healthy',
                    'timestamp': '2024-01-15T10:30:00Z',
                    'version': '1.0.0'
                }
            }
        )
    },
    summary='Health Check',
    description='Check API health status',
    tags=['common']
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    from django.utils import timezone
    
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })
