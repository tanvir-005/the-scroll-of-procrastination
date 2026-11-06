from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import Todo
from .serializers import TodoSerializer
from .pagination import TodoPagination, PaginatedTodoSerializer
from .auth_serializers import RegisterSerializer
from .schema_serializers import RegisterResponseSerializer

class TodoListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        operation_id='todo_list',
        responses=PaginatedTodoSerializer
    )
    def get(self, request):
        todos = Todo.objects.filter(user=request.user)

        # Filter by status
        todo_status = request.query_params.get('status')

        if todo_status is not None:
            if todo_status not in ['completed', 'pending']:
                return Response(
                    {
                        "error": (
                            "Invalid status parameter. "
                            "Must be either 'completed' or 'pending'."
                        ),
                        "code": status.HTTP_400_BAD_REQUEST
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            todos = todos.filter(
                is_completed=(todo_status == 'completed')
            )

        # Search TODOs by title
        search_query = request.query_params.get('search')

        if search_query:
            todos = todos.filter(
                title__icontains=search_query.strip()
            )

        # Sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        order = request.query_params.get('order', 'desc')

        allowed_sort_fields = ['created_at', 'title']
        allowed_orders = ['asc', 'desc']

        if sort_by not in allowed_sort_fields:
            return Response(
                {
                    "error": (
                        "Invalid sorting field. "
                        "Allowed values: created_at, title."
                    ),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if order not in allowed_orders:
            return Response(
                {
                    "error": (
                        "Invalid sorting order. "
                        "Allowed values: asc, desc."
                    ),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        ordering = sort_by if order == 'asc' else f'-{sort_by}'
        todos = todos.order_by(ordering, '-id')

        # Pagination
        paginator = TodoPagination()
        paginated_todos = paginator.paginate_queryset(
            todos,
            request
        )

        serializer = TodoSerializer(
            paginated_todos,
            many=True
        )

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        request=TodoSerializer,
        responses={201: TodoSerializer}
    )
    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class TodoDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TodoSerializer

    def get_object(self, pk):
        return get_object_or_404(
            Todo,
            pk=pk,
            user=self.request.user
        )

    @extend_schema(
        operation_id='todo_retrieve',
        responses=TodoSerializer
    )
    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id='todo_update',
        request=TodoSerializer,
        responses=TodoSerializer
    )
    def put(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(
            todo,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id='todo_partial_update',
        request=TodoSerializer,
        responses=TodoSerializer
    )
    def patch(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(
            todo,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        operation_id='todo_delete',
        responses={204: None}
    )
    def delete(self, request, pk):
        todo = self.get_object(pk)
        todo.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(
        operation_id='register_user',
        request=RegisterSerializer,
        responses={201: RegisterSerializer}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            },
            status=status.HTTP_201_CREATED
        )