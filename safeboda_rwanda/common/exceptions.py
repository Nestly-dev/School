"""
Custom exception handler for DRF
"""
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that adds additional context to error responses
    """
    # Call DRF's default exception handler first
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Add custom error format
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
                'status_code': response.status_code
            }
        }

        # Include original error details if available
        if hasattr(response, 'data'):
            custom_response_data['error']['details'] = response.data

        response.data = custom_response_data

    return response
