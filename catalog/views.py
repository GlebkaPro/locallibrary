from django.shortcuts import render

# Создание представлений

from .models import Book, Author, BookInstance, Genre


def index(request):
    """Функция представления для домашней страницы сайта."""
    # Генерация количества некоторых основных объектов
    # Запрос всех книг и подсчет их количества
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги (статус = 'д')
    num_instances_available = BookInstance.objects.filter(status__exact='д').count()
    num_authors = Author.objects.count()  # 'all()' подразумевается по умолчанию.

    # Количество посещений этого представления, как подсчитывается в переменной сессии.
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits+1

    # Отображение HTML-шаблона index.html с данными в переменной контекста.
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )


from django.views import generic


class BookListView(generic.ListView):
    """Общий класс-представление для списка книг."""
    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):
    """Общий класс-представление для детальной информации о книге."""
    model = Book


class AuthorListView(generic.ListView):
    """Общий класс-представление для списка авторов."""
    model = Author
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    """Общий класс-представление для детальной информации об авторе."""
    model = Author


from django.contrib.auth.mixins import LoginRequiredMixin


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Общий класс-представление для списка книг, взятых на аренду текущим пользователем."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='р') # Книги на руках (статус = 'р')
            .order_by('due_back')
        )


# Добавлено в рамках задания!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Общий класс-представление для списка всех книг, взятых на аренду. Доступно только пользователям с разрешением can_mark_returned."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='р').order_by('due_back') # Книги на руках (статус = 'р')


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required

# from .forms import RenewBookForm
from catalog.forms import RenewBookForm
from django.utils import timezone

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """Функция представления для продления конкретного экземпляра книги библиотекарем."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Если это POST-запрос, то обрабатываем данные формы
    if request.method == 'POST':

        # Создаем экземпляр формы и заполняем его данными из запроса (привязка):
        form = RenewBookForm(request.POST)

        # # Проверяем, действительна ли форма:
        # if form.is_valid():
        #     # Обрабатываем данные в form.cleaned_data, как требуется (здесь мы просто записываем их в поле due_back модели)
        #     book_instance.due_back = form.cleaned_data['renewal_date']
        #     book_instance.save()
        #
        #     # Перенаправляем на новый URL:
        #     return HttpResponseRedirect(reverse('all-borrowed'))
        if form.is_valid():
            if not book_instance.due_back:  # Проверка, была ли книга продлена ранее
                proposed_renewal_date = timezone.now() + timezone.timedelta(weeks=1)
                book_instance.due_back = proposed_renewal_date
            else:
                book_instance.due_back = form.cleaned_data['renewal_date']
                book_instance.save()
    # Если это GET (или любой другой метод), создаем форму по умолчанию
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=1)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = '__all__' # Не рекомендуется (потенциальная проблема безопасности, если добавляются новые поля)
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'


# Классы, созданные для задания с формами
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'



from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# @login_required
# def renew_book_librarian(request, bookinst_id):
#     book_instance = get_object_or_404(BookInstance, id=bookinst_id)
#
#     # Проверка прав доступа (только пользователь, который арендует книгу, может продлить)
#     if request.user != book_instance.borrower:
#         return render(request, 'error_page.html', {'message': 'У вас нет прав на продление этой книги.'})
#
#     # Процесс продления аренды
#     if request.method == 'POST':
#         book_instance.due_back += timedelta(weeks=1)  # Продлеваем на неделю (или другой установленный срок)
#         book_instance.save()
#         return HttpResponseRedirect(reverse('my-borrowed'))
#
#     return render(request, 'renew_book_librarian.html', {'book_instance': book_instance})
