from django.urls import path

from . import views

app_name = 'an_ac_stats'
urlpatterns = [
    path('<int:campaign_id>/records', views.get_total_records, name='records'),
]
