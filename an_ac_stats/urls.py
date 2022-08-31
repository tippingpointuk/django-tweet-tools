from django.urls import path

from . import views

app_name = 'an_ac_stats'
urlpatterns = [
    path('<int:campaign_id>/records', views.get_total_records, name='records'),
    path('<int:campaign_id>/buttons', views.outreach_button, name='buttons'),
    path('group/<int:campaign_group_id>', views.get_total_records_campaign_group, name='group_records'),
]
