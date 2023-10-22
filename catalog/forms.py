from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime  # для проверки диапазона дат продления.

from django import forms


class RenewBookForm(forms.Form):
    """Форма для библиотекаря для обновления книг."""
    renewal_date = forms.DateField(
            help_text="Введите дату продления(максимум на 1 неделю).")

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

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

from django import forms
from .models import BookInstance, Genre, Language, Author
from django.core.exceptions import ValidationError

from django import forms
from .models import BookInstance

from django import forms
from django.core.exceptions import ValidationError
from .models import BookInstance

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'imprint', 'due_back', 'borrower', 'status']

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        due_back = cleaned_data.get('due_back')

        if book:
            # Проверьте, остались ли доступные экземпляры книги
            if book.instances <= 0:
                raise ValidationError('Нет доступных экземпляров книги для аренды.')

            # Другие проверки здесь (например, проверка даты)

        return cleaned_data


# Ваш файл forms.py

from django import forms

# Ваш файл forms.py

from django import forms

from django import forms
from .models import Book

class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image', 'instances']


from django import forms
from .models import Book


class BookForm(forms.ModelForm):
  class Meta:
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language', 'image', 'instances']

class AuthorForm(forms.ModelForm):
  class Meta:
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
