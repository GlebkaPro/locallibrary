from datetime import date
from uuid import UUID

from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.forms import formset_factory
from django.http import Http404
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from catalog.forms import RenewBookForm, BookInstanceEditForm, GenreForm, LanguageForm, PositionDebitingActForm, \
  ParticipantForm
from users.models import User
from .forms import AcceptActForm
from .forms import AccountingBookCopyForm, BookCopyForm
from .forms import BookExemplarForm
from .forms import PositionAcceptActFormSet
from .forms import UserRegistrationForm, BookInstanceForm, AddBookForm, EditBookForm, AuthorForm, \
  ProfileUserForm
from .models import AcceptAct, FizPersonSource
from .models import Book, BookInstance, Author, Genre, Language
from .models import BookCopy
from .models import BookExemplar
from django.views import View

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
  request.session['num_visits'] = num_visits + 1

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
  paginate_by = 12
  template_name = 'books/book_list.html'

  def get_queryset(self):
    query = self.request.GET.get('search', '')
    return Book.objects.filter(title__icontains=query)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['search_query'] = self.request.GET.get('search', '')
    return context


class BookDetailView(generic.DetailView):
  """Общий класс-представление для детальной информации о книге."""
  model = Book
  template_name = 'books/book_detail.html'
  # def book_detail(request, book_id):
  #   book = Book.objects.get(pk=book_id)
  #
  #   # Получаем количество копий с статусом 'д' для данной книги
  #   available_copies = BookCopy.objects.filter(book=book, status='д').count()
  #
  #   return render(request, 'books/book_detail.html', {'book': book, 'available_copies': available_copies})


class AuthorListView(generic.ListView):
  """Общий класс-представление для списка авторов."""
  model = Author
  paginate_by = 10
  template_name = 'authors/author_list.html'

  def get_queryset(self):
    query = self.request.GET.get('search', '')
    return Author.objects.filter(
      Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(middle_name__icontains=query)
    )

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['search_query'] = self.request.GET.get('search', '')
    return context


class AuthorDetailView(generic.DetailView):
  """Общий класс-представление для детальной информации об авторе."""
  model = Author
  template_name = 'authors/author_detail.html'


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
  """Общий класс-представление для списка книг, взятых на аренду текущим пользователем."""
  model = BookInstance
  template_name = 'bookinstances/bookinstance_list_borrowed_user.html'
  paginate_by = 10

  def get_queryset(self):
    query = self.request.GET.get('search', '')
    return User.objects.filter(
      Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(middle_name__icontains=query)
    )

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['search_query'] = self.request.GET.get('search', '')
    return context
  # def get_queryset(self):
  #   status = self.request.GET.get('status', None)
  #
  #   if status is None:
  #     status = ['р', 'з']  # Установите стандартное значение 'р, з'
  #
  #   return BookInstance.objects.filter(borrower=self.request.user, status__in=status).order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
  """Общий класс-представление для списка всех книг, взятых на аренду. Доступно только пользователям с разрешением can_mark_returned."""
  model = BookInstance
  permission_required = 'catalog.can_mark_returned'
  template_name = 'bookinstances/bookinstance_list_borrowed_all.html'
  paginate_by = 10

  def get_queryset(self):
    status = self.request.GET.get('status', None)

    if status is None:
      status = ['р', 'з', 'п']

    return BookInstance.objects.filter(status__in=status).order_by('due_back')


# @login_required
# @permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
  """Функция представления для продления конкретного экземпляра книги библиотекарем."""
  book_instance = get_object_or_404(BookInstance, pk=pk)

  # Если это POST-запрос, то обрабатываем данные формы
  if request.method == 'POST':

    # Создаем экземпляр формы и заполняем его данными из запроса (привязка):
    form = RenewBookForm(request.POST, instance=book_instance)

    if form.is_valid():
      if not book_instance.due_back:  # Проверка, была ли книга продлена ранее
        proposed_renewal_date = timezone.now() + timezone.timedelta(weeks=1)
        book_instance.due_back = proposed_renewal_date
      else:
        proposed_renewal_date = form.cleaned_data['renewal_date']
        book_instance.renewal_date = proposed_renewal_date  # Обновляем атрибут
        book_instance.status = 'д'
        book_instance.save()
        messages.success(request, 'Выдача успешно продлена.')
        return redirect('my-borrowed')
    else:
      messages.error(request, 'Введённая дата не входит в рамки 1 недели.')
  # Если это GET (или любой другой метод), создаем форму по умолчанию
  else:
    proposed_renewal_date = book_instance.due_back + timezone.timedelta(weeks=1)
    form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

  context = {
    'form': form,
    'book_instance': book_instance,
  }

  return render(request, 'bookinstances/book_renew_librarian.html', context)


class AuthorCreate(PermissionRequiredMixin, CreateView):
  model = Author
  fields = ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'date_of_death']
  initial = {'date_of_death': '11/06/2020'}
  permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
  model = Author
  fields = '__all__'  # Не рекомендуется (потенциальная проблема безопасности, если добавляются новые поля)
  permission_required = 'catalog.can_mark_returned'
  template_name = 'authors/author_edit.html'
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
  template_name = 'authors/author_confirm_delete.html'  # Создайте шаблон подтверждения удаления автора


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
    users = get_user_model().objects.all()
    return render(request, 'users/user_list.html', {'users': users})
  else:
    return render(request, 'access_denied.html')


def add_bookinstance(request):
  if request.method == 'POST':
    form = BookInstanceForm(request.POST)
    if form.is_valid():
      book = form.cleaned_data['book']
      # Проверьте наличие доступного экземпляра
      worker = request.user
      available_copy = book.bookcopy_set.filter(status='д').first()
      if available_copy:
        form.instance.loan = available_copy
        form.instance.worker = worker
        form.save()
        # Измените статус экземпляра на 'з'
        available_copy.status = 'р'
        available_copy.borrower = form.cleaned_data['borrower']
        available_copy.save()
        return redirect('all-borrowed')
      else:
        # Если нет доступных экземпляров, возбудите исключение Http404
        raise Http404("Нет доступных экземпляров для аренды")
  else:
    form = BookInstanceForm()

  return render(request, 'bookinstances/add_bookinstance.html', {'form': form})


@login_required
def edit_bookinstance(request, bookinstance_id):
  book_instance = get_object_or_404(BookInstance, id=bookinstance_id)

  if book_instance.status == 'з':  # Проверьте статус экземпляра
    if request.method == 'POST':
      form = BookInstanceEditForm(request.POST, instance=book_instance)

      if form.is_valid():
        # Устанавливаем статус 'р' (Выдано)
        form.instance.status = 'р'
        form.save()

        # Получите соответствующий экземпляр в BookCopy
        book_copy = BookCopy.objects.filter(book=book_instance.book, status='з').first()

        # Установите статус book_copy как в book_instance
        if book_copy:
          book_copy.status = book_instance.status
          book_copy.save()

        return redirect('all-borrowed')

    else:
      form = BookInstanceEditForm(instance=book_instance)

    return render(request, 'bookinstances/edit_bookinstance.html', {'form': form, 'book_instance': book_instance})
  else:
    # Обработка случая, когда экземпляр не имеет статус 'з'
    return redirect('all-borrowed')


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

      # Сначала сохраните книгу без связей с жанрами
      book.save()

      # Теперь добавьте связи с жанрами
      if genre:
        book.genre.set(genre)

      return redirect('books')  # Перенаправление на список книг или другую страницу
  else:
    form = AddBookForm()

  return render(request, 'books/add_book.html', {'form': form})


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

  return render(request, 'books/edit-book.html', {'book': book, 'form': form})


def delete_book(request, book_id):
  book = get_object_or_404(Book, pk=book_id)

  if request.method == 'POST':
    # Удаляем книгу
    book.delete()
    return redirect('books')  # Перенаправление на список книг или другую страницу

  return render(request, 'books/delete_book_confirm.html', {'book': book})


def add_author(request):
  if request.method == 'POST':
    form = AuthorForm(request.POST)
    if form.is_valid():
      date_of_death = form.cleaned_data['date_of_death']
      if not date_of_death:
        # Если дата смерти не введена, устанавливаем ее в None
        form.cleaned_data['date_of_death'] = None
      author = form.save()
      return redirect('author-detail', pk=author.id)
  else:
    form = AuthorForm()

  return render(request, 'authors/add_authors.html', {'form': form})


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


from django.core.exceptions import PermissionDenied

@login_required
def reserve_book(request, book_id):
    user = request.user
    # Получите все резервы текущего пользователя
    user_reservations_count = BookInstance.objects.filter(borrower=user, status='з').count()

    # Проверьте количество резервов
    if user_reservations_count < 3:
        book = get_object_or_404(Book, pk=book_id)
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

            messages.success(request, "Экземпляр успешно зарезервирован.")
        else:
            # Если нет доступных экземпляров, установите сообщение об ошибке
            messages.error(request, "Нет доступных экземпляров для резервации")
    else:
        # Если количество резервов больше или равно трём, выдайте ошибку разрешения
        messages.error(request, "Вы уже зарезервировали максимальное количество книг (3шт.).")

    return redirect('book-detail', pk=book_id)



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

  return render(request, 'books/create_book_copy.html', {'book': book, 'form': form})


from django.shortcuts import render
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from .forms import ProfileUserForm


class ProfileUser(UpdateView):
  model = get_user_model()
  form_class = ProfileUserForm
  template_name = 'users/profile.html'
  extra_context = {'title': "Профиль пользователя"}

  def get_success_url(self):
    return reverse_lazy('profile')

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    user = self.request.user
    # Получаем все мероприятия, в которых зарегистрирован текущий пользователь
    registered_events = PositionEvent.objects.filter(borrower=user)
    context['registered_events'] = registered_events

    # Получаем все арендованные книги текущего пользователя
    bookinstance_list = BookInstance.objects.filter(borrower=user)
    context['bookinstance_list'] = bookinstance_list

    user_requests = Request.objects.filter(borrower=user)
    context['user_requests'] = user_requests

    return context

  def form_valid(self, form):
    user = form.save(commit=False)
    avatar = form.cleaned_data.get('avatar')
    if avatar:
      user.avatar = avatar
    user.save()
    return super().form_valid(form)

  def get_object(self, queryset=None):
    return self.request.user


def add_genre(request):
  if request.method == 'POST':
    form = GenreForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('add-genre')
  else:
    form = GenreForm()

  genres = Genre.objects.all()

  return render(request, 'catalog/add_genre.html', {'form': form, 'genres': genres})


def add_language(request):
  if request.method == 'POST':
    form = LanguageForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('add-language')
  else:
    form = LanguageForm()

  languages = Language.objects.all()

  return render(request, 'catalog/add_language.html', {'form': form, 'languages': languages})


def privacy_policy(request):
  return render(request, 'catalog/privacy_policy.html')


from django.views import View


class AcceptActListView(View):
  def get(self, request):
    accept_acts = AcceptAct.objects.all()
    return render(request, 'accept_acts/accept_act_list.html', {'accept_acts': accept_acts})


class CreateAcceptActView(View):
  def get(self, request):
    form = AcceptActForm()
    position_formset = PositionAcceptActFormSet(queryset=PositionAcceptAct.objects.none())
    return render(request, 'accept_acts/create_accept_act.html', {'form': form, 'position_formset': position_formset})

  def post(self, request):
    form = AcceptActForm(request.POST)
    position_formset = PositionAcceptActFormSet(request.POST)

    if form.is_valid() and position_formset.is_valid():
      accept_act = form.save()

      for position_form in position_formset:
        if position_form.cleaned_data:  # Проверяем, есть ли данные в форме
          position = position_form.save(commit=False)
          position.accept_act = accept_act
          position.save()

      return redirect('accept_act_list')

    return render(request, 'accept_acts/create_accept_act.html', {'form': form, 'position_formset': position_formset})


class AddPositionAcceptActView(View):
  def get(self, request, pk):
    accept_act = AcceptAct.objects.get(pk=pk)
    form = PositionAcceptActForm()
    return render(request, 'accept_acts/add_position_accept_act.html', {'accept_act': accept_act, 'form': form})

  def post(self, request, pk):
    accept_act = AcceptAct.objects.get(pk=pk)
    form = PositionAcceptActForm(request.POST)
    if form.is_valid():
      position_accept_act = form.save(commit=False)
      position_accept_act.accept_act = accept_act
      position_accept_act.save()
      return redirect('edit_accept_act', pk=pk)
    return render(request, 'accept_acts/add_position_accept_act.html', {'accept_act': accept_act, 'form': form})


# views.py
from .models import PositionAcceptAct
from .forms import PositionAcceptActForm


class EditPositionAcceptActView(View):
  def get(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    form = PositionAcceptActForm(instance=position_accept_act)
    return render(
      request,
      'accept_acts/edit_position_accept_act.html',
      {'position_accept_act': position_accept_act, 'form': form}
    )

  def post(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    form = PositionAcceptActForm(request.POST, instance=position_accept_act)
    if form.is_valid():
      form.save()
      return redirect('edit_accept_act', pk=position_accept_act.accept_act.pk)
    return render(request, 'accept_acts/edit_position_accept_act.html',
                  {'position_accept_act': position_accept_act, 'form': form})


class EditAcceptActView(View):
  def get(self, request, pk):
    accept_act = get_object_or_404(AcceptAct, pk=pk)
    form = AcceptActForm(instance=accept_act)
    position_accept_acts = PositionAcceptAct.objects.filter(accept_act=accept_act)
    return render(
      request,
      'accept_acts/edit_accept_act.html',
      {'accept_act': accept_act, 'position_accept_acts': position_accept_acts, 'form': form}
    )

  def post(self, request, pk):
    accept_act = AcceptAct.objects.get(pk=pk)
    form = AcceptActForm(request.POST, instance=accept_act)
    if form.is_valid():
      form.save()
      return redirect('accept_act_list')
    position_accept_acts = PositionAcceptAct.objects.filter(accept_act=accept_act)
    return render(request, 'accept_acts/edit_accept_act.html',
                  {'accept_act': accept_act, 'position_accept_acts': position_accept_acts, 'form': form})


def create_book_exemplar(request):
  if request.method == 'POST':
    form = BookExemplarForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('list_book_exemplar')
  else:
    form = BookExemplarForm()

  return render(request, 'books/create_book_exemplar.html', {'form': form})


def list_book_exemplar(request):
  book_exemplars = BookExemplar.objects.all()
  return render(request, 'books/list_book_exemplar.html', {'book_exemplars': book_exemplars})


from django.shortcuts import render
from .models import Publisher
from .forms import PublisherForm


def list_publishers(request):
  publishers = Publisher.objects.all()
  return render(request, 'catalog/list_publishers.html', {'publishers': publishers})


def create_publisher(request):
  if request.method == 'POST':
    form = PublisherForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('list_publishers')
  else:
    form = PublisherForm()
  return render(request, 'catalog/create_publisher.html', {'form': form})


class DeletePositionAcceptActView(View):
  def post(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    accept_act_pk = position_accept_act.accept_act.pk
    position_accept_act.delete()
    return redirect('edit_accept_act', pk=accept_act_pk)


class CreateAccountingView(View):
  template_name = 'accouting/create_accounting.html'

  def get(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    size = request.GET.get('size', 0)
    size = int(size) if size.isdigit() and int(size) > 0 else 0

    accounting_form = AccountingBookCopyForm()

    # Create initial data for BookCopyForm
    initial_data = {
      'book': position_accept_act.exemplar.book,
      'positionAcceptAct': position_accept_act
    }

    # Calculate max_num based on size
    max_num = size if size > 0 else None

    # Create a BookCopyForm formset with initial data and max_num
    BookCopyFormSet = formset_factory(
      BookCopyForm, extra=size, max_num=max_num, can_order=False
    )
    book_copy_formset = BookCopyFormSet(
      initial=[initial_data for _ in range(size)],
      prefix='book_copy_forms'
    )

    context = {
      'position_accept_act': position_accept_act,
      'accounting_form': accounting_form,
      'book_copy_formset': book_copy_formset
    }

    return render(request, self.template_name, context)

  def post(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    accounting_form = AccountingBookCopyForm(request.POST)

    # Check if the accounting form is valid
    if accounting_form.is_valid():
      # Save the accounting form
      accounting_book_copy = accounting_form.save()

      # Create a BookCopyForm formset
      BookCopyFormSet = formset_factory(BookCopyForm, extra=0)

      # Check if the formset is valid
      formset = BookCopyFormSet(request.POST, prefix='book_copy_forms')
      if formset.is_valid():
        # Save data from each form in the formset
        for form in formset:
          book_copy = form.save(commit=False)
          book_copy.accountingBookCopy = accounting_book_copy
          book_copy.save()

        # Your existing code for redirection
        redirect_url = request.GET.get('next', reverse('edit_accept_act', kwargs={'pk': pk}))
        return redirect(redirect_url)

    # Handle form validation errors
    return render(request, self.template_name,
                  {'position_accept_act': position_accept_act, 'accounting_form': accounting_form,
                   'book_copy_formset': formset})

class CreateDebitingActView(View):
  template_name = 'debiting_acts/create_debiting_act.html'

  def get(self, request):
    debiting_form = DebitingActForm()
    position_formset = PositionDebitingActFormSet(prefix='position_formset')

    context = {
      'debiting_form': debiting_form,
      'position_formset': position_formset,
    }

    return render(request, self.template_name, context)

  def post(self, request):
    debiting_form = DebitingActForm(request.POST)
    position_formset = PositionDebitingActFormSet(request.POST, prefix='position_formset')

    if debiting_form.is_valid() and position_formset.is_valid():
      debiting_act = debiting_form.save()

      for form in position_formset:
        position = form.save(commit=False)
        position.debiting_act = debiting_act
        position.save()

        if position.debiting_exemplar:
          position.debiting_exemplar.status = 'с'  # 'с' означает "Списано"
          position.debiting_exemplar.save()

      return redirect('debiting_act_list')  # Change 'your_success_url' to your actual success URL

    context = {
      'debiting_form': debiting_form,
      'position_formset': position_formset,
    }

    return render(request, self.template_name, context)


# ваш_проект/views.py
from django.shortcuts import render
from django.views import View
from .models import DebitingAct


class DebitingActListView(View):
  template_name = 'debiting_acts/debiting_act_list.html'

  def get(self, request):
    debiting_acts = DebitingAct.objects.all()

    context = {
      'debiting_acts': debiting_acts,
    }

    return render(request, self.template_name, context)


# ваш_проект/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import DebitingAct, PositionDebitingAct
from .forms import DebitingActForm, PositionDebitingActFormSet


class EditDebitingActView(View):
  template_name = 'debiting_acts/edit_debiting_act.html'

  def get(self, request, pk):
    debiting_act = get_object_or_404(DebitingAct, pk=pk)
    position_debiting_acts = PositionDebitingAct.objects.filter(debiting_act=debiting_act)
    debiting_form = DebitingActForm(instance=debiting_act)

    context = {
      'debiting_act': debiting_act,
      'debiting_form': debiting_form,
      'position_debiting_acts': position_debiting_acts,
    }

    return render(request, self.template_name, context)

  def post(self, request, pk):
    debiting_act = get_object_or_404(DebitingAct, pk=pk)
    debiting_form = DebitingActForm(request.POST, instance=debiting_act)

    if debiting_form.is_valid():
      debiting_form.save()
      return redirect('debiting_act_list')

    # Если форма не валидна, вернуть ее с ошибками
    position_debiting_acts = PositionDebitingAct.objects.filter(debiting_act=debiting_act)
    context = {
      'debiting_act': debiting_act,
      'debiting_form': debiting_form,
      'position_debiting_acts': position_debiting_acts,
    }
    return render(request, self.template_name, context)


class EditPositionDebitingActView(View):
  template_name = 'debiting_acts/edit_position_debiting_act.html'

  def get(self, request, pk):
    position_debiting_act = get_object_or_404(PositionDebitingAct, pk=pk)
    form = PositionDebitingActForm(instance=position_debiting_act)

    context = {
      'position_debiting_act': position_debiting_act,
      'form': form,
    }

    return render(request, self.template_name, context)

  def post(self, request, pk):
    position_debiting_act = get_object_or_404(PositionDebitingAct, pk=pk)
    form = PositionDebitingActForm(request.POST, instance=position_debiting_act)

    if form.is_valid():
      form.save()
      return redirect('edit_debiting_act', pk=position_debiting_act.debiting_act.pk)

    # Если форма не валидна, вернуть ее с ошибками
    context = {
      'position_debiting_act': position_debiting_act,
      'form': form,
    }
    return render(request, self.template_name, context)


class AddPositionDebitingActView(View):
  template_name = 'debiting_acts/add_position_debiting_act.html'

  def get(self, request, pk):
    form = PositionDebitingActForm()
    tip_choices = PositionDebitingAct.ACCEPT_TIP  # Получите значения выбора из модели
    context = {
      'form': form,
      'tip_choices': tip_choices,  # Передайте значения выбора в контекст
    }
    return render(request, self.template_name, context)

  def post(self, request, pk):
    form = PositionDebitingActForm(request.POST)

    if form.is_valid():
      position_debiting_act = form.save(commit=False)
      position_debiting_act.debiting_act_id = pk
      position_debiting_act.save()
      return redirect('edit_debiting_act', pk=pk)

    # Если форма не валидна, вернуть ее с ошибками
    context = {'form': form}
    return render(request, self.template_name, context)


class DeletePositionDebitingActView(View):
  def post(self, request, pk):
    position_debiting_act = get_object_or_404(PositionDebitingAct, pk=pk)
    debiting_act_pk = position_debiting_act.debiting_act.pk
    position_debiting_act.delete()
    return redirect('edit_debiting_act', pk=debiting_act_pk)


# ваш_проект/views.py
from django.views.generic import ListView
from .models import BookInstance


class UserLoansListView(ListView):
  model = BookInstance
  # template_name = 'catalog/user_loans_list.html'
  template_name = 'catalog/templates/bookinstances/bookinstance_list_borrowed_all.html'

  paginate_by = 10

  def get_queryset(self):
    user_id = self.kwargs['pk']
    return BookInstance.objects.filter(borrower__id=user_id, status__in=['р', 'з', 'п']).order_by('due_back')


from django.shortcuts import render, redirect
from .forms import SourceForm, FizPersonSourceForm

from django.shortcuts import render, redirect
from .forms import SourceForm, FizPersonSourceForm


def create_source(request):
  if request.method == 'POST':
    form = SourceForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('source_list')  # Замените 'success_page' на URL успешной страницы
  else:
    form = SourceForm()

  return render(request, 'source/create_source.html', {'form': form})


def create_fiz_person_source(request):
  if request.method == 'POST':
    form = FizPersonSourceForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('fiz_person_source_list')  # Замените 'success_page' на URL успешной страницы
  else:
    form = FizPersonSourceForm()

  return render(request, 'source/create_fiz_person_source.html', {'form': form})


from django.shortcuts import render
from .models import Source


def source_list(request):
  organizations = Source.objects.all()
  return render(request, 'source/source_list.html', {'organizations': organizations})


from django.shortcuts import render
from .models import FizPersonSource


def fiz_person_source_list(request):
  fiz_persons = FizPersonSource.objects.all()
  return render(request, 'source/fiz_person_source_list.html', {'fiz_persons': fiz_persons})


from django.shortcuts import render
from django.views.generic import DetailView
from django.http import HttpResponse
from .models import AcceptAct
from django.views.generic import DetailView
from reportlab.pdfgen import canvas
from .models import AcceptAct
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# В начале файла views.py
pdfmetrics.registerFont(TTFont('LiberationSans', 'catalog/static/fonts/LiberationSans-Regular.ttf'))


class AcceptActDetailView(DetailView):
  model = AcceptAct
  template_name = 'accept_acts/accept_act_detail.html'


class PrintAcceptActView(DetailView):
  model = AcceptAct
  template_name = 'print_accept_act.html'

  def render_to_response(self, context, **response_kwargs):
    # Создаем объект HttpResponse с типом содержимого PDF.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="accept_act.pdf"'

    # Создаем объект PDF, связанный с объектом HttpResponse.
    p = canvas.Canvas(response)

    # Устанавливаем шрифт
    p.setFont('LiberationSans', 12)

    # Получаем данные акта из контекста.
    accept_act = context['object']

    # Добавляем данные акта в PDF.
    p.drawString(100, 800, f"Акт о приёме №{accept_act.number}")
    p.drawString(100, 780, f"Дата: {accept_act.current_date}")
    p.drawString(100, 760, f"Сумма: {accept_act.summa}")
    p.drawString(100, 740, f"Сотрудник: {accept_act.worker}")
    p.drawString(100, 720, f"Источник: {accept_act.source}")
    p.drawString(100, 700, f"Тип поступления: {accept_act.get_Tip_display()}")

    # Добавляем заголовок для позиций.
    p.drawString(100, 670, "Позиции в акте:")

    # Получаем позиции акта и добавляем их в PDF.
    positions = accept_act.position_accept_acts.all()
    y_position = 650
    for position in positions:
      p.drawString(120, y_position, f"Цена: {position.price}")
      p.drawString(120, y_position - 20, f"Количество: {position.size}")
      p.drawString(120, y_position - 40, f"Экземпляр: {position.exemplar}")
      y_position -= 60

    # Завершаем создание PDF.
    p.showPage()
    p.save()

    return response


from django.shortcuts import render, redirect
from .forms import EventForm


def create_event(request):
  if request.method == 'POST':
    form = EventForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('event_list')  # Перенаправляем пользователя на страницу со списком мероприятий после создания
  else:
    form = EventForm()
  return render(request, 'event/create_event.html', {'form': form})


from django.shortcuts import render, redirect
from .models import Event


def event_list(request):
  events = Event.objects.all()
  return render(request, 'event/event_list.html',  {'events': events})


from django.shortcuts import render
from .models import Room


def room_list(request):
  rooms = Room.objects.all()
  return render(request, 'event/room_list.html', {'rooms': rooms})


from django.shortcuts import render, redirect
from .forms import RoomForm


def create_room(request):
  if request.method == 'POST':
    form = RoomForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('room_list')  # Перенаправляем пользователя на страницу со списком комнат после создания
  else:
    form = RoomForm()
  return render(request, 'event/create_room.html', {'form': form})


from django.shortcuts import render, redirect
from .models import TypeRoom
from .forms import TypeRoomForm


def type_room_list(request):
  type_rooms = TypeRoom.objects.all()
  return render(request, 'event/type_room_list.html', {'type_rooms': type_rooms})


def create_type_room(request):
  if request.method == 'POST':
    form = TypeRoomForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect(
        'type_room_list')  # Перенаправляем пользователя на страницу со списком типов комнат после создания
  else:
    form = TypeRoomForm()
  return render(request, 'event/create_type_room.html', {'form': form})


from django.shortcuts import render, redirect, get_object_or_404
from .models import TypeRoom
from .forms import TypeRoomForm


def edit_type_room(request, type_room_id):
  type_room = get_object_or_404(TypeRoom, id=type_room_id)
  if request.method == 'POST':
    form = TypeRoomForm(request.POST, instance=type_room)
    if form.is_valid():
      form.save()
      return redirect('type_room_list')
  else:
    form = TypeRoomForm(instance=type_room)
  return render(request, 'event/edit_type_room.html', {'form': form, 'type_room': type_room})


from django.shortcuts import render, redirect, get_object_or_404
from .models import TypeRoom


def delete_type_room(request, type_room_id):
  type_room = get_object_or_404(TypeRoom, id=type_room_id)
  if request.method == 'POST':
    type_room.delete()
    return redirect('type_room_list')
  return render(request, 'event/delete_type_room.html', {'type_room': type_room})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Room
from .forms import RoomForm


def edit_room(request, room_id):
  room = get_object_or_404(Room, id=room_id)
  if request.method == 'POST':
    form = RoomForm(request.POST, instance=room)
    if form.is_valid():
      form.save()
      return redirect('room_list')
  else:
    form = RoomForm(instance=room)
  return render(request, 'event/edit_room.html', {'form': form, 'room': room})


from django.shortcuts import render, redirect, get_object_or_404
from .models import Room


def delete_room(request, room_id):
  room = get_object_or_404(Room, id=room_id)
  if request.method == 'POST':
    room.delete()
    return redirect('room_list')
  return render(request, 'event/delete_room.html', {'room': room})


from django.shortcuts import render, get_object_or_404
from .models import PositionEvent, Event


def participants_list(request, event_id):
  event = get_object_or_404(Event, id=event_id)
  participants = PositionEvent.objects.filter(event=event)
  context = {
    'event': event,
    'participants': participants,
  }
  return render(request, 'event/participants_list.html', context)


from django.utils import timezone  # Импортируем timezone


def add_participant(request, event_id):
  event = get_object_or_404(Event, id=event_id)
  if request.method == 'POST':
    form = ParticipantForm(request.POST)
    if form.is_valid():
      participant = form.save(commit=False)
      participant.event = event
      participant.date_record = timezone.now()  # Устанавливаем текущую дату
      participant.save()
      return redirect('participants_list', event_id=event.id)
  else:
    form = ParticipantForm()
  return render(request, 'event/add_participant.html', {'form': form, 'event': event})


def edit_participant(request, event_id, participant_id):
  participant = get_object_or_404(PositionEvent, id=participant_id)
  form = ParticipantForm(request.POST or None, instance=participant)
  if request.method == 'POST' and form.is_valid():
    form.save()
    return redirect('participants_list', event_id=event_id)
  return render(request, 'event/edit_participant.html', {'form': form, 'event_id': event_id})


def delete_participant(request, event_id, participant_id):
  participant = get_object_or_404(PositionEvent, id=participant_id)
  if request.method == 'POST':
    participant.delete()
    return redirect('participants_list', event_id=event_id)
  return render(request, 'event/delete_participant.html', {'participant': participant, 'event_id': event_id})


from .forms import EventForm


def edit_event(request, event_id):
  event = get_object_or_404(Event, id=event_id)

  if request.method == 'POST':
    form = EventForm(request.POST, instance=event)
    if form.is_valid():
      form.save()
      return redirect('event_list')
  else:
    form = EventForm(instance=event, initial={'date_start': event.date_start,
                                              'date_end': event.date_end})

  return render(request, 'event/edit_event.html', {'form': form, 'event': event})


def delete_event(request, event_id):
  event = get_object_or_404(Event, id=event_id)
  if request.method == 'POST':
    event.delete()
    return redirect('event_list')
  return render(request, 'event/delete_event.html', {'event': event})


@login_required
def register_to_event(request, event_id):
  event = get_object_or_404(Event, id=event_id)
  # Проверяем, зарегистрирован ли пользователь на данное мероприятие
  if PositionEvent.objects.filter(event=event, borrower=request.user).exists():
    messages.error(request, 'Вы уже зарегистрированы на выбранное мероприятие.')
    return redirect('event_list_borrower')  # Редиректим на страницу со списком мероприятий
  else:
    position_event = PositionEvent(event=event, borrower=request.user, date_record=date.today())
    position_event.save()
    return redirect('participants_list', event_id=event.id)


# @login_required
def event_list_borrower(request):
  events = Event.objects.all()
  # Получаем текущего пользователя из запроса
  current_user = request.user

  # Фильтруем мероприятия на основе участия пользователя
  events = Event.objects.filter(positionevent__borrower=current_user)

  return render(request, 'event/event_list_borrower.html', {'events': events})


from .models import PositionEvent


def cancel_registration(request, registration_id):
  registration = get_object_or_404(PositionEvent, id=registration_id)

  # Проверяем, что текущий пользователь зарегистрирован на это мероприятие
  if registration.borrower == request.user:
    # Изменяем статус записи на "не записан"
    registration.status_record = 'н'
    registration.save()

  # Перенаправляем пользователя на страницу профиля с указанием активной вкладки "Мероприятия"
  redirect_url = reverse('profile') + '?tab=events'
  return redirect(redirect_url)


from .models import Event


def detail_event(request, event_id):
  # Получаем объект Event по event_id или возвращаем 404, если ивент не найден
  event = get_object_or_404(Event, id=event_id)
  context = {'event': event}
  return render(request, 'event/detail_event.html', context)


from django.contrib.auth.decorators import login_required


@login_required
def create_request(request):
  if request.method == 'POST':
    form = RequestForm(request.POST)
    if form.is_valid():
      # Присваиваем текущего пользователя полю "Абонент" перед сохранением формы
      request_obj = form.save(commit=False)
      request_obj.date_creation = timezone.now()  # Установка текущей даты и времени
      request_obj.borrower = request.user
      request_obj.save()
      return redirect('request_list')  # Перенаправляем пользователя на страницу со списком заявок после создания
  else:
    form = RequestForm()
  return render(request, 'request/create_request.html', {'form': form})


def request_list(request):
  requests = Request.objects.all()
  return render(request, 'request/request_list.html', {'requests': requests})


def delete_request(request, request_id):
  request_obj = get_object_or_404(Request, id=request_id)
  if request.method == 'POST':
    request_obj.delete()
    return redirect('request_list')
  return redirect('request_list')  # В случае GET запроса перенаправляем обратно на страницу списка заявок


from django.shortcuts import render
from .forms import RequestForm
from .models import Request
from django.utils import timezone


def edit_request(request, request_id):
    request_obj = get_object_or_404(Request, id=request_id)

    # Проверяем, что статус записи равен 'в'
    if request_obj.status_record != 'в':
        # Если статус не 'в', перенаправляем пользователя на страницу профиля
        redirect_url = reverse('profile') + '?tab=my_requests'
        return redirect(redirect_url)

    if request.method == 'POST':
        form = RequestForm(request.POST, instance=request_obj)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.date_creation = timezone.now()  # Обновляем дату редактирования
            request_obj.worker = request.user
            request_obj.save()
            # Формируем URL для редиректа
            redirect_url = reverse('profile') + '?tab=my_requests'
            # Редирект на страницу профиля с активной вкладкой "Мои заявки"
            return redirect(redirect_url)
    else:
        form = RequestForm(instance=request_obj)

    return render(request, 'request/edit_request.html', {'form': form, 'request_obj': request_obj})


def profile_delete_request(request, request_id):
  request_obj = get_object_or_404(Request, id=request_id)

  # Проверяем, что статус записи равен 'в'
  if request_obj.status_record != 'в':
    # Если статус не 'в', перенаправляем пользователя на страницу профиля
    redirect_url = reverse('profile') + '?tab=my_requests'
    return redirect(redirect_url)

  if request.method == 'POST':
    # Удаляем заявку
    request_obj.delete()

  # Перенаправляем пользователя на страницу профиля с указанием активной вкладки "Мероприятия"
  redirect_url = reverse('profile') + '?tab=my_requests'
  return redirect(redirect_url)


from django.shortcuts import get_object_or_404, redirect
from .models import PositionEvent
from django.contrib.auth.decorators import login_required
from django.urls import reverse


@login_required
def profile_register_to_event(request, registration_id):
  registration = get_object_or_404(PositionEvent, id=registration_id)

  # Проверяем, что текущий пользователь зарегистрирован на это мероприятие
  if registration.borrower == request.user:
    # Изменяем статус записи на "записан"
    registration.status_record = 'з'
    registration.save()

  # Перенаправляем пользователя на страницу профиля с указанием активной вкладки "Мероприятия"
  redirect_url = reverse('profile') + '?tab=events'
  return redirect(redirect_url)

def cancel_reservation(request, bookinst_id):

    bookinst = get_object_or_404(BookInstance, pk=bookinst_id)

    if request.method == 'POST':
        # Удаляем запись о резерве
        bookinst.delete()
        messages.success(request, "Резерв успешно отменен.")
    else:
        messages.error(request, "Ошибка при отмене резерва.")

    # Перенаправляем пользователя на страницу профиля
    redirect_url = reverse('profile') + '?tab=books'
    return redirect(redirect_url)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Request
from .forms import RequestForm

@login_required
def accept_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    req.status_record = 'п'
    req.worker = request.user
    req.save()
    return redirect('request_list')

@login_required
def reject_request(request, request_id):
    req = get_object_or_404(Request, id=request_id)
    if request.method == 'POST':
        req.reason = request.POST.get('reason')
        req.status_record = 'о'
        req.worker = request.user
        req.save()
        return redirect('request_list')
    return render(request, 'request/reject_request.html')


from django.shortcuts import render
from django.http import JsonResponse
from .models import Request

from django.template.loader import render_to_string


def filtered_requests(request):
  start_date = request.GET.get('start_date')
  end_date = request.GET.get('end_date')

  # Применяем фильтр к запросам на основе даты создания
  filtered_requests = Request.objects.filter(date_creation__range=[start_date, end_date])

  context = {
    'requests': filtered_requests,
  }

  # Рендерим только строки таблицы без обертки
  rows_html = render_to_string('request/filtered_requests.html', context)

  return JsonResponse({'rows_html': rows_html})


