from django.db import models
from django.urls import reverse
from uuid import uuid4
from datetime import date
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _  

class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        help_text=_('Enter a book genre (e.g. Science Fiction)')
    )

    def __str__(self):
        return self.name
    
class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(
        max_length=200,
        help_text=_('Enter the title of the book')
    )
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(
        max_length=1000,
        help_text=_('Enter a brief description of the book')
    )
    isbn = models.CharField(
        _('ISBN'), 
        max_length=13,
        help_text=_('13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    )
    genre = models.ManyToManyField(
        Genre,
        help_text=_('Select a genre for this book')
    )

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/catalog/book/{self.id}/"
    
    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
    
class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        help_text=_('Unique ID for this particular book across whole library')
    )
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(
        max_length=200,
        help_text=_('Enter the imprint of the book')
    )
    due_back = models.DateField(
        null=True,
        blank=True,
        help_text=_('Enter the date when this book is due back')
    )
    borrower = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_('Select a borrower for this book')
    )
    LOAN_STATUS = (
        ('m', _('Maintenance')),
        ('o', _('On loan')),
        ('a', _('Available')),
        ('r', _('Reserved')),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text=_('Book availability'),
    )

    class Meta:
        ordering = ['due_back']
        permissions = (
            ("can_mark_returned", _("Set book as returned")), 
        )

    def __str__(self):
        return f'{self.id} ({self.book.title})'
    
    def is_overdue(self):
        """Determines if the book is overdue."""
        return self.due_back < date.today() if self.due_back else False
    
class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(
        max_length=100,
        help_text=_('Enter the author\'s first name')
    )
    last_name = models.CharField(
        max_length=100,
        help_text=_('Enter the author\'s last name')
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text=_('Enter the author\'s date of birth')
    )
    date_of_death = models.DateField(
        null=True,
        blank=True,
        help_text=_('Enter the author\'s date of death (if applicable)')
    )

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.last_name}, {self.first_name}'
