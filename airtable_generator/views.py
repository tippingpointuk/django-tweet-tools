from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils.encoding import iri_to_uri
from airtable import airtable
from os import environ
import random
from liquid import Template
import json

from .models import Config


def get_tweets(request, config_id):
    view = {
        'target': request.POST.get('targetView') or request.GET.get('targetView') or request.POST.get('mpView') or request.GET.get('mpView'),
        'tweets': request.POST.get('tweetView') or request.GET.get('tweetView')
    }
    max_tweets = int(request.POST.get('tweets')
                     or request.GET.get('tweets') or 4)
    print(view)
    # Get config
    config = get_object_or_404(Config, pk=config_id)

    # Get targets
    target_at = airtable.Airtable(
        config.target_base, environ.get(config.api_key_name))
    targets = []
    print('Getting targer')
    for r in target_at.iterate(config.target_table, view=view['target']):
        targets.append(r['fields'])
        print("got one"")

    # Get tweets
    tweets_at = airtable.Airtable(
        config.tweets_base, environ.get(config.api_key_name))
    tweet_table = tweets_at.iterate(config.tweets_table, view=view['tweets'])
    tweets = [{'tweet': r['fields']['Text']} for r in tweet_table]
    random.shuffle(tweets)
    results = {'tweets': []}
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
    return JsonResponse(results)


def tweet_to_html(tweet):
    words = []
    for line in tweet['tweet'].split('\n'):
        for word in line.split(' '):
            words.append(process_word(word))
        words.append('<br>')
    inner_html = ' '.join(words)
    html = f"""
        <div class=tweet onclick="sendOutreach(this)"  data-tweet="{ iri_to_uri(json.dumps(tweet['target'])) }">
          <a target="_blank" href="{ create_ctt(tweet['tweet']) }">
            { inner_html }
          </a>
        </div>
        """
    return html


def create_ctt(tweet, url=''):
    url = "https://twitter.com/intent/tweet"
    return f"{url}?text={ iri_to_uri(tweet) }&url={ iri_to_uri(url) }"


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
