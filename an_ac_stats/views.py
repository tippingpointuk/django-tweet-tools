from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from os import environ
import requests

from .models import Campaign


def get_total_records(req, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    since_sync = timezone.now() - campaign.last_updated
    if since_sync.seconds > 30:
        update_records(campaign)
    return JsonResponse({'total_records': campaign.total_records})


def update_records(campaign):
    headers = {
        'content-type': 'application/json'
    }
    if environ.get(campaign.key):
        headers['OSDI-API-Token'] = environ[campaign.key]
    url = campaign.campaign_url+"/outreaches"
    res = requests.get(url, headers=headers)
    if 200 > res.status_code > 299:
        return
    ac = res.json()
    if 'total_records' not in ac.keys():
        pass
    campaign.total_records = ac['total_records']
    campaign.last_updated = timezone.now()
    campaign.save()
