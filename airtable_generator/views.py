from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
# from django.utils.encoding import iri_to_uri
from urllib.parse import quote
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.template.loader import render_to_string
from airtable import airtable
from os import environ
import random
from liquid import Template
import json
import requests
import datetime

from .models import Config


def req_prop(request, prop):
    return request.POST.get(prop) or request.GET.get(prop)


def embed(request, config_id):
    # config = get_object_or_404(Config, pk=config_id)
    context = {'config_id': config_id}
    print(context)
    return render(request, 'airtable_generator/embed.html', context)


def embed2(request, config_id):
    # config = get_object_or_404(Config, pk=config_id)
    context = {
        'targetView': str(request.POST.get('targetView')
                          or request.GET.get('targetView')
                          or request.POST.get('mpView')
                          or request.GET.get('mpView')),
        'tweetView': str(request.POST.get('tweetView')
                         or request.GET.get('tweetView')),
        'maxTweets': int(request.POST.get('tweets')
                         or request.GET.get('tweets') or 4),
        'config_id': int(config_id),
        'base_url': str(request.POST.get('baseUrl')
                        or request.GET.get('baseUrl')
                        or 'https://django-tweet-tool.herokuapp.com'),
        'button_class': str(request.POST.get('buttonClass')
                            or request.GET.get('buttonClass')).replace(",", " "),
        'gather_emails': str(request.POST.get('gatherEmails')
                             or request.GET.get('gatherEmails')).lower() in ['true', '1'],
        'consent_text': str(req_prop(request, 'consentText')),
        'static_tweets': req_prop(request, 'staticTweets')
    }
    return render(request, 'airtable_generator/embed2.html', context)


def embed_js(request, config_id):
    # config = get_object_or_404(Config, pk=config_id)
    context = {
        'targetView': request.POST.get('targetView') or request.GET.get('targetView') or request.POST.get('mpView') or request.GET.get('mpView'),
        'tweetView': request.POST.get('tweetView') or request.GET.get('tweetView'),
        'maxTweets': int(request.POST.get('tweets')
                         or request.GET.get('tweets') or 4),
        'config_id': config_id,
        'base_url': request.POST.get('baseUrl') or request.GET.get('baseUrl') or 'https://django-tweet-tool.herokuapp.com',
        'preload': req_prop(request, 'preload')
    }
    javascript = render_to_string('airtable_generator/embed.js', context)
    return HttpResponse(javascript, content_type='application/javascript')


def html(request, config_id):
    context = get_tweet_data(request, config_id)
    return render(request, 'airtable_generator/index.html', context)


def json_view(request, config_id):
    tweets = get_tweet_data(request, config_id)
    return JsonResponse(tweets)


def get_tweet_data(request, config_id):
    view = {
        'target': request.POST.get('targetView') or request.GET.get('targetView') or request.POST.get('mpView') or request.GET.get('mpView'),
        'tweets': request.POST.get('tweetView') or request.GET.get('tweetView')
    }
    max_tweets = int(request.POST.get('tweets')
                     or request.GET.get('tweets') or 4)
    # Get config
    config = get_object_or_404(Config, pk=config_id)
    # Get targets
    target_at = airtable.Airtable(
        config.target_base, environ.get(config.api_key_name))
    target_table = target_at.iterate(config.target_table, view=view['target'])
    targets = [r['fields']
               for r in target_table if 'Twitter' in r['fields'].keys()]
    # Get tweets
    tweets_at = airtable.Airtable(
        config.tweets_base, environ.get(config.api_key_name))
    tweet_table = tweets_at.iterate(config.tweets_table, view=view['tweets'])
    tweets = [{'tweet': r['fields']['Text']} for r in tweet_table]
    # Randomise tweets
    random.shuffle(tweets)

    results = {'tweets': []}

    # Pick up to max number of tweets and process with random target
    for tweet in tweets[0:max_tweets]:
        if len(targets) > 1:
            target = targets[random.randrange(0, len(targets)-1)]
        elif len(targets) == 1:
            target = targets[0]
        else:
            target = {'Name': '', 'Twitter': ''}
        target_filtered = {
            'name': target['Name'],
            'twitter': target['Twitter']
            }
        tweet_template = Template(tweet['tweet'])
        result = {
            'tweet': tweet_template.render(target=target_filtered),
            'target': target_filtered
        }
        result['ctt'] = create_ctt(result['tweet'])
        result['html'] = tweet_to_html(result)
        results['tweets'].append(result)
    return results


def tweet_to_html(tweet):
    words = []
    for line in tweet['tweet'].split('\n'):
        for word in line.split(' '):
            words.append(process_word(word))
        words.append('<br>')
    inner_html = ' '.join(words)
    return mark_safe(inner_html)


def create_ctt(tweet, url=''):
    base_url = "https://twitter.com/intent/tweet"
    return f"{base_url}?text={ quote(tweet) }&url={ quote(url) }"


def process_word(word):
    span_class = None
    if len(word) <= 0 or not word:
        return ''
    if word[0] == '#':
        span_class = 'hashtag'
    elif word[0] == '@':
        span_class = 'at'
    elif '://' in word:
        span_class = 'url'
    if span_class:
        return f'<span class="{span_class}">{word}</span>'
    else:
        return word


def tweet_sent(request, config_id):
    # print(request.COOKIES['sessionid'])
    # Get config
    config = get_object_or_404(Config, pk=config_id)
    email = request.GET.get('email_address') or "None"
    opt_in = request.GET.get('opt_in')
    target = request.GET.get('target')
    tweet = request.GET.get('tweet')
    # Send outreach to action network
    headers = {
        'content-type': 'application/json'
    }
    if environ.get(config.action_network_api_key_name):
        headers['OSDI-API-Token'] = environ[config.action_network_api_key_name]
    print(opt_in)
    print(request.GET.get('opt_in'))
    if opt_in != 'true' or not email:
        email = request.headers.get(
            'X-Request-ID') or "anonymous"
    print(email)
    body = {
      "targets": [
        {
          "given_name": target,
          "family_name": ""
        }
      ],
      "person": {
        "email_addresses": [{"address": email}],
      },
      "message": tweet
    }
    url = config.action_network_advocacy_campaign+"/outreaches"
    res = requests.post(url, data=json.dumps(body), headers=headers)
    if 200 <= res.status_code < 299:
        data = res.json()
    else:
        return HttpResponse("Error in recording tweet")
    print(data)
    if opt_in != 'true':
        # Unsubscribe person
        person_url = data['_links']['osdi:person']['href']
    return HttpResponse("Tweet recorded")


def get_tweets_sent(request, config_id):
    config = get_object_or_404(Config, pk=config_id)
    updated = config.action_network_advocacy_campaign_records_last_updated
    if updated:
        since_update = timezone.now() - updated
        if since_update.seconds > 15:
            update_tweets_sent(request, config)
    else:
        update_tweets_sent(request, config)
    return JsonResponse({'tweets_sent': config.action_network_advocacy_campaign_records})


def update_tweets_sent(request, config):
    print('updating from action network')
    headers = {
        'content-type': 'application/json'
    }
    if environ.get(config.action_network_api_key_name):
        headers['OSDI-API-Token'] = environ[config.action_network_api_key_name]
    url = config.action_network_advocacy_campaign+"/outreaches"
    res = requests.get(url, headers=headers)
    if 200 > res.status_code > 299:
        return
    ac = res.json()
    if 'total_records' not in ac.keys():
        pass
    config.action_network_advocacy_campaign_records = ac['total_records']
    config.action_network_advocacy_campaign_records_last_updated = timezone.now()
    config.save()


def live(request, config_id):
    context = {
        'config_id': config_id,
        'base_url': (req_prop(request, 'baseUrl')
                     or "https://django-tweet-tool.herokuapp.com")
    }
    return render(request, 'airtable_generator/live.html', context)
