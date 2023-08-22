from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_LIMIT


class CustomPagination(PageNumberPagination):
    page_size = PAGE_LIMIT
