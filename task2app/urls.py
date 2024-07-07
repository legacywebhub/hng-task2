from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/register', views.register, name='register'),
    path('auth/login', views.login, name='login'),
    path('api/users/<str:userId>', views.user, name='user'),
    path('api/organisations', views.organisations, name='organisations'), # POST & GET
    path('api/organisations/<str:orgId>', views.organisation, name='organisation'),
    path('api/organisations/<str:orgId>/users', views.addUserToOrg, name='add_user_to_org'),
]