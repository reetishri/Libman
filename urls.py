from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'library'

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('rules/', views.rules, name='rules'),
    path('about/', views.contact, name='contact'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'), 
    path('logout/', views.user_logout, name='logout'), #logout url
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('password_change/', views.password_change, name='password_change'),
    path('book_catalogue/', views.book_catalogue, name='book_catalogue'),
    path('book_record/', views.book_record, name='book_record'),
    path('issue_return/', views.issue_return, name='issue_return'),
    path('book_enquiry/', views.book_enquiry, name='book_enquiry'),
    path('student_enquiry/', views.student_enquiry, name='student_enquiry'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)