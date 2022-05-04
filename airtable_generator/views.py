from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse
# from django.utils.encoding import iri_to_uri
from urllib.parse import quote
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from airtable import airtable
from os import environ
import random
from liquid import Template
import json

from .models import Config


def embed(request, config_id):
    # config = get_object_or_404(Config, pk=config_id)
    context = {'config_id': config_id}
    print(context)
    return render(request, 'airtable_generator/embed.html', context)


def embed2(request, config_id):
    # config = get_object_or_404(Config, pk=config_id)
    context = {
        'targetView': request.POST.get('targetView') or request.GET.get('targetView') or request.POST.get('mpView') or request.GET.get('mpView'),
        'tweetView': request.POST.get('tweetView') or request.GET.get('tweetView'),
        'maxTweets': int(request.POST.get('tweets')
                         or request.GET.get('tweets') or 4),
        'config_id': config_id
    }
    print(context)
    return render(request, 'airtable_generator/embed2.html', context)


def embed_js(request, config_id):
    # config = get_object_or_404(Config, pk=config_id)
    context = {
        'targetView': request.POST.get('targetView') or request.GET.get('targetView') or request.POST.get('mpView') or request.GET.get('mpView'),
        'tweetView': request.POST.get('tweetView') or request.GET.get('tweetView'),
        'maxTweets': int(request.POST.get('tweets')
                         or request.GET.get('tweets') or 4),
        'config_id': config_id
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
        target = targets[random.randrange(0, len(targets)-1)]
        target_filtered = {
            'name': target['Name'],
            'twitter': target['Twitter']
            }
        tweet_template = Template(tweet['tweet'])
        result = {
            'tweet': tweet_template.render(target=target_filtered),
            'target': target_filtered
        }
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
    html = f"""
        <div
            class=tweet onclick="sendOutreach(this)"
            data-tweet="{ quote(json.dumps(tweet['target'])) }">
          <a target="_blank" href="{ create_ctt(tweet['tweet']) }">
            { inner_html }
          </a>
        </div>
        """
    return mark_safe(html)


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

        return word
