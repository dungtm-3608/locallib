from django.contrib import admin
from .models import Author, Book, Genre, BookInstance

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

class BookInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BookInstanceInline]

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id', 'borrower')
    list_filter = ('status', 'due_back')

    fieldsets = (
        (
            None,
            {
                'fields': ('book', 'imprint', 'id')
            }
        ),
        (
            'Availability',
            {
                'fields': ('borrower', 'status', 'due_back')
            }
        )
    )
