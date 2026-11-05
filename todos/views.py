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

    @extend_schema(operation_id='todo_list', responses=PaginatedTodoSerializer)
    def get(self, request):
        todos = Todo.objects.filter(user=request.user)

        # filtering only completed or incompleted todos
        is_completed = request.query_params.get('is_completed')
        if is_completed is not None:
            if is_completed.lower() not in ['true', 'false']:
                return Response(
                    {
                        "success": False,
                        "message": "Invalid query parameter.",
                        "errors": {
                            "is_completed": ["Must be either true or false."]
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            todos = todos.filter(is_completed=is_completed.lower() == 'true')

        # searching with keywords
        search_query = request.query_params.get('search')
        if search_query:
            todos = todos.filter(title__icontains=search_query)

        # sort the results
        sort_by = request.query_params.get('sort', '-created_at')

        allowed_sort_fields = [
            'created_at',
            '-created_at',
            'title',
            '-title',
            'is_completed',
            '-is_completed',
        ]

        # handle sorting
        if sort_by not in allowed_sort_fields:
            return Response(
                {
                    "success": False,
                    "message": "Invalid sorting parameter.",
                    "errors": {
                        "sort": [
                            f"Allowed values: {', '.join(allowed_sort_fields)}"
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        todos = todos.order_by(sort_by, '-id')

        # pagination
        paginator = TodoPagination()
        paginated_todos = paginator.paginate_queryset(todos, request)

        serializer = TodoSerializer(paginated_todos, many=True)

        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=TodoSerializer, responses={201: TodoSerializer})
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
        return get_object_or_404(Todo, pk=pk, user=self.request.user)

    @extend_schema(operation_id='todo_retrieve', responses=TodoSerializer)
    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(operation_id='todo_update', request=TodoSerializer, responses=TodoSerializer)
    def put(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(operation_id='todo_partial_update', request=TodoSerializer, responses=TodoSerializer)
    def patch(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(
            todo,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(operation_id='todo_delete', responses={204: None})
    def delete(self, request, pk):
        todo = self.get_object(pk)
        todo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    @extend_schema(operation_id='register_user', request=RegisterSerializer, responses={201: RegisterSerializer})
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