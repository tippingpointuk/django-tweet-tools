# Tipping Point Tools

* Tweet Generator
* Event Map
* Action Network Advocacy Campaign outreach counter

## Prerequisites

* Docker
* Docker Compose

## Running Locally

to run locally add a .env file that looks like this:

```
MONGODB_HOST_STRING="DATABASE STRING FROM MONGODB HERE"
DJANGO_SECRET_KEY="SECRET KEY HERE"
DJANGO_DEBUG=true

AIRTABLE_API_KEY=keysomethingsomething # https://airtable.com/account
AN_API_KEY=alongapikey # https://actionnetwork.org/groups/<yourgroup>/apis
```

To start the container just run:

sh```
docker-compose up
```

If you get requirement errors add the `--build` flag.

## Contributing

Feel free to open pull requests.
