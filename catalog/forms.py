from django.contrib.auth import get_user_model
from django.forms import DateInput
from django.utils.translation import gettext_lazy as _
import datetime
from .models import Book, Author, BookCopy, BookInstance, Genre, Language
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm

class RenewBookForm(forms.Form):
  """Форма для библиотекаря для продления абонимирования."""
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
  this_year = datetime.date.today().year
  date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 50, this_year - 5))))
  class Meta:
    model = get_user_model()
    fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'middle_name','date_birth')

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
  genres = forms.MultipleChoiceField(
    required=False,
    widget=forms.CheckboxSelectMultiple,
    choices=Genre.objects.all().values_list('id', 'name'),
  )
  new_genre = forms.CharField(max_length=200, required=False)

  # Валидация для нового жанра
  def clean_new_genre(self):
    new_genre = self.cleaned_data['new_genre']
    if new_genre and Genre.objects.filter(name=new_genre).exists():
      raise forms.ValidationError("Такой жанр уже существует.")
    return new_genre
  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image']

class EditBookForm(forms.ModelForm):
  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image']

class AuthorForm(forms.ModelForm):
    # this_year = datetime.date.today().year
    # date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 1000, this_year - 5))), required=False)
    # date_of_death = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 1000, this_year - 5))),
    #                                 required=False)
    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'middle_name', 'date_of_birth', 'date_of_death']



class BookCopyForm(forms.ModelForm):
  class Meta:
    model = BookCopy
    fields = ['imprint']

class ProfileUserForm(forms.ModelForm):
  username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
  email = forms.CharField(disabled=True, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))
  this_year = datetime.date.today().year
  date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))

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

