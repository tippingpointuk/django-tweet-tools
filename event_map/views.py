from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django.core.exceptions import FieldError
from django.views.decorators.clickjacking import xframe_options_exempt
from django.db.models import Q
import pyairtable
import os
import requests
import datetime

from .models import EventMap, Event, AirtableSync, ActionNetworkECSync

ALL_FIELDS = ["title", "description", "summary", "browser_url",
              "type", "featured_image_url",
              "total_tickets", "total_amount", "status",
              "start_date", "end_date", "all_day_date",
              "all_day", "capacity", "guests_can_invite_others",
              "transparence", "visibility", "timezone_identifier", "latitude",
              "longitude", "address", "online", "modified_date"
              ]
existing_fields = [f.name for f in Event._meta.get_fields()]
AVAILABLE_FIELDS = [f for f in ALL_FIELDS if f in existing_fields]


@xframe_options_exempt
def html_map(request, map_id):
    # Embedable HTML map of events
    return render(request, "event_map/map.html", context={"map_id": map_id})


def embed_map(request, map_id):
    # Embed code and preview
    return render(request, "event_map/embed.html", context={"map_id": map_id})


def embed_text_only_map(request, map_id):
    # Just the embed code (plain text)
    embed_code = render_to_string("event_map/embed_code.html",
                                  {"map_id": map_id, "request": request})
    return HttpResponse(embed_code, content_type='text/plain')


def json_map(request, map_id):
    map = get_object_or_404(EventMap, id=map_id)
    q = request.GET
    filters_input = {k[7:]: q.get(k) for k in q.keys() if k[0:7] == "filter_"}
    filters = {}
    # Loop through keys and get type from Event model
    for key in filters_input.keys():
        field_name = key.split("__")[0]
        field = Event._meta.get_field(field_name)
        if not field:
            continue
        print(field.to_python(filters_input[key]))
        filters[key] = field.to_python(filters_input[key])
    print(filters)
    events_lists = [
        Event.objects.filter(
            visibility="public", status="confirmed",
            airtable_sync__in=map.airtable_syncs.all()),
        Event.objects.filter(
            visibility="public", status="confirmed",
            action_network_ec_sync__in=map.action_network_ec_syncs.all())
    ]
    events = []
    for event_q in events_lists:
        if "past" not in q.keys():
            event_q = event_q.filter(start_date__gte=datetime.date.today())
        try:
            events_filtered = event_q.filter(**filters)
        except FieldError as err:
            return HttpResponseBadRequest(err)
        events.extend(list(events_filtered.values(*AVAILABLE_FIELDS, "id")))
    events.sort(key=lambda x: x['start_date'])
    return JsonResponse(events, safe=False)


def js_map(request, map_id):
    # map = get_object_or_404(EventMap, id=map_id)
    # events = Event.objects.filter(event_maps__id=map.id, visibility="public")
    # events_list = list(events.values(*AVAILABLE_FIELDS))
    # context = {"events_json": json.dumps(events_list)}
    javascript = render_to_string("event_map/map.js",
                                  {"map_id": map_id, "request": request })
    return HttpResponse(javascript, content_type='application/javascript')


def refresh_map(request, map_uuid):
    map = get_object_or_404(EventMap, uuid=map_uuid)
    airtable = 0
    an = {
        'removed': 0,
        'updated': 0,
        'new': 0
    }
    for airtable_sync in map.airtable_syncs.all():
        airtable += refresh_airtable(request, airtable_sync.uuid, map)
    for action_network_ec_sync in map.action_network_ec_syncs.all():
        an_sync_data =  refresh_action_network_ec(request,
                                                  action_network_ec_sync.uuid, map)
        for k in an.keys():
            an[k] += an_sync_data[k]
    context = {
        "name": map.name,
        "airtable_events": airtable,
        "an_events": an
    }
    return render(request, "event_map/refresh.html", context=context)


def refresh_airtable(request, airtable_uuid, event_map=None):
    airtable_sync = get_object_or_404(AirtableSync, uuid=airtable_uuid)
    last_synced = airtable_sync.last_synced
    airtable_sync.last_synced = timezone.now()
    airtable_sync.save()
    print(airtable_sync.name)
    filter = f"{{{airtable_sync.field_last_modified}}}>'{last_synced}'"
    api_key = os.environ.get(airtable_sync.key) or airtable_sync.key
    airtable_table = pyairtable.Table(api_key, airtable_sync.base,
                                      airtable_sync.table)
    print(f"Filtering buy this formula: {filter}")
    airtable_events = airtable_table.all(view=airtable_sync.view,
                                         formula=filter,
                                         return_fields_by_field_id=True)
    print(f"Found {len(airtable_events)} new events: ")
    for airtable_event in airtable_events:
        # try to get exsting event in events database
        event = airtable_event["fields"]
        print(f"Event: {event.get(airtable_sync.field_title)}")
        db_events = Event.objects.filter(airtable_id=airtable_event['id']
                                         ).filter(airtable_sync=airtable_sync)
        if len(db_events) == 0:
            db_event = Event()
        else:
            db_event = db_events[0]
        db_event.title = event.get(airtable_sync.field_title)
        db_event.start_date = event.get(airtable_sync.field_start_date)
        db_event.end_date = event.get(airtable_sync.field_end_date)
        db_event.browser_url = event.get(airtable_sync.field_browser_url)
        db_event.longitude = event.get(airtable_sync.field_longitude)
        db_event.latitude = event.get(airtable_sync.field_latitude)
        db_event.online = event.get(airtable_sync.field_online)
        db_event.address = event.get(airtable_sync.field_address)
        db_event.summary = event.get(airtable_sync.field_summary)

        db_event.airtable_sync = airtable_sync
        db_event.airtable_id = airtable_event["id"]

        db_event.save()

        if event_map:
            if len(db_event.event_maps.filter(id=event_map.id)) == 0:
                db_event.event_maps.add(event_map)

            db_event.save()
    return len(airtable_events)


def refresh_action_network_ec(request, uuid, event_map=None):
    sync = get_object_or_404(ActionNetworkECSync, uuid=uuid)
    output = {
        'removed': 0,
        'updated': 0,
        'new': 0
    }
    if request.GET.get("all"):
        print("getting all action network events")
        last_synced = None
    else:
        last_synced = sync.last_synced
    sync.last_synced = timezone.now()
    sync.save()
    api_key = os.environ.get(sync.api_key) or sync.api_key

    events = get_an_ec(api_key, sync.event_campaign_api, last_synced)

    for event in events:
        # try to get exsting event in events database
        event_api = event['_links']["self"]["href"]
        db_events = Event.objects.filter(action_network_api=event_api
                                         ).filter(action_network_ec_sync__id=sync.id)
        if len(db_events) == 0:
            db_event = Event()
            output['new'] += 1
        else:
            db_event = db_events[0]
            output['updated'] += 1
        for field in ALL_FIELDS:
            value = event.get(field)
            # if field.includes('_date'):
            #     value = event.get(field)
            setattr(db_event, field, value)

        db_event.action_network_ec_sync = sync
        db_event.action_network_api = event_api

        # Extract Location data
        loc = event["location"]
        db_event.latitude = loc["location"]["latitude"]
        db_event.longitude = loc["location"]["longitude"]
        address = loc['venue']
        if loc.get('address_lines'):
            address += f", {', '.join(loc['address_lines'])}"
        if loc.get('locality'):
            address += f", {loc['locality']}"
        if loc.get('region'):
            address += f", {loc['region']}"
        if loc.get('postal_code'):
            address += f", {loc['postal_code']}"
        db_event.address = address

        # Online Event?
        if address == "" or "online" in address.lower():
            db_event.online = True

        # Save event to add ID etc
        db_event.save()

        if event_map:
            if len(db_event.event_maps.filter(id=event_map.id)) == 0:
                db_event.event_maps.add(event_map)
            db_event.save()
    # if request.GET.get("all") and event_map:
    #     output['removed'] = cleanup_old_an_events(event_map, events)
    if request.GET.get("all") == 'true':
        output['removed'] = cleanup_old_an_ec_events(sync, events)
    return output


def get_an_ec(api_key, endpoint, last_synced):
    headers = {
        "Content-Type": "application/json",
        "OSDI-API-Token": api_key
    }
    params = {"page": 1}
    if last_synced:
        ls_date = f"{last_synced.year}-{last_synced.month}-{last_synced.day}"
        params["filter"] = f"modified_date gt '{ls_date}'"
    url = endpoint+"events"
    events = []
    new_events = [None]
    while len(new_events) > 0:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            page = res.json()
            new_events = page["_embedded"]["osdi:events"]
            events.extend(new_events)
        else:
            print(res)
            break
        params["page"] += 1
    print(f"Got {len(events)} events from Action Network")
    return events


def cleanup_old_an_events(map, events):
    print("cleaning up deteted events")
    map_events = Event.objects.filter(event_maps__id=map.id)
    removed = 0
    for event in map_events:
        match = [e for e in events if e['_links']["self"]["href"] == event.action_network_api]
        if len(match) > 0:
            continue
        event.event_maps.remove(map)
        removed += 1
    return removed


def cleanup_old_an_ec_events(sync, events):
    print('removing evnets')
    sync_events = Event.objects.filter(action_network_ec_sync__id=sync.id)
    removed = 0
    for event in sync_events:
        match = [e for e in events if e['_links']["self"]["href"] == event.action_network_api]
        if len(match) > 0:
            continue
        print(f'Removing: {event}, {event.id}')
        event.action_network_ec_sync = None
        event.save()
        removed += 1
    return removed
