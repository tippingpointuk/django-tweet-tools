from django.urls import path

from . import views

app_name = 'airtable_generator'
urlpatterns = [
    # ex: /action_network/1/sync/
    path('<int:config_id>/json', views.json_view, name='json'),
    path('<int:config_id>/embed', views.embed, name='embed'),
    path('<int:config_id>/embed2', views.embed2, name='embed2'),
    path('<int:config_id>/embed.js', views.embed_js, name='embed_js'),
    path('<int:config_id>', views.html, name='html'),
]
