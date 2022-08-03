from django.urls import path

from . import views

app_name = 'event_map'
urlpatterns = [
    path('<int:map_id>', views.html_map, name='html'),
    path('<int:map_id>/', views.html_map, name='html'),
    path('<int:map_id>/embed', views.embed_map, name='embed'),
    path('<int:map_id>/embed_text', views.embed_text_only_map,
         name='embed_text'),
    path('<int:map_id>/json', views.json_map, name='json'),
    path('<str:map_uuid>/refresh', views.refresh_map, name='refresh'),
    path('<int:map_id>.js', views.js_map, name='js'),
    path('<str:uuid>/refresh_an_ec', views.refresh_action_network_ec,
         name='refresh_an_ec'),

]
