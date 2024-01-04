from django.contrib import admin

# Register your models here.

from .models import Author, Genre, Book, BookInstance, Language, BookCopy, AcceptAct, PositionAcceptAct, Source, \
  FizPersonSource, BookExemplar, Publisher
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

# admin.site.register(AuthorAdmin)
#
# class BooksInline(admin.TabularInline):
#     """Определяет формат вставки онлайн-книги (используется в Author Admin)"""
#     model = Book
#
#
# class AuthorAdmin(admin.ModelAdmin):
#     """Объект администрирования для авторских моделей.
#         Определяет:
#         - поля, которые будут отображаться в виде списка (list_display)
#         - поля заказов в подробном представлении (fields),
#           группирующие поля данных по горизонтали
#       - - добавляет встроенное добавление книг в режиме просмотра автора (встроенные строки)
#     """
#     list_display = ('last_name',
#                     'first_name', 'date_of_birth', 'date_of_death')
#     fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
#     inlines = [BooksInline]
#
#
# class BooksInstanceInline(admin.TabularInline):
#     """Определяет формат вставки экземпляра онлайн-книги (используется в Book Admin)"""
#     model = BookInstance
#
#
# class BookAdmin(admin.ModelAdmin):
#     """Объект администрирования для книжных моделей.
#     Определяет:
#     - поля, которые будут отображаться в виде списка (list_display)
#     - - добавляет встроенное добавление экземпляров книги в режиме просмотра книги (встроенные строки)
#     """
#     list_display = ('title', 'author', 'display_genre')
#     inlines = [BooksInstanceInline]
#
#
# admin.site.register(Book, BookAdmin)
#
#
# class BookInstanceAdmin(admin.ModelAdmin):
#     """Объект администрирования для моделей BookInstance.
#       Определяет:
#       - поля, которые будут отображаться в виде списка (list_display)
#       - фильтры, которые будут отображаться на боковой панели (list_filter)
#       - группировка полей по разделам (fieldsets)
#     """
#     list_display = ('book', 'status', 'borrower', 'due_back', 'id')
#     list_filter = ('status', 'due_back')
#
#     fieldsets = (
#         (None, {
#             'fields': ('book', 'imprint', 'id')
#         }),
#         ('Availability', {
#             'fields': ('status', 'due_back', 'borrower')
#         }),
#     )
