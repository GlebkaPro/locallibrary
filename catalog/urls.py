from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='index'),
  path('books/', views.BookListView.as_view(), name='books'),
  path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
  path('book/<int:book_id>/create_copy/', views.create_book_copy, name='create-book-copy'),
  path('add-book/', views.add_book, name='add-book'),
  path('book/<int:book_id>/edit/', views.edit_book, name='edit-book'),
  path('book/<int:book_id>/delete/', views.delete_book, name='delete-book'),
  path('add/genre/', views.add_genre, name='add-genre'),
  path('add/language/', views.add_language, name='add-language'),
  path('create_book_exemplar/', views.create_book_exemplar, name='create_book_exemplar'),
  path('list_book_exemplar/', views.list_book_exemplar, name='list_book_exemplar'),
  path('list_publishers/', views.list_publishers, name='list_publishers'),
  path('create_publisher/', views.create_publisher, name='create_publisher'),
]

urlpatterns += [
  path('authors/', views.AuthorListView.as_view(), name='authors'),
  path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
  path('author/add/', views.add_author, name='add-author'),
  path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
  path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
  path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
]

urlpatterns += [
  path('create_user/', views.create_user, name='create_user'),
  path('user_list/', views.user_list, name='user_list'),
  path('user_loans/<int:pk>/', views.UserLoansListView.as_view(), name='user_loans'),
]

urlpatterns += [
  path('bookinstance/add/', views.add_bookinstance, name='add-bookinstance'),
  path('return/<uuid:book_instance_id>/', views.return_book, name='return-book'),
  path('book/<int:book_id>/reserve/', views.reserve_book, name='reserve-book'),
  path('edit-bookinstance/<uuid:bookinstance_id>/', views.edit_bookinstance, name='edit-bookinstance'),
  path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
  path('cancel_reservation/<uuid:bookinst_id>/', views.cancel_reservation, name='cancel_reservation'),
]

urlpatterns += [
  path('mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
  path(r'borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),
]

urlpatterns += [
  path('profile/', views.ProfileUser.as_view(), name='profile'),
  path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]

urlpatterns += [
  path('book/create/', views.BookCreate.as_view(), name='book-create'),
  path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
  path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]

urlpatterns += [
  path('accept_acts/', views.AcceptActListView.as_view(), name='accept_act_list'),
  path('create_accept_act/', views.CreateAcceptActView.as_view(), name='create_accept_act'),
  path('add_position_accept_act/<int:pk>/', views.AddPositionAcceptActView.as_view(), name='add_position_accept_act'),
  path('edit_accept_act/<int:pk>/', views.EditAcceptActView.as_view(), name='edit_accept_act'),
  path('edit_position_accept_act/<int:pk>/', views.EditPositionAcceptActView.as_view(),
       name='edit_position_accept_act'),
  path('delete_position_accept_act/<int:pk>/', views.DeletePositionAcceptActView.as_view(),
       name='delete_position_accept_act'),
  path('create_accounting/<int:pk>/', views.CreateAccountingView.as_view(), name='create_accounting'),
  path('create_debiting_act/', views.CreateDebitingActView.as_view(), name='create_debiting_act'),
  path('debiting_act_list/', views.DebitingActListView.as_view(), name='debiting_act_list'),
  path('edit_debiting_act/<int:pk>/', views.EditDebitingActView.as_view(), name='edit_debiting_act'),
  path('add_position_debiting_act/<int:pk>/', views.AddPositionDebitingActView.as_view(),
       name='add_position_debiting_act'),
  path('edit_position_debiting_act/<int:pk>/', views.EditPositionDebitingActView.as_view(),
       name='edit_position_debiting_act'),
  path('delete_position_debiting_act/<int:pk>/', views.DeletePositionDebitingActView.as_view(),
       name='delete_position_debiting_act'),

  path('create_source/', views.create_source, name='create_source'),
  path('create_fiz_person_source/', views.create_fiz_person_source, name='create_fiz_person_source'),
  path('source_list/', views.source_list, name='source_list'),
  path('fiz_person_source_list/', views.fiz_person_source_list, name='fiz_person_source_list'),
  path('accept_act/<int:pk>/', views.AcceptActDetailView.as_view(), name='accept_act_detail'),
  path('accept_act/<int:pk>/print/', views.PrintAcceptActView.as_view(), name='print_accept_act'),
]

urlpatterns += [
  path('create/', views.create_event, name='create_event'),
  path('edit/<int:event_id>/', views.edit_event, name='edit_event'),
  path('delete/<int:event_id>/', views.delete_event, name='delete_event'),
  path('events/', views.event_list, name='event_list'),
  path('events_a/', views.event_list_borrower, name='event_list_borrower'),
  path('rooms/', views.room_list, name='room_list'),
  path('rooms/create/', views.create_room, name='create_room'),
  path('type-rooms/', views.type_room_list, name='type_room_list'),
  path('type-rooms/create/', views.create_type_room, name='create_type_room'),
  path('type-rooms/edit/<int:type_room_id>/', views.edit_type_room, name='edit_type_room'),
  path('type-rooms/delete/<int:type_room_id>/', views.delete_type_room, name='delete_type_room'),
  path('rooms/edit/<int:room_id>/', views.edit_room, name='edit_room'),
  path('rooms/delete/<int:room_id>/', views.delete_room, name='delete_room'),
  path('participants/<int:event_id>/', views.participants_list, name='participants_list'),
  path('participants/<int:event_id>/add/', views.add_participant, name='add_participant'),
  path('events/<int:event_id>/participants/<int:participant_id>/edit/', views.edit_participant,
       name='edit_participant'),
  path('events/<int:event_id>/participants/<int:participant_id>/delete/', views.delete_participant,
       name='delete_participant'),
  path('events/<int:event_id>/register/', views.register_to_event, name='register_to_event'),
  path('cancel_registration/<int:registration_id>/', views.cancel_registration, name='cancel_registration'),
  path('events/<int:event_id>/', views.detail_event, name='detail_event'),
]

urlpatterns += [
  path('create_request/', views.create_request, name='create_request'),
  path('requests/', views.request_list, name='request_list'),
  path('requests/<int:request_id>/edit/', views.edit_request, name='edit_request'),
  path('requests/<int:request_id>/delete/', views.delete_request, name='delete_request'),
  path('accept/<int:request_id>/', views.accept_request, name='accept_request'),  # Новый URL для принятия запроса
  path('reject/<int:request_id>/reason/', views.reject_request, name='reject_request'),
]

urlpatterns += [
  path('request/<int:request_id>/delete/', views.profile_delete_request, name='profile_delete_request'),
  path('register_to_event_again/<int:registration_id>/', views.profile_register_to_event,
       name='profile_register_to_event'),
]
