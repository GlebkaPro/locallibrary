import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _

from .models import Book, BookCopy, BookInstance, Genre, Language, BookExemplar, AccountingBookCopy, History_of_appeals


class RenewBookForm(forms.ModelForm):
  renewal_date = forms.DateField(help_text="Введите дату в диапазоне 1 недель (по умолчанию 1).")

  class Meta:
    model = BookInstance
    fields = ['renewal_date']

  def clean_renewal_date(self):
    data = self.cleaned_data['renewal_date']

    # Проверка, что дата в будущем
    if data < datetime.date.today():
      raise ValidationError(_('Неверная дата - дата выбрана из прошлого'))

    # Проверка, что дата не более чем на 4 недели вперед
    if data > datetime.date.today() + datetime.timedelta(weeks=1):
      raise ValidationError(_('Неверная дата - дата должна быть не более чем на 4 недели вперед'))

    # Помните всегда вернуть обработанные данные
    return data


class UserRegistrationForm(UserCreationForm):
  email = forms.EmailField(required=True, label='Email')
  this_year = datetime.date.today().year
  date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))
  privacy_policy_agreement = forms.BooleanField(
    required=True,
    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    label='Согласен с обработкой персональных данных'
  )
  phone_number = forms.CharField(label='Номер телефона', required=False)
  record_status = (
    ('а', 'активирована'),
    ('н', 'не активирована'),
  )

  class Meta:
    model = get_user_model()
    fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'middle_name', 'date_birth',
              'privacy_policy_agreement', 'phone_number')

from django import forms
from django.contrib.auth import get_user_model

class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['last_name', 'first_name', 'middle_name', 'date_birth', 'phone_number', 'email']

class BookInstanceForm(forms.ModelForm):
  class Meta:
    model = BookInstance
    fields = ['book', 'due_back', 'borrower', 'status', 'loan']

  def __init__(self, *args, **kwargs):
    super(BookInstanceForm, self).__init__(*args, **kwargs)

    # Ограничьте queryset для поля 'loan' на те копии, которые принадлежат выбранной книге.
    if 'book' in self.data:
      book_id = self.data.get('book')
      if book_id:
        self.fields['loan'].queryset = BookInstance.objects.filter(book=book_id)
    elif self.instance.pk and self.instance.book:
      self.fields['loan'].queryset = self.instance.book.bookcopy_set.filter(status='р')

  def clean(self):
    cleaned_data = super().clean()
    book = cleaned_data.get('book')
    status = cleaned_data.get('status')

    if book:
      # Проверьте, остались ли доступные экземпляры книги
      available_copies = book.bookcopy_set.filter(status='д')
      if not available_copies.exists() and status != 'з':
        raise forms.ValidationError('Нет доступных экземпляров книги для аренды.')

  # Добавьте виджет DateInput к полю 'due_back'
  widgets = {
    'due_back': DateInput(attrs={'type': 'date'}),
  }


class BookInstanceEditForm(forms.ModelForm):
  class Meta:
    model = BookInstance
    fields = ['book', 'due_back', 'borrower', 'status']

  def clean(self):
    cleaned_data = super().clean()
    book = cleaned_data.get('book')
    status = cleaned_data.get('status')

    if book:
      # Проверьте, остались ли доступные экземпляры книги
      available_copies = book.bookcopy_set.filter(status='з')
      # available_copies = book.bookcopy_set.filter(Q(status='д') | Q(status='з'))
      if not available_copies.exists() and status != 'з':
        raise forms.ValidationError('Нет доступных экземпляров книги для аренды (редактирование).')

  widgets = {
    'due_back': DateInput(attrs={'type': 'date'}),
  }


class AddBookForm(forms.ModelForm):
  # genres = forms.MultipleChoiceField(
  #   required=False,
  #   widget=forms.CheckboxSelectMultiple,
  #   choices=Genre.objects.all().values_list('id', 'name'),
  # )
  new_genre = forms.CharField(max_length=200, required=False)

  # Валидация для нового жанра
  # def clean_new_genre(self):
  #   new_genre = self.cleaned_data['new_genre']
  #   if new_genre and Genre.objects.filter(name=new_genre).exists():
  #     raise forms.ValidationError("Такой жанр уже существует.")
  #   return new_genre

  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image']


class EditBookForm(forms.ModelForm):
  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image']


from django import forms
from .models import Author

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'date_of_death', 'image']



class ProfileUserForm(forms.ModelForm):
  username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
  email = forms.CharField(label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))
  this_year = datetime.date.today().year
  date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))
  avatar = forms.ImageField(label='Аватар', required=False)

  class Meta:
    model = get_user_model()
    fields = ['avatar', 'username', 'email', 'date_birth', 'first_name', 'last_name', 'middle_name']
    labels = {
      'first_name': 'Имя',
      'last_name': 'Фамилия',
      'middle_name': 'Отчество',
    }
    widgets = {
      'first_name': forms.TextInput(attrs={'class': 'form-input'}),
      'last_name': forms.TextInput(attrs={'class': 'form-input'}),
      'middle_name': forms.TextInput(attrs={'class': 'form-input'}),
    }


class GenreForm(forms.ModelForm):
  class Meta:
    model = Genre
    fields = ['name']


class LanguageForm(forms.ModelForm):
  class Meta:
    model = Language
    fields = ['name']


# forms.py
from django import forms
from .models import AcceptAct, PositionAcceptAct

from django.forms import inlineformset_factory


class AcceptActForm(forms.ModelForm):
  class Meta:
    model = AcceptAct
    fields = ['number', 'summa', 'Tip', 'worker', 'source', 'current_date']


PositionAcceptActFormSet = inlineformset_factory(AcceptAct, PositionAcceptAct, fields=('price', 'size', 'exemplar'))

from django import forms


class PositionAcceptActForm(forms.ModelForm):
  class Meta:
    model = PositionAcceptAct
    fields = ['price', 'size', 'exemplar']

  # def __init__(self, *args, **kwargs):
  #   super(PositionAcceptActForm, self).__init__(*args, **kwargs)
  #   self.fields['exemplar'].queryset = BookExemplar.objects.all()
  #   self.fields['exemplar'].widget.attrs.update({'class': 'form-control'})


class BookExemplarForm(forms.ModelForm):
  class Meta:
    model = BookExemplar
    fields = '__all__'


from django import forms
from .models import Publisher


class PublisherForm(forms.ModelForm):
  class Meta:
    model = Publisher
    fields = '__all__'


class AccountingBookCopyForm(forms.ModelForm):
  class Meta:
    model = AccountingBookCopy
    fields = ['worker', 'date_of_creation']


class BookCopyForm(forms.ModelForm):
  class Meta:
    model = BookCopy
    fields = ['book', 'imprint', 'positionAcceptAct']


# ваш_проект/forms.py
from django import forms
from .models import DebitingAct, PositionDebitingAct


class DebitingActForm(forms.ModelForm):
  class Meta:
    model = DebitingAct
    fields = ['number', 'current_date', 'worker']


class PositionDebitingActForm(forms.ModelForm):
  class Meta:
    model = PositionDebitingAct
    fields = ['price', 'debiting_exemplar', 'Tip']


PositionDebitingActFormSet = inlineformset_factory(
  DebitingAct, PositionDebitingAct,
  form=PositionDebitingActForm, extra=1, can_delete=True
)

from django import forms
from .models import Source, FizPersonSource


class SourceForm(forms.ModelForm):
  class Meta:
    model = Source
    fields = ['name', 'address']


class FizPersonSourceForm(forms.ModelForm):
  class Meta:
    model = FizPersonSource
    fields = ['first_name', 'last_name', 'middle_name', 'source', 'contact_information']


from django import forms
from .models import Event


class EventForm(forms.ModelForm):
  class Meta:
    model = Event
    fields = '__all__'
    widgets = {
      'date_start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
      'date_end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    }

  image = forms.ImageField(label='Изображение', required=False)

from django import forms
from .models import Room


class RoomForm(forms.ModelForm):
  class Meta:
    model = Room
    fields = ['type', 'number', 'number_seats']


from django import forms
from .models import TypeRoom


class TypeRoomForm(forms.ModelForm):
  class Meta:
    model = TypeRoom
    fields = ['name']

from django import forms
from .models import PositionEvent

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = PositionEvent
        fields = ['borrower', 'status_record']  # Перечислите поля для добавления участника

# forms.py

from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'author', 'description']  # Поля, которые разрешено редактировать


class AppealForm(forms.ModelForm):
  class Meta:
    model = History_of_appeals
    fields = ['title', 'note', 'bookinstance', 'worker']

from django import forms
from .models import News


class NewsForm(forms.ModelForm):
  class Meta:
    model = News
    fields = ['title', 'description', 'title_image', 'images']

  def __init__(self, *args, **kwargs):
    super(NewsForm, self).__init__(*args, **kwargs)
    self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите название'})
    self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите описание'})
    self.fields['images'].widget.attrs.update({'class': 'form-control-file', 'multiple': True})
    self.fields['title_image'].widget.attrs.update({'class': 'form-control-file'})

  def save(self, commit=True):
    instance = super(NewsForm, self).save(commit=False)
    if commit:
      instance.save()
      self.save_m2m()  # Сохраняем множественные связи (изображения)
    return instance

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review_text']
