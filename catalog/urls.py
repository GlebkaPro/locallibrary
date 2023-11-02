from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>',views.AuthorDetailView.as_view(), name='author-detail'),
    path('create_user/', views.create_user, name='create_user'),  # Добавление пользователя
    path('user_list/', views.user_list, name='user_list'), # список пользователей
    path('bookinstance/add/', views.add_bookinstance, name='add-bookinstance'),
    path('add-book/', views.add_book, name='add-book'),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit-book'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete-book'),
    path('author/add/', views.add_author, name='add-author'),
    path('return/<uuid:book_instance_id>/', views.return_book, name='return-book'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
    path('book/<int:book_id>/reserve/', views.reserve_book, name='reserve-book'),
    path('edit-bookinstance/<uuid:bookinstance_id>/', views.edit_bookinstance, name='edit-bookinstance'),
]


urlpatterns += [
    path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
    path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),  # Added for challenge
]


# Add URLConf for librarian to renew a book.
urlpatterns += [
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]


# Add URLConf to create, update, and delete authors
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
]

# Add URLConf to create, update, and delete books
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]


