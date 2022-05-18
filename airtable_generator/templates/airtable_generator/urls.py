from django.urls import path

from . import views

app_name = 'action_network'
urlpatterns = [
    # ex: /action_network/1/sync/
    path('<int:config_id>/sync/', views.sync, name='sync'),
]
