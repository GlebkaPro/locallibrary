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
        # Дата проверки находится в диапазоне, который библиотекарь может изменить (+4 недели)
        if data > datetime.date.today() + datetime.timedelta(weeks=1):
            raise ValidationError(
                _('Недействительная дата - продление более чем на 1 неделю вперед'))

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
from .models import BookInstance
from django.core.exceptions import ValidationError

from django import forms
from .models import BookInstance

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = ['book', 'imprint', 'due_back', 'borrower', 'status']


