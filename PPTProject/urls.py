from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('settings', views.settings, name='settings'),
    path('add-ticket', views.add_ticket, name='add-ticket'),
    path('edit-ticket/<str:pk>', views.edit_ticket, name='edit-ticket'),
    path('delete-ticket/<str:pk>', views.delete_ticket, name='delete-ticket'),
    path('buy-ticket', views.buy_ticket, name='buy-ticket'),
    path('complete-purchase', views.complete_purchase, name='complete-purchase'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('search', views.search, name='search'),
]
