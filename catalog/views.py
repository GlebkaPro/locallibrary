from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from catalog.forms import RenewBookForm, BookInstanceEditForm
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .forms import UserRegistrationForm, BookCopyForm, BookInstanceForm, AddBookForm, EditBookForm, AuthorForm
from django.contrib.auth.decorators import login_required, permission_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BookCopy, BookInstance, Author
from django.contrib.auth.models import User
def index(request):
    """Функция представления для домашней страницы сайта."""
    # Генерация количества некоторых основных объектов
    # Запрос всех книг и подсчет их количества
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Доступные книги (статус = 'д')
    num_instances_available = BookInstance.objects.filter(status__exact='д').count()
    num_authors = Author.objects.count()  # 'all()'

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

class BookListView(generic.ListView):
    """Общий класс-представление для списка книг."""
    model = Book
    paginate_by = 10

class BookDetailView(generic.DetailView):
    """Общий класс-представление для детальной информации о книге."""
    model = Book

    # def book_detail(request, book_id):
    #   book = Book.objects.get(pk=book_id)
    #
    #   # Получаем количество копий с статусом 'д' для данной книги
    #   available_copies = BookCopy.objects.filter(book=book, status='д').count()
    #
    #   return render(request, 'catalog/book_detail.html', {'book': book, 'available_copies': available_copies})


class AuthorListView(generic.ListView):
    """Общий класс-представление для списка авторов."""
    model = Author
    paginate_by = 10
    def get_queryset(self):
        return Author.objects.all()  # Получите всех авторов

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
class AuthorDetailView(generic.DetailView):
    """Общий класс-представление для детальной информации об авторе."""
    model = Author

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

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Общий класс-представление для списка всех книг, взятых на аренду. Доступно только пользователям с разрешением can_mark_returned."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
      status = self.request.GET.get('status', None)

      if status is None:
        status = ['р', 'з'] # Установите стандартное значение, например, 'р'

      return BookInstance.objects.filter(status__in=status).order_by('due_back')

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """Функция представления для продления конкретного экземпляра книги библиотекарем."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # Если это POST-запрос, то обрабатываем данные формы
    if request.method == 'POST':

        # Создаем экземпляр формы и заполняем его данными из запроса (привязка):
        form = RenewBookForm(request.POST)

        if form.is_valid():
            if not book_instance.due_back:  # Проверка, была ли книга продлена ранее
                proposed_renewal_date = timezone.now() + timezone.timedelta(weeks=1)
                book_instance.due_back = proposed_renewal_date
            else:
                proposed_renewal_date = form.cleaned_data['renewal_date']
                book_instance.renewal_date = proposed_renewal_date  # Обновляем атрибут
                book_instance.save()
            return redirect('all-borrowed')
    # Если это GET (или любой другой метод), создаем форму по умолчанию
    else:
        proposed_renewal_date = book_instance.due_back + timezone.timedelta(weeks=1)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class AuthorCreate(PermissionRequiredMixin, CreateView):
  model = Author
  fields = ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'date_of_death']
  initial = {'date_of_death': '11/06/2020'}
  permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
  model = Author
  fields = '__all__'  # Не рекомендуется (потенциальная проблема безопасности, если добавляются новые поля)
  permission_required = 'catalog.can_mark_returned'
  template_name = 'catalog/author_edit.html'
  success_url = reverse_lazy('authors')  # URL для перенаправления после успешного редактирования автора

  def get_initial(self):
    initial = super(AuthorUpdate, self).get_initial()
    author = self.get_object()
    initial['first_name'] = author.first_name
    initial['last_name'] = author.last_name
    initial['middle_name'] = author.middle_name  # Установите начальное значение для "Отчество"
    initial['date_of_birth'] = author.date_of_birth
    initial['date_of_death'] = author.date_of_death
    return initial


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/author_confirm_delete.html'  # Создайте шаблон подтверждения удаления автора

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

# @login_required
# @permission_required('auth.add_user', raise_exception=True)
def create_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/create_user.html', {'form': form})

def user_list(request):
  if request.user.is_staff:
    users = User.objects.all()
    return render(request, 'catalog/user_list.html', {'users': users})
  else:
    return render(request, 'access_denied.html')


def add_bookinstance(request):
  if request.method == 'POST':
    form = BookInstanceForm(request.POST)
    if form.is_valid():
      book = form.cleaned_data['book']
      # Проверьте наличие доступного экземпляра
      available_copy = book.bookcopy_set.filter(status='д').first()
      if available_copy:
        form.instance.loan = available_copy
        form.save()
        # Измените статус экземпляра на 'з'
        available_copy.status = 'з'
        available_copy.borrower = form.cleaned_data['borrower']
        available_copy.save()
        return redirect('book-detail', pk=book.id)
      else:
        # Если нет доступных экземпляров, возбудите исключение Http404
        raise Http404("Нет доступных экземпляров для аренды")
  else:
    form = BookInstanceForm()

  return render(request, 'catalog/add_bookinstance.html', {'form': form})


@login_required
def edit_bookinstance(request, bookinstance_id):
    book_instance = get_object_or_404(BookInstance, id=bookinstance_id)

    if book_instance.status == 'з':  # Проверьте статус экземпляра
        if request.method == 'POST':
            form = BookInstanceEditForm(request.POST, instance=book_instance)

            if form.is_valid():
                # Если статус был изменен, разрешите сохранение
                if form.cleaned_data['status'] != 'з':
                    form.save()
                # Получите соответствующий экземпляр в BookCopy
                book_copy = BookCopy.objects.filter(book=book_instance.book, status='з').first()

                # Установите статус book_copy как в book_instance
                if book_copy:
                    book_copy.status = book_instance.status
                    book_copy.save()
                form.save()
                return redirect('all-borrowed')

        else:
            form = BookInstanceEditForm(instance=book_instance)

        return render(request, 'catalog/edit_bookinstance.html', {'form': form, 'book_instance': book_instance})
    else:
        # Обработка случая, когда экземпляр не имеет статус 'з'
        return redirect('all-borrowed')  # Пример: вернуться на страницу с информацией о книге

def add_book(request):
  if request.method == 'POST':
    form = AddBookForm(request.POST, request.FILES)
    if form.is_valid():
      title = form.cleaned_data['title']
      author = form.cleaned_data['author']
      summary = form.cleaned_data['summary']
      isbn = form.cleaned_data['isbn']
      genre = form.cleaned_data['genre']
      language = form.cleaned_data['language']
      image = form.cleaned_data['image']

      # Создайте новую книгу
      book = Book(title=title, summary=summary, isbn=isbn, language=language, image=image)
      if author:
        book.author = author
      if genre:
        book.genre.set(genre)
      book.save()

      return redirect('books')  # Перенаправление на список книг или другую страницу
  else:
    form = AddBookForm()

  return render(request, 'catalog/add_book.html', {'form': form})


def edit_book(request, book_id):
  book = get_object_or_404(Book, pk=book_id)

  if request.method == "POST":
    form = EditBookForm(request.POST, request.FILES, instance=book)
    if form.is_valid():
      form.save()
      return redirect('book-detail', book_id)
  else:
    # Устанавливаем начальные значения для полей, включая ManyToMany поле genre
    initial_data = {
      'title': book.title,
      'isbn': book.isbn,
      'genre': book.genre.all(),
      # Добавьте другие поля, если необходимо
    }
    form = EditBookForm(instance=book, initial=initial_data)

  return render(request, 'catalog/edit-book.html', {'book': book, 'form': form})


def delete_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        # Удаляем книгу
        book.delete()
        return redirect('books')  # Перенаправление на список книг или другую страницу

    return render(request, 'catalog/delete_book_confirm.html', {'book': book})

def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            return redirect('author-detail', pk=author.id)
    else:
        form = AuthorForm()

    return render(request, 'catalog/add_authors.html', {'form': form})

def return_book(request, book_instance_id):
  book_instance = get_object_or_404(BookInstance, id=book_instance_id)

  if book_instance.status == 'р':
    # Если статус аренды равен 'р', устанавливаем его в 'п'
    book_instance.status = 'п'
    book_instance.save()

    # Находим соответствующий экземпляр в BookCopy и устанавливаем его статус как 'д'
    book_copy = BookCopy.objects.filter(book=book_instance.book, status='р').first()
    if book_copy:
      book_copy.status = 'д'
      book_copy.save()

  elif book_instance.status == 'з':
    # Если статус аренды равен 'з', устанавливаем его в 'д'
    book_instance.status = 'д'
    book_instance.save()

    # Находим соответствующий экземпляр в BookCopy и устанавливаем его статус также как 'д'
    book_copy = BookCopy.objects.filter(book=book_instance.book, status='з').first()
    if book_copy:
      book_copy.status = 'д'
      book_copy.save()
  else:
    # Обработка случая, когда статус не равен 'р' или 'з'
    raise Http404("Статус экземпляра не позволяет его вернуть")

  return redirect('all-borrowed')

@login_required
def reserve_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user

    # Проверка наличия доступных экземпляров для резервации
    available_copy = book.bookcopy_set.filter(status='д').first()

    if available_copy:
        # Создайте аренду экземпляра и заполните поле 'loan' доступным экземпляром
        new_copy = BookInstance(book=book, borrower=user, status='з', loan=available_copy)
        new_copy.save()

        # Измените статус экземпляра на 'з'
        available_copy.status = 'з'
        available_copy.borrower = user
        available_copy.save()

        return redirect('book-detail', pk=book_id)
    else:
        # Если нет доступных экземпляров, возбудите исключение Http404
        raise Http404("Нет доступных экземпляров для резервации")


def create_book_copy(request, book_id):
    book = Book.objects.get(id=book_id)

    if request.method == 'POST':
        form = BookCopyForm(request.POST)
        if form.is_valid():
            book_copy = form.save(commit=False)
            book_copy.book = book
            book_copy.status = 'д'  # Установите статус, например, 'д' для доступности
            book_copy.save()
            return redirect('book-detail', pk=book.id)
    else:
        form = BookCopyForm()

    return render(request, 'catalog/create_book_copy.html', {'book': book, 'form': form})



