"""
OpenAPI schema customization for drf-spectacular.
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import serializers


# Response schemas for common patterns

class ErrorResponseSerializer(serializers.Serializer):
    """Generic error response."""

    detail = serializers.CharField()


class PaginatedResponseSerializer(serializers.Serializer):
    """Paginated response wrapper."""

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField()


# Common parameters

authentication_header = OpenApiParameter(
    name="Authorization",
    in_="header",
    description="JWT token authentication (Bearer <token>)",
    required=True,
    schema={"type": "string", "pattern": "^Bearer .+$"},
)

date_range_parameters = [
    OpenApiParameter(
        name="start_date",
        in_="query",
        description="Start date in YYYY-MM-DD format",
        required=False,
        schema={"type": "string", "format": "date"},
    ),
    OpenApiParameter(
        name="end_date",
        in_="query",
        description="End date in YYYY-MM-DD format",
        required=False,
        schema={"type": "string", "format": "date"},
    ),
]

pagination_parameters = [
    OpenApiParameter(
        name="page",
        in_="query",
        description="Page number (default: 1)",
        required=False,
        schema={"type": "integer", "minimum": 1},
    ),
    OpenApiParameter(
        name="page_size",
        in_="query",
        description="Number of results per page (default: 50, max: 100)",
        required=False,
        schema={"type": "integer", "minimum": 1, "maximum": 100},
    ),
]

search_parameter = OpenApiParameter(
    name="search",
    in_="query",
    description="Search query string",
    required=False,
    schema={"type": "string"},
)

ordering_parameter = OpenApiParameter(
    name="ordering",
    in_="query",
    description="Ordering field (prefix with - for descending)",
    required=False,
    schema={"type": "string"},
)

# Extend schema decorators for common endpoints

def list_endpoint(description: str, parameters: list = None):
    """Decorator for list endpoints."""
    params = pagination_parameters.copy()
    if parameters:
        params.extend(parameters)
    return extend_schema(
        description=description,
        parameters=params,
    )


def create_endpoint(description: str):
    """Decorator for create endpoints."""
    return extend_schema(description=description)


def retrieve_endpoint(description: str):
    """Decorator for retrieve endpoints."""
    return extend_schema(description=description)


def update_endpoint(description: str):
    """Decorator for update endpoints."""
    return extend_schema(
        description=description,
        request=None,  # Let the serializer handle this
    )


def destroy_endpoint(description: str):
    """Decorator for delete endpoints."""
    return extend_schema(description=description)
