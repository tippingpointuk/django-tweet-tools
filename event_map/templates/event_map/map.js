{% load static %}
var xmlhttp = new XMLHttpRequest();
var url = "/map/{{ map_id }}/json?{{ request.META.QUERY_STRING }}";
var now = new Date()

xmlhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        var actions = JSON.parse(this.responseText);
        makeMap(actions);
    }
};
xmlhttp.open("GET", url, true);
xmlhttp.send();


function makeMap(actions) {
  var actionsData = {"events":actions};

  console.log(actionsData);

  var actionsMap = L.map("Chaos-Map-{{ map_id }}",{
                      center: [55.0006601,-2.7039512],
                      crs: L.CRS.EPSG3857,
                      zoom: 6,
                      zoomControl: true,
                      preferCanvas: false,
                  });
  var customMarker = L.icon({
      iconUrl: "/assets/images/fist_pointer_shadow.png",
      shadowUrl: "/assets/images/red_fist_marker.png",
      iconSize: [70,125],
      shadowSize: [125,125],
      iconAnchor:   [35,125], // point of the icon which will correspond to marker's location
      shadowAnchor: [0,125],  // the same for the shadow
      popupAnchor:  [0, -125] // point from which the popup should open relative to the iconAnchor
  })

  var redMarker = new L.Icon({
   iconUrl: '{% static "event_map/marker-icon-red.png" %}',
   shadowUrl: '{% static "event_map/marker-shadow.png" %}',
   iconSize: [25, 41],
   iconAnchor: [12, 41],
   popupAnchor: [1, -34],
   shadowSize: [41, 41]
  });

  var titleLayer = L.tileLayer(
    "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg",{
      "attribution": "Map tiles by \u003ca href=\"http://stamen.com\"\u003eStamen Design\u003c/a\u003e, under \u003ca href=\"http://creativecommons.org/licenses/by/3.0\"\u003eCC BY 3.0\u003c/a\u003e. Data by \u0026copy; \u003ca href=\"http://openstreetmap.org\"\u003eOpenStreetMap\u003c/a\u003e, under \u003ca href=\"http://creativecommons.org/licenses/by-sa/3.0\"\u003eCC BY SA\u003c/a\u003e.",
      "detectRetina": false,
      "maxNativeZoom": 18,
      "maxZoom": 18,
      "minZoom": 0,
      "noWrap": false,
      "opacity": 1,
      "subdomains": "abc",
      "tms": false
    }
  ).addTo(actionsMap);

  var markerCluster = L.markerClusterGroup({
    maxClusterRadius: 25,
  });

  for (i in actions){
    action = actions[i]
    startDate = new Date(action["start_date"])
    // var markerLocation = action;
    if (action['map_exclude'] || action['online']){
      continue
    }
    var newMarker = L.marker([action["latitude"], action["longitude"]],{icon: redMarker});
    newMarker.bindPopup(/*html*/`
      <a href='${action['browser_url']}' target='_blank'>
        ${action['title']}
      </a>
    `)
    newMarker.actionData = action

    newMarker.on("click", markerClicked);
    newMarker.addTo(markerCluster);
  }
  markerCluster.addTo(actionsMap)
  actionsMap.on("zoomend",function(e){
    mapMoved(actionsMap, actions)
  })
  actionsMap.on("moveend",function(e){
    mapMoved(actionsMap, actions)
  })
  updateActionsList(actions)
}

function getVisablePoints(bounds, actions){
  var events = [];
  for (i in actions){
    let action = actions[i];
    let publish;
    var markerLocation = action;
    if (Object.keys(action).includes('latitude') && Object.keys(action).includes('longitude')){
      var latlng = L.latLng(markerLocation["latitude"], markerLocation["longitude"]);
      if (bounds.contains(latlng)){
        publish = true;
      }
    }else{
      publish=true
    }
    if (publish){
      events.push(action)
    }
  }
  return events
}
function updateActionsList(actions){
  var actionslisthtml = "";
  for (i in actions){
    let action = actions[i];
    var id = action["id"];
    console.log(action["start_date"])
    var start = new Date(action["start_date"].replace("Z", "+0100"));
    console.log(start);
    var options = { hour: 'numeric', minute: 'numeric'}
    var startTime = start.getTime() ? new Intl.DateTimeFormat('en-GB', options).format(start) : "";
    var options = { weekday: 'short', month: 'short', day: 'numeric'}
    var startDate = start.getTime() ? new Intl.DateTimeFormat('en-GB', options).format(start) : "";
    actionslisthtml = actionslisthtml.concat(/*html*/`
      <div class="Chaos-Blog-Item Action"  id="${ id }">
        <div class="top">
          <div class="description">
            <div class="header-line">
              <h3><a target="_blank" href="${action["browser_url"]}">${ action["title"] }</a></h3>
              <a target="_blank" href="${action["browser_url"]}"><span class="Chaos-Button">Join</span></a>
            </div>
            <p><time>${ startTime  }</time> on ${ startDate }</p>
            <address>${action['address'] }</address>
          </div>
        </div>
      </div>
    `);
    if (i > 100){
      actionslisthtml = actionslisthtml.concat(`...`);
      break
    }
  }
  $('.Action-List').html(actionslisthtml);
}

function mapMoved(actionsMap, actions) {
  var visibleActions = getVisablePoints(actionsMap.getBounds(), actions);
  updateActionsList(visibleActions);
}

function markerClicked(e){
  var lastMarker = $(`.Action-List .Action.first`).attr('id');
  var thisMarker = e.target.actionData.id ;

 $(`#${ lastMarker }`).removeClass('first');
 $(`#${ thisMarker }`).addClass('first');
}


$('#Postcode-Form-Input').on("keyup", function(e){
  // console.log(this);this.value
  var input = this.value;
  $.get(`https://api.postcodes.io/postcodes/${input}/autocomplete`, function(postcodes){
    var postcode = postcodes.result[0];
    console.log(postcodes);
    console.log(postcodes.result.length);
    $.get(`https://api.postcodes.io/postcodes/${postcode}`, function(data){

      newView = L.latLng(data.result.latitude, data.result.longitude);
      actionsMap.setView(newView);
      if (postcodes.result.length==1){
        actionsMap.setZoom(10);
      }else if (input.length > 1){
        actionsMap.setZoom(8);
      }else if (input.length > 2){
        actionsMap.setZoom(9);
      }else if (input.length > 3){
        actionsMap.setZoom(9.8);
      }else{
        actionsMap.setZoom(6);
      }
    })
  });
})
