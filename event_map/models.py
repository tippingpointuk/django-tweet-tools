from django.db import models
from django.utils import timezone
import uuid

EVENT_FIELDS = ["title", "description", "summary", "browser_url",
                "administrative_url", "type", "featured_image_url",
                "total_accepted", "total_tickets", "total_amount", "status",
                "instructions", "start_date", "end_date", "all_day_date",
                "all_day", "capacity", "guests_can_invite_others",
                "transparence", "visibility", "timezone_identifier", "latitude",
                "longitude"
                ]


class Event(models.Model):
    # OSDI fields
    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    browser_url = models.CharField(max_length=200)
    visibility = models.CharField(max_length=200)
    summary = models.CharField(max_length=1000, null=True)
    status = models.CharField(max_length=200, null=True)
    modified_date = models.DateTimeField(default=timezone.now)

    # Extra fields
    online = models.BooleanField(default=False)
    address = models.CharField(max_length=200)

    # Location fields
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Linked Syncs
    # - Airtable
    airtable_sync = models.ForeignKey('AirtableSync',
                                      on_delete=models.CASCADE, null=True)
    airtable_id = models.CharField(max_length=50, null=True)

    # - Action Network
    action_network_api = models.CharField(max_length=200, null=True)
    action_network_ec_sync = models.ForeignKey('ActionNetworkECSync',
                                               on_delete=models.CASCADE,
                                               null=True)
    # Linked maps
    event_maps = models.ManyToManyField("EventMap")

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f"Event {self.id}"


class AirtableSync(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    key = models.CharField(max_length=100)
    base = models.CharField(max_length=50)
    table = models.CharField(max_length=50)
    view = models.CharField(max_length=50)

    field_title = models.CharField(max_length=50)
    field_start_date = models.CharField(max_length=50)
    field_end_date = models.CharField(max_length=50, null=True)
    field_browser_url = models.CharField(max_length=50)
    field_latitude = models.CharField(max_length=50, null=True)
    field_longitude = models.CharField(max_length=50, null=True)
    field_online = models.CharField(max_length=50, null=True)
    field_address = models.CharField(max_length=50, null=True)
    field_last_modified = models.CharField(max_length=50, null=True)
    field_visibility = models.CharField(max_length=200, default="Visibility")
    field_summary = models.CharField(max_length=200, null=True)

    last_synced = models.DateTimeField()

    def __str__(self):
        return self.name


class EventMap(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    airtable_syncs = models.ManyToManyField(AirtableSync, blank=True)

    action_network_ec_syncs = models.ManyToManyField("ActionNetworkECSync",
                                                     blank=True)

    def __str__(self):
        return f"{self.name} ({self.uuid})"


class ActionNetworkECSync(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    api_key = models.CharField(max_length=200)
    event_campaign_api = models.CharField(max_length=200)

    last_synced = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}: {self.uuid}"
