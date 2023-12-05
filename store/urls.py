from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
	path('', views.index, name = "index"),
	path('login', views.signin, name="signin"),
	path('logout', views.signout, name="signout"),
	path('registration', views.registration, name="registration"),
	path('book/<int:id>', views.get_book, name="book"),
	path('books', views.get_books, name="books"),
	path('category/<int:id>', views.get_book_category, name="category"),
	path('writer/<int:id>', views.get_writer, name = "writer"),
	path('generate_otp', views.get_generate_otp, name = "generate_otp"),
	path('submit_otp', views.get_submit_otp, name = "submit_otp")
]
