from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Tenant


@csrf_exempt
@require_http_methods(["GET"])
def validate_tenant(request, subdomain):
    """
    Validate if a subdomain corresponds to an existing tenant.
    This endpoint is used by the frontend middleware to check tenant validity.
    """
    try:
        tenant = Tenant.objects.get(schema_name=subdomain)
        return JsonResponse({
            'valid': True,
            'tenant_name': tenant.name,
            'schema_name': tenant.schema_name
        })
    except Tenant.DoesNotExist:
        return JsonResponse({'valid': False}, status=404)
