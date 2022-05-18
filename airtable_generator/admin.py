from django.contrib import admin
from .models import Config
from os import environ
import requests


@admin.action(description="Create Advocacy Campaign")
def make_advocacy_campaign(modeladmin, request, queryset):
    headers = {
        'content-type': 'application/json'
    }
    for config in queryset:
        if config.action_network_advocacy_campaign != None:
            pass
        api_key = config.action_network_api_key_name
        if environ.get(api_key):
            headers['OSDI-API-Token'] = environ[api_key]
        elif api_key:
            headers['OSDI-API-Token'] = api_key
        else:
            pass
        url = "https://actionnetwork.org/api/v2/advocacy_campaigns"
        campaign_info = {
            'title': config.name,
            'origin_system': 'tweet_generator',
            'type': 'email'
        }
        res = requests.post(url, headers=headers, data=campaign_info)
        if 200 <= res.status_code < 299:
            campaign = res.json()
            link = campaign['_links']['self']['href']
            config.action_network_advocacy_campaign = link
            config.save()
            admin.ModelAdmin.message_user(request, f"""
                Created campaign for {config}
                """)
        else:
            admin.ModelAdmin.message_user(request, f"""
            There was an error creating an advocacy campaign for {config}
            """)


admin.site.register(Config)
