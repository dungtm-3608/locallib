from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext as _
from catalog.models import Book, Author, BookInstance
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from catalog.forms import RenewBookForm
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from catalog.enums import BookInstanceStatus
import catalog.constants as constants

def index(request):
    """View function for home page of site."""

    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact=BookInstanceStatus.AVAILABLE).count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + constants.ADD_NUM_VISITS

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    return render(request, 'index.html', context=context)

class BookListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing all books."""
    model = Book
    context_object_name = 'book_list'  
    queryset = Book.objects.filter(title__icontains='')  
    template_name = 'catalog/book_list.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['some_data'] = _("This is just some data")
        return context

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    model = Book


    def book_detail_view(request, primary_key):
        book = get_object_or_404(Book, pk=primary_key)
        return render(request, 'catalog/book_detail.html', context={'book': book})

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to the current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user,
            status=BookInstanceStatus.ON_LOAN
        ).order_by('due_back')
    
@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific book instance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('my-borrowed'))
    else: 
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreateView(CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {
        'date_of_birth': '01/01/1970',
        'date_of_death': '01/01/2020',
    }

class AuthorUpdateView(UpdateView):
    model = Author
    fields = ('first_name', 'last_name', 'date_of_birth', 'date_of_death')

class AuthorDeleteView(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class AuthorListView(generic.ListView):
    """Generic class-based view listing all authors."""
    model = Author
    context_object_name = 'author_list'
    template_name = 'catalog/author_list.html'
    paginate_by = 10
    queryset = Author.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['some_data'] = _("This is just some data")
        return context

class AuthorDetailView(generic.DetailView):
    """Generic class-based view for an author detail page."""
    model = Author

    def author_detail_view(request, primary_key):
        author = get_object_or_404(Author, pk=primary_key)
        return render(request, 'catalog/author_detail.html', context={'author': author})
