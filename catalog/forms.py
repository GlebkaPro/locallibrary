from django.core.validators import RegexValidator
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _
import datetime  # для проверки диапазона дат продления.
from .models import Book, Author, BookCopy, BookInstance
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RenewBookForm(forms.Form):
  """Форма для библиотекаря для обновления книг."""
  renewal_date = forms.DateField(help_text="Введите дату продления(максимум на 1 неделю).")
  # fields = ['renewal_date']
  def clean_renewal_date(self):
    data = self.cleaned_data['renewal_date']
    # Дата проверки еще не прошла.
    if data < datetime.date.today():
      raise ValidationError(_('Недействительная дата - продление в прошедшую дату'))
    # Дата проверки находится в диапазоне, который библиотекарь может изменить (+1 неделя)
    if data > datetime.date.today() + datetime.timedelta(weeks=1):
      raise ValidationError(
        _('Недействительная дата - возможно не более чем на 1 неделю вперед'))
    # Возврат очищенных данных.
    return data

class UserRegistrationForm(UserCreationForm):
  email = forms.EmailField(required=True, label='Email')

  class Meta:
    model = User
    fields = ('username', 'email', 'password1', 'password2')

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'due_back', 'borrower', 'status']

    def __init__(self, *args, **kwargs):
      super(BookInstanceForm, self).__init__(*args, **kwargs)

      # Ограничьте queryset для поля 'loan' на те копии, которые принадлежат выбранной книге.
      if 'book' in self.data:
        book_id = self.data.get('book')
        if book_id:
          self.fields['loan'].queryset = BookInstance.objects.filter(book=book_id)
      elif self.instance.pk and self.instance.book:
        self.fields['loan'].queryset = self.instance.book.bookcopy_set.filter(status='д')

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
  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image']

class EditBookForm(forms.ModelForm):
  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image']


class AuthorForm(forms.ModelForm):
  class Meta:
    model = Author
    fields = ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'date_of_death']

  # # Поле ISBN с валидатором
  # isbn_validator = RegexValidator(
  #   regex=r'^\d{3}-\d-\d{4}-\d{4}-\d$',
  #   message='Введите ISBN в формате "978-5-9614-2009-0".',
  #   code='invalid_isbn'
  # )
  #
  # isbn = forms.CharField(
  #   label='ISBN',
  #   validators=[isbn_validator],
  #   widget=forms.TextInput(attrs={'pattern': r'^\d{3}-\d-\d{4}-\d{4}-\d$'})
  # )


class BookCopyForm(forms.ModelForm):
  class Meta:
    model = BookCopy
    fields = ['imprint']
