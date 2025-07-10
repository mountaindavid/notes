from rest_framework import generics
from .models import Note
from .serializers import NoteSerializer
from users.permissions import JWTAuthentication


class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user) # type: ignore

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user) # type: ignore



