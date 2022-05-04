from django.urls import path

from . import views

app_name = 'airtable_generator'
urlpatterns = [
    # ex: /action_network/1/sync/
    path('<int:config_id>', views.get_tweets, name='get_tweets'),
]
