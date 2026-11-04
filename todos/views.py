from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Todo
from .serializers import TodoSerializer


class TodoListCreateView(APIView):

    def get(self, request):
        todos = Todo.objects.all()
        serializer = TodoSerializer(todos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TodoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class TodoDetailView(APIView):

    def get_object(self, pk):
        return get_object_or_404(Todo, pk=pk)

    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

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

    def delete(self, request, pk):
        todo = self.get_object(pk)
        todo.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)