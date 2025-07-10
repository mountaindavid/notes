from notes.models import Note
from django.contrib.auth.models import User
from django.test import TestCase



class NoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.note = Note.objects.create(title='Test Note', content='This is a test note', user=self.user) # type: ignore

    def test_note_creation(self):
        saved_note = Note.objects.get(id=self.note.id) # type: ignore
        self.assertEqual(saved_note.title, 'Test Note')
        self.assertEqual(saved_note.content, 'This is a test note')
        self.assertEqual(saved_note.user, self.user)
        self.assertIsNotNone(saved_note.created_at)
        self.assertIsNotNone(saved_note.updated_at)

    def test_note_str(self):
        self.assertEqual(str(self.note), 'Test Note')

    def test_note_update(self):
        self.note.title = 'Updated Title'
        self.note.content = 'Updated Content'
        self.note.save()
        saved_note = Note.objects.get(id=self.note.id) # type: ignore
        self.assertEqual(saved_note.title, 'Updated Title')
        self.assertEqual(saved_note.content, 'Updated Content')
        self.assertIsNotNone(saved_note.updated_at)

    def test_note_deletion(self):
        self.note.delete()
        with self.assertRaises(Note.DoesNotExist): # type: ignore
            Note.objects.get(id=self.note.id) # type: ignore
            
        