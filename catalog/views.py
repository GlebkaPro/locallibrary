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
from catalog.forms import RenewBookForm, BookInstanceEditForm, GenreForm, LanguageForm, PositionDebitingActForm
from .forms import AcceptActForm
from .forms import AccountingBookCopyForm, BookCopyForm
from .forms import BookExemplarForm
from .forms import PositionAcceptActFormSet
from .forms import UserRegistrationForm, BookInstanceForm, AddBookForm, EditBookForm, AuthorForm, \
  ProfileUserForm
from .models import AcceptAct
from .models import Book, BookInstance, Author, Genre, Language
from .models import BookCopy
from .models import BookExemplar


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
  template_name = 'catalog/book_list.html'

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
  template_name = 'catalog/bookinstance_list_borrowed_user.html'
  paginate_by = 10

  def get_queryset(self):
    status = self.request.GET.get('status', None)

    if status is None:
      status = ['р', 'з']  # Установите стандартное значение 'р, з'

    return BookInstance.objects.filter(borrower=self.request.user, status__in=status).order_by('due_back')


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
  """Общий класс-представление для списка всех книг, взятых на аренду. Доступно только пользователям с разрешением can_mark_returned."""
  model = BookInstance
  permission_required = 'catalog.can_mark_returned'
  template_name = 'catalog/bookinstance_list_borrowed_all.html'
  paginate_by = 10

  def get_queryset(self):
    status = self.request.GET.get('status', None)

    if status is None:
      status = ['р', 'з']  # Установите стандартное значение, например, 'р'

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
    return render(request, 'catalog/user_list.html', {'users': users})
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

      # Сначала сохраните книгу без связей с жанрами
      book.save()

      # Теперь добавьте связи с жанрами
      if genre:
        book.genre.set(genre)

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
      date_of_death = form.cleaned_data['date_of_death']
      if not date_of_death:
        # Если дата смерти не введена, устанавливаем ее в None
        form.cleaned_data['date_of_death'] = None
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

    messages.success(request, "Экземпляр успешно зарезервирован.")
  else:
    # Если нет доступных экземпляров, установите сообщение об ошибке
    messages.error(request, "Нет доступных экземпляров для резервации")

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

  return render(request, 'catalog/create_book_copy.html', {'book': book, 'form': form})


class ProfileUser(LoginRequiredMixin, UpdateView):
  model = get_user_model()
  form_class = ProfileUserForm
  template_name = 'catalog/profile.html'
  extra_context = {'title': "Профиль пользователя"}

  def get_success_url(self):
    return reverse_lazy('profile')

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
    return render(request, 'catalog/accept_act_list.html', {'accept_acts': accept_acts})


class CreateAcceptActView(View):
  def get(self, request):
    form = AcceptActForm()
    position_formset = PositionAcceptActFormSet(queryset=PositionAcceptAct.objects.none())
    return render(request, 'catalog/create_accept_act.html', {'form': form, 'position_formset': position_formset})

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

    return render(request, 'catalog/create_accept_act.html', {'form': form, 'position_formset': position_formset})


class AddPositionAcceptActView(View):
  def get(self, request, pk):
    accept_act = AcceptAct.objects.get(pk=pk)
    form = PositionAcceptActForm()
    return render(request, 'catalog/add_position_accept_act.html', {'accept_act': accept_act, 'form': form})

  def post(self, request, pk):
    accept_act = AcceptAct.objects.get(pk=pk)
    form = PositionAcceptActForm(request.POST)
    if form.is_valid():
      position_accept_act = form.save(commit=False)
      position_accept_act.accept_act = accept_act
      position_accept_act.save()
      return redirect('edit_accept_act', pk=pk)
    return render(request, 'catalog/add_position_accept_act.html', {'accept_act': accept_act, 'form': form})


# views.py
from .models import PositionAcceptAct
from .forms import PositionAcceptActForm


class EditPositionAcceptActView(View):
  def get(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    form = PositionAcceptActForm(instance=position_accept_act)
    return render(
      request,
      'catalog/edit_position_accept_act.html',
      {'position_accept_act': position_accept_act, 'form': form}
    )

  def post(self, request, pk):
    position_accept_act = get_object_or_404(PositionAcceptAct, pk=pk)
    form = PositionAcceptActForm(request.POST, instance=position_accept_act)
    if form.is_valid():
      form.save()
      return redirect('edit_accept_act', pk=position_accept_act.accept_act.pk)
    return render(request, 'catalog/edit_position_accept_act.html',
                  {'position_accept_act': position_accept_act, 'form': form})


class EditAcceptActView(View):
  def get(self, request, pk):
    accept_act = get_object_or_404(AcceptAct, pk=pk)
    form = AcceptActForm(instance=accept_act)
    position_accept_acts = PositionAcceptAct.objects.filter(accept_act=accept_act)
    return render(
      request,
      'catalog/edit_accept_act.html',
      {'accept_act': accept_act, 'position_accept_acts': position_accept_acts, 'form': form}
    )

  def post(self, request, pk):
    accept_act = AcceptAct.objects.get(pk=pk)
    form = AcceptActForm(request.POST, instance=accept_act)
    if form.is_valid():
      form.save()
      return redirect('accept_act_list')
    position_accept_acts = PositionAcceptAct.objects.filter(accept_act=accept_act)
    return render(request, 'catalog/edit_accept_act.html',
                  {'accept_act': accept_act, 'position_accept_acts': position_accept_acts, 'form': form})


def create_book_exemplar(request):
  if request.method == 'POST':
    form = BookExemplarForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('list_book_exemplar')
  else:
    form = BookExemplarForm()

  return render(request, 'catalog/create_book_exemplar.html', {'form': form})


def list_book_exemplar(request):
  book_exemplars = BookExemplar.objects.all()
  return render(request, 'catalog/list_book_exemplar.html', {'book_exemplars': book_exemplars})


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


from django.shortcuts import render, redirect
from django.views import View
from .models import DebitingAct, PositionDebitingAct
from .forms import DebitingActForm, PositionDebitingActFormSet


class CreateDebitingActView(View):
  template_name = 'catalog/create_debiting_act.html'

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
  template_name = 'catalog/debiting_act_list.html'

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
  template_name = 'catalog/edit_debiting_act.html'

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
      return redirect('edit_debiting_act', pk=pk)

    # Если форма не валидна, вернуть ее с ошибками
    position_debiting_acts = PositionDebitingAct.objects.filter(debiting_act=debiting_act)
    context = {
      'debiting_act': debiting_act,
      'debiting_form': debiting_form,
      'position_debiting_acts': position_debiting_acts,
    }
    return render(request, self.template_name, context)


class EditPositionDebitingActView(View):
  template_name = 'catalog/edit_position_debiting_act.html'

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
  template_name = 'catalog/add_position_debiting_act.html'

  def get(self, request, pk):
    form = PositionDebitingActForm()
    context = {'form': form}
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
