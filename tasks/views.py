from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db import connection
from .models import Task
from .serializers import TaskSerializer

# Create your views here.

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return Task.objects.filter(user=self.request.user).order_by('-created_at')[:4]
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def raw_retrieve(self, request, pk=None):
        """Retrieve a task using raw SQL"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, duration, status, created_at, updated_at, completed_at 
                FROM tasks_task 
                WHERE id = %s AND user_id = %s
            """, [pk, request.user.id])
            row = cursor.fetchone()
            
            if row:
                task = {
                    'id': row[0],
                    'title': row[1],
                    'duration': row[2],
                    'status': row[3],
                    'created_at': row[4],
                    'updated_at': row[5],
                    'completed_at': row[6]
                }
                return Response(task)
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['put'])
    def raw_update_title(self, request, pk=None):
        """Update only the title of a task using raw SQL"""
        if 'title' not in request.data:
            return Response(
                {'error': 'Title is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        new_title = request.data['title']
        
        with connection.cursor() as cursor:
            # checking if the task exists and belongs to the user
            cursor.execute("""
                SELECT id FROM tasks_task 
                WHERE id = %s AND user_id = %s
            """, [pk, request.user.id])
            
            if not cursor.fetchone():
                return Response(
                    {'error': 'Task not found or not authorized'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Update only the title
            cursor.execute("""
                UPDATE tasks_task 
                SET title = %s, updated_at = NOW() 
                WHERE id = %s AND user_id = %s
            """, [new_title, pk, request.user.id])
            
            if cursor.rowcount > 0:
                return Response({'message': 'Title updated successfully'})
            
            return Response(
                {'error': 'Failed to update title'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Delete a task if it belongs to the logged-in user"""
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
