from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone

from os import environ
import requests

from .models import Campaign


def get_total_records(req, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    since_sync = timezone.now() - campaign.last_updated
    output = {}
    if since_sync.seconds > 30:
        update_records(campaign)
    if campaign.total_records < campaign.boost_count:
        output['total_records'] = campaign.boost_count
    else:
        output['total_records'] = campaign.total_records
    return JsonResponse(output)


def update_records(campaign):
    headers = {
        'content-type': 'application/json'
    }
    if environ.get(campaign.key):
        headers['OSDI-API-Token'] = environ[campaign.key]
    if 'advocacy_campaigns' in campaign.campaign_url:
        url = campaign.campaign_url+"/outreaches"
    elif 'petitions' in campaign.campaign_url:
        url = campaign.campaign_url+"/signatures"
    elif 'forms' in campaign.campaign_url:
        url = campaign.campaign_url+"/submissions"
    elif 'fundraising_pages' in campaign.campaign_url:
        url = campaign.campaign_url+"/donations"
    res = requests.get(url, headers=headers)
    if 200 > res.status_code > 299:
        return
    ac = res.json()
    if 'total_records' not in ac.keys():
        print(ac)
        return
    campaign.total_records = ac['total_records']
    campaign.last_updated = timezone.now()
    campaign.save()


def outreach_button(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    context = {'request': request, 'campaign': campaign, 'test': 'TESTING'}
    return render(request, "an_ac_stats/button.html", context=context)
