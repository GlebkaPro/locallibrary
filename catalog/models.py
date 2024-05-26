import uuid
from datetime import date
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from locallibrary import settings


class Genre(models.Model):
  name = models.CharField(verbose_name='Жанр',
                          max_length=200,
                          unique=True,
                          error_messages={
                            'unique': 'Жанр с таким именем уже существует.',
                          },
                          help_text="Введите жанр книги (например, научная фантастика, французская поэзия и т. д.)"
                          )

  def __str__(self):
    return self.name


class Language(models.Model):
  """Модель, представляющая язык (например, английский, французский, японский и т. д.)"""
  name = models.CharField(verbose_name='Язык',
                          max_length=200,
                          unique=True,
                          error_messages={'unique': 'Такой язык уже существует.',
                                          },
                          help_text="Введите естественный язык книги (например, английский, французский, японский и т. д.)")

  def __str__(self):
    """Строка для представления объекта модели (в административном сайте и т. д.)"""
    return self.name


class Book(models.Model):
  """Модель, представляющая книгу (но не конкретную копию книги)."""
  title = models.CharField(max_length=200)
  author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
  # Внешний ключ используется, потому что книга может иметь только одного автора, но авторы могут иметь несколько книг
  # Автор как строка, а не объект, потому что он еще не был объявлен в файле.
  summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги")
  isbn = models.CharField('ISBN', max_length=18,
                          unique=True,
                          help_text='13-значный <a href="https://www.isbn-international.org/content/what-isbn'
                                    '">номер ISBN</a>')
  # genre = models.ManyToManyField(Genre, help_text="Выберите жанр")
  genre = models.ManyToManyField(Genre, help_text="Выберите жанр", related_name="books")
  # ManyToManyField используется, потому что жанр может содержать много книг, а книга может охватывать много жанров.
  # Класс Genre уже был определен, поэтому мы можем указать объект выше.
  language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
  image = models.ImageField(upload_to='books/', blank=True, null=True)

  def available_copies_count(self):
    return self.bookcopy_set.filter(status='д').count()
  class Meta:
    ordering = ['title', 'author']

  def display_genre(self):
    """Создает строку для жанра. Это необходимо для отображения жанра в административной панели."""
    return ', '.join([genre.name for genre in self.genre.all()[:3]])

  display_genre.short_description = 'Жанр'

  def get_absolute_url(self):
    """Возвращает URL-адрес для доступа к конкретному экземпляру книги."""
    return reverse('book-detail', args=[str(self.id)])

  def __str__(self):
    """Строка для представления объекта модели."""
    return self.title


class AccountingBookCopy(models.Model):
  """Модель, представляющая учтённую копию книги (т. е. которой проставлен штамм)."""
  id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                        help_text="Уникальный идентификатор")
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Сотрудник')
  date_of_creation = models.DateField(default=timezone.now, verbose_name='Дата создания')

  def __str__(self):
    """Строка для представления объекта модели."""
    return '{0} ({1})'.format(self.id, self.worker, self.date_of_creation)


class BookCopy(models.Model):
  """Модель, представляющая учтённую копию книги (т. е. которой проставлен штамм)."""
  id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                        help_text="Уникальный идентификатор")
  book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True, verbose_name='Книга')
  imprint = models.CharField(max_length=200, null=True, verbose_name='Штамп')
  positionAcceptAct = models.ForeignKey('PositionAcceptAct', on_delete=models.RESTRICT, null=True,
                                        verbose_name='Позиция акта послупления')
  accountingBookCopy = models.ForeignKey('AccountingBookCopy', on_delete=models.RESTRICT, null=True,
                                         verbose_name='Позиция учёта экземпляра')
  LOAN_STATUS = (
    ('р', 'Выдано'),
    ('д', 'Доступно'),
    ('з', 'Зарезервировано'),
    ('с', 'Списано'),
  )

  status = models.CharField(
    max_length=1, choices=LOAN_STATUS, blank=True, default='д', help_text='Доступность книги', verbose_name='Статус')

  def __str__(self):
    """Строка для представления объекта модели."""
    title = self.book.title if self.book else 'Нет названия книги'
    return '{0} ({1})'.format(self.imprint, title, )


class BookInstance(models.Model):
  """Модель, представляющая аренду эксемпляров книг"""
  id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                        help_text="Уникальный идентификатор")
  book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True, verbose_name='Книга')
  due_back = models.DateField(null=True, blank=True, verbose_name='Дата окончания')
  borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Абонент')
  renewal_date = models.DateField(null=True, blank=True, verbose_name='Дата продления')
  current_date = models.DateField(default=timezone.now, verbose_name='Дата начала')
  return_date = models.DateField(null=True, blank=True, verbose_name='Дата возврата')
  loan = models.ForeignKey('BookCopy', on_delete=models.SET_NULL, null=True, blank=True)
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='worked_books', verbose_name='Сотрудник')

  @property
  def is_overdue(self):
    """Определяет, просрочена ли книга на основе даты возврата и текущей даты."""
    return bool(self.due_back and date.today() > self.due_back)

  LOAN_STATUS = (
    ('р', 'Выдано'),
    ('д', 'Продлено'),
    ('з', 'Зарезервировано'),
    ('п', 'Погашено'),
    ('о', 'Просрочено'),
  )

  status = models.CharField(
    max_length=1, choices=LOAN_STATUS, blank=True, default='р', help_text='Доступность книги', verbose_name='Статус')

  class Meta:
    ordering = ['due_back']
    permissions = (("can_mark_returned", "Отметить книгу как возвращенную"),)

  def __str__(self):
    """Строка для представления объекта модели."""
    return '{2} ({1}) {0}'.format(self.book.title, self.current_date, self.borrower)


class Author(models.Model):
  """Модель, представляющая автора."""
  first_name = models.CharField(verbose_name='Имя', max_length=100)
  last_name = models.CharField(verbose_name='Фамилия', max_length=100)
  middle_name = models.CharField(verbose_name='Отчество', null=True, max_length=100)
  date_of_birth = models.DateField('Дата рождения', null=True, blank=True)
  date_of_death = models.DateField('Дата смерти', null=True, blank=True)
  image = models.ImageField(upload_to='authors/', null=True, blank=True, verbose_name='Изображение')

  def __str__(self):
    """Строка для представления объекта модели."""
    return '{0} {1} {2}'.format(self.last_name, self.first_name, self.middle_name)
  class Meta:
    ordering = ['last_name', 'first_name', 'middle_name']

  def get_absolute_url(self):
    """Возвращает URL-адрес для доступа к конкретному экземпляру автора."""
    return reverse('author-detail', args=[int(self.id)])


class Source(models.Model):
  name = models.CharField(verbose_name='Наименование', max_length=100)
  address = models.CharField(verbose_name='Адрес', max_length=100)

  def __str__(self):
    return f"{self.name}"


class FizPersonSource(models.Model):
  first_name = models.CharField(verbose_name='Имя', max_length=100)
  last_name = models.CharField(verbose_name='Фамилия', max_length=100)
  middle_name = models.CharField(verbose_name='Отчество', null=True, max_length=100)
  contact_information = models.CharField(verbose_name='Контактные данные', null=True, max_length=100)
  source = models.ForeignKey('Source', on_delete=models.RESTRICT, null=True, verbose_name='Источник')

  def __str__(self):
    return f"{self.source}"


class AcceptAct(models.Model):
  number = models.CharField(verbose_name='Номер акта', max_length=100)
  current_date = models.DateField(default=timezone.now, verbose_name='Текущая дата')
  summa = models.CharField(verbose_name='Сумма', max_length=100)
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Сотрудник')
  source = models.ForeignKey('FizPersonSource', on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Источник')
  ACCEPT_TIP = (
    ('д', 'Дарение'),
    ('ж', 'Пожертвование'),
    ('п', 'Покупка'),
    ('о', 'Обмен'),
    ('н', 'Наследование'),
    ('з', 'Заимствование'),
  )

  Tip = models.CharField(
    max_length=1, choices=ACCEPT_TIP, blank=True, default='р', verbose_name='Тип поступления')

  ACCEPT_status = (
    ('у', 'учтено'),
    ('н', 'не учтено'),
  )

  status_record = models.CharField(
    max_length=1, choices=ACCEPT_status, blank=True, default='н', verbose_name='Статус записи')
  def __str__(self):
    return f"{self.current_date} - {self.worker}"


class PositionAcceptAct(models.Model):
  price = models.CharField(verbose_name='Цена', max_length=100)
  size = models.CharField(verbose_name='Количество', max_length=100)
  exemplar = models.ForeignKey('BookExemplar', on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Экземпляр')
  accept_act = models.ForeignKey('AcceptAct', on_delete=models.CASCADE, related_name='position_accept_acts',
                                 verbose_name='Акт о приёме')
  ACCEPT_status = (
    ('у', 'учтено'),
    ('н', 'не учтено'),
  )

  status_record = models.CharField(
    max_length=1, choices=ACCEPT_status, blank=True, default='н', verbose_name='Статус записи')
  def __str__(self):
    return f"{self.price} - {self.exemplar}"


class BookExemplar(models.Model):
  date_of_manufacture = models.DateField('Дата изготовления', null=True, blank=True)
  city_of_publication = models.CharField(verbose_name='Город издания', max_length=100)
  book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True, verbose_name='Книга')
  publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE, related_name='publisher',
                                verbose_name='Издательство')
  isbn = models.CharField('ISBN', max_length=20, blank=True, default='')
  udc = models.CharField('УДК', max_length=20, blank=True, default='')
  bbk = models.CharField('ББК', max_length=20, blank=True, default='')

  ACCEPT_publication_type = (
    ('к', 'Книга'),
    ('ж', 'Журнал'),
    ('г', 'Газета'),
    ('э', 'Электронный ресурс'),
    ('м', 'Мультимедийный материал'),
    ('р', 'Реферативное издание'),
    ('у', 'Учебники и учебные пособия'),
  )

  publication_type = models.CharField(
    max_length=1, choices=ACCEPT_publication_type, blank=True, default='к', verbose_name='Тип издания')

  def __str__(self):
    formatted_date = self.date_of_manufacture.strftime("%d.%m.%y") if self.date_of_manufacture else ""
    return f"{self.isbn} {self.udc} {self.bbk} | {self.book} | {formatted_date} "


class Publisher(models.Model):
  name = models.CharField(verbose_name='Наименование', max_length=100)

  def __str__(self):
    return f"{self.name}"


class DebitingAct(models.Model):
  number = models.CharField(verbose_name='Номер акта', max_length=100)
  current_date = models.DateField(default=timezone.now, verbose_name='Текущая дата')
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Сотрудник')

  def __str__(self):
    return f"{self.current_date} - {self.worker}"


class PositionDebitingAct(models.Model):
  price = models.CharField(verbose_name='Цена', max_length=100)
  debiting_exemplar = models.ForeignKey('BookCopy', on_delete=models.SET_NULL, null=True, blank=True,
                                        verbose_name='Учтённый экземпляр')
  debiting_act = models.ForeignKey('DebitingAct', on_delete=models.CASCADE, related_name='position_debiting_acts',
                                   verbose_name='Акт о приёме')
  ACCEPT_TIP = (
    ('а', 'Амортизация'),
    ('с', 'Устаревание'),
    ('п', 'Повреждение'),
    ('у', 'Утрата'),
  )

  Tip = models.CharField(
    max_length=1, choices=ACCEPT_TIP, blank=True, default='п', verbose_name='Тип списания')

  def __str__(self):
    return f"{self.price} - {self.debiting_exemplar}"


class Event(models.Model):
  fio = models.CharField(verbose_name='ФИО организатора', max_length=100)
  event_name = models.CharField(verbose_name='Наименование мероприятия', max_length=100)
  number_of_participants = models.CharField(verbose_name='Количество участников', max_length=100)
  date_start = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время начала проведения')
  date_end = models.DateTimeField(null=True, blank=True, verbose_name='Дата и время окончания проведения')
  date_end2 = models.DateField(null=True, blank=True, verbose_name='Дата фактического окончания')
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Сотрудник')
  room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
  typeroom = models.ForeignKey('TypeRoom', on_delete=models.SET_NULL, null=True)
  description = models.CharField(verbose_name='Описание', max_length=1000)
  image = models.ImageField(verbose_name='Изображение', upload_to='event_images/', blank=True, null=True)

class Review(models.Model):
  event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='reviews', verbose_name='Мероприятие')
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
  review_text = models.TextField(verbose_name='Отзыв')
  review_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')
  ACCEPT_status = (
    ('о', 'опубликован'),
    ('н', 'не опубликован'),
  )

  status_record = models.CharField(
    max_length=1, choices=ACCEPT_status, blank=True, default='н', verbose_name='Статус записи')

  def __str__(self):
    return f"Отзыв от {self.user} на {self.event.event_name}"

class PositionEvent(models.Model):
  event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True)
  date_record = models.DateField(null=True, blank=True, verbose_name='Дата регистрации')
  borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Абонент')
  ACCEPT_status = (
    ('з', 'записан'),
    ('н', 'не записан'),
  )

  status_record = models.CharField(
    max_length=1, choices=ACCEPT_status, blank=True, default='з', verbose_name='Статус записи')


class Room(models.Model):
  type = models.CharField(verbose_name='Тип', max_length=100)
  number = models.CharField(verbose_name='Номер', max_length=100)
  number_seats = models.CharField(verbose_name='Количество мест', max_length=100)

  def __str__(self):
    return f"№{self.number} мест: {self.number_seats}"


class TypeRoom(models.Model):
  name = models.CharField(verbose_name='Наименование', max_length=20)

  def __str__(self):
    return self.name


class Request(models.Model):
  title = models.CharField(max_length=200)
  author = models.CharField(max_length=200)
  description = models.CharField(verbose_name='Описание', max_length=100)
  date_creation = models.DateField(null=True, blank=True, verbose_name='Дата создания')
  borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               verbose_name='Абонент')
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='worked_request', verbose_name='Сотрудник')
  reason = models.TextField(blank=True, null=True, verbose_name='Причина')

  ACCEPT_status = (
    ('п', 'принята'),
    ('з', 'закрыта'),
    ('в', 'в обработке'),
    ('о', 'отклонено'),
  )

  status_record = models.CharField(
    max_length=1, choices=ACCEPT_status, blank=True, default='в', verbose_name='Статус заявки-')

  class Meta:
    ordering = ['title', 'author']
  def __str__(self):
    return self.title

class History_of_appeals(models.Model):
  title = models.CharField(max_length=200)
  note = models.CharField(max_length=200)
  date_creation = models.DateField(null=True, blank=True, verbose_name='Дата создания')
  bookinstance = models.ForeignKey('BookInstance', on_delete=models.CASCADE, null=True)
  worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='worked_history', verbose_name='Сотрудник')
  def __str__(self):
    return self.title

class News(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='news', verbose_name='Мероприятие')
    title = models.CharField(verbose_name='Название новости', max_length=100)
    description = models.TextField(verbose_name='Описание')
    images = models.ManyToManyField('NewsImage', verbose_name='Изображения', blank=True)
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='worked_news', verbose_name='Сотрудник')
    date_creation = models.DateField(null=True, blank=True, verbose_name='Дата создания')
    title_image = models.ImageField(verbose_name='Титульное изображение', upload_to='news_title_images/', blank=True,
                                    null=True)
class NewsImage(models.Model):
    image = models.ImageField(verbose_name='Изображение', upload_to='news_images/')

    def __str__(self):
        return self.image.name
