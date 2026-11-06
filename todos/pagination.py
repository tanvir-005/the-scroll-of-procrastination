from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from .serializers import TodoSerializer


class TodoPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'limit'
    max_page_size = 50

class PaginatedTodoSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = TodoSerializer(many=True)