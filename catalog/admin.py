from django.contrib import admin

# Register your models here.

from .models import Author, Book, BookInstance, Language, BookCopy, AcceptAct, PositionAcceptAct, Source, \
  FizPersonSource, BookExemplar, Publisher, Genre, DebitingAct, PositionDebitingAct, Event, PositionEvent, Request, \
  History_of_appeals, AccountingBookCopy, News
from users.models import User
# Minimal registration of Models.
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BookInstance)
admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(BookCopy)
admin.site.register(User)
admin.site.register(AcceptAct)
admin.site.register(PositionAcceptAct)
admin.site.register(Source)
admin.site.register(FizPersonSource)
admin.site.register(Publisher)
admin.site.register(BookExemplar)
admin.site.register(DebitingAct)
admin.site.register(PositionDebitingAct)
admin.site.register(Event)
admin.site.register(PositionEvent)
admin.site.register(Request)
admin.site.register(History_of_appeals)
admin.site.register(AccountingBookCopy)
admin.site.register(News)
