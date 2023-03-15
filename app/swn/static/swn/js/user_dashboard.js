const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib =
  '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });

const satelliteUrl =
  "http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const satelliteAttrib =
  "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community";
const satellite = L.tileLayer(satelliteUrl, {
  maxZoom: 18,
  attribution: satelliteAttrib,
});

const topoUrl = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png";
const topoAttrib =
  'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)';
const topo = L.tileLayer(topoUrl, { maxZoom: 18, attribution: topoAttrib });

const alertBox = document.getElementById("alert-box");
//const loadUrl = window.location.href + "load/";
const loadUrl = "load/";
const saveUrl = window.location.href + "save/";

const csrf = document.getElementsByName("csrfmiddlewaretoken");
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

const handleAlerts = (type, msg) => {
  // https://getbootstrap.com/docs/5.2/components/alerts/#examples
  // types can be: primary, secondary, success, danger, warning, info, light, dark
  alertBox.innerHTML = `
      <div class="alert alert-${type} alert-dismissible " role="alert">
          ${msg}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close">
      </div>`;
  alertBox.classList.remove("d-none");
  setTimeout(() => {
    alertBox.classList.add("d-none");
  }, 2000);
};

// create Map
const baseMaps = {
  "Open Street Maps": osm,
  Satellit: satellite,
  Topomap: topo,
};

const map = new L.Map("map", {
  layers: [osm],
  center: new L.LatLng(52.338145830363914, 13.85877631507592),
  zoom: 8,
});

// Spreewasser:N overlay, pilotRegion from data/pilotregion.js
const pilotGeojson = L.geoJSON(pilotRegion);

pilotGeojson.setStyle(function (feature) {
  return {
    fillColor: "white",
    color: "purple",

    // borderColor: 'black'
  };
});
pilotGeojson.addTo(map);

// Leaflet Control top-right
// https://github.com/brunob/leaflet.fullscreen
const fullScreenControl = new L.Control.FullScreen({
  position: "topright",
});
map.addControl(fullScreenControl);

// search for locations
const GeocoderControl = new L.Control.geocoder({
  position: "topright",
});
map.addControl(GeocoderControl);

//add map scale
const mapScale = new L.control.scale({
  position: "bottomright",
}).addTo(map);

var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);
// Draw functionality
var drawControl = new L.Control.Draw({
  position: "topright",
  draw: {
    circlemarker: false,
    polyline: false,
    polygon: {
      allowIntersection: false,
      showArea: true,
    },
  },
  edit: {
    featureGroup: drawnItems,
  },
});

map.addControl(drawControl);

// function onMapClick(e) {
//   alert("You clicked the map at " + e.latlng);
//   console.log('Target')
//   console.log(e.target.layer)
// }

// map.on('click', onMapClick);

// SIDEBAR
// Adds the sidebar div from HTML to the map as sidebar
const sidebarLeft = L.control
  .sidebar("sidebar", {
    closeButton: true,
    position: "left",
  })
  .addTo(map);

const sidebar = document.getElementById("sidebar");
const baseLayers = document.getElementById("baseLayerList");

// LayerControl is moved to sidebar
const layerSwitcher = L.control.layers(baseMaps).addTo(map);
const layerControls = document.querySelectorAll(
  "#map > div.leaflet-control-container > div.leaflet-top.leaflet-right > div.leaflet-control-layers.leaflet-control > section > div.leaflet-control-layers-base > label"
);

// reverse order to prepend baselayers before project region
for (let i = layerControls.length - 1; i >= 0; i--) {
  let li = document.createElement("li");
  li.classList.add("list-group-item");
  li.appendChild(layerControls[i]);
  baseLayers.prepend(li);
}

// hiding the default layer switcher icon
document.querySelector(
  "#map > div.leaflet-control-container > div.leaflet-top.leaflet-right > div.leaflet-control-layers.leaflet-control"
).hidden = true;

const projectRegionSwitch = document.getElementById("projectRegionSwitch");
// pilotCheckbox.stopPropagation()
projectRegionSwitch.addEventListener("change", function () {
  if (projectRegionSwitch.checked) {
    pilotGeojson.addTo(map);
  } else {
    pilotGeojson.remove();
  }
});

class UserField {
  constructor(name, geom_json, layer, id) {
    this.name = name;
    this.geoJson = geom_json;
    this.layer = layer;
    this.user = 0;
    this.id = id;
    this.projects = [];
  }
}

class UserProject {
  constructor(userField, cropID) {
    this.userField = userField;
    this.cropID = cropID;
    this.calculation = {};
    this.timestamp = Date.now();
  }
}

var userFields = [];
let projectIndex = 0;
const userLayerList = document.getElementById("sidebarLayerList");
// Load all user projects and fields
$.ajax({
  type: "GET",
  url: loadUrl,
  success: function (response) {
    $("#display-data").empty();

    const userFields = response.user_fields;
    userFields.forEach((el) => {
      $("#display-data").append(`<li>${el.name}</li><li>${el.geom_json}</li>`);
      const userField = new UserField(
        el.name,
        el.geom_json,
        L.geoJSON(el.geom_json),
        el.id
      );
      addLayerToSidebar(userField);
    });
  },
  error: function (error) {
    console.log(error);
  },
});

map.on(L.Draw.Event.CREATED, function (event) {
  // console.log('event drawcreated' + JSON.stringify(event.layer))
  event.layer.addTo(drawnItems);
  let layer = event.layer;
  let type = event.layerType;
  let geomJson = layer.toGeoJSON();
  const currentUserField = new UserField(
    (fieldName = userFieldNameInput()),
    geomJson,
    layer,
    (id = 5)
  );

  addLayerToSidebar(currentUserField);
});

/// 2023-03-8 WAS TRYING TO MAKE THE PROMPT A MODAL, CSRF TOKEN is the problem!!!
// todo check if fieldname already exists, else add number
function userFieldNameInput() {
  // userFieldNameModal.classList.remove('fade')
  // userFieldNameModal.classList.add('show')
  const userFieldNameModal = new bootstrap.Modal(
    document.getElementById("userFieldNameModal")
  );
  userFieldNameModal.show();
  let fieldName = prompt(
    "Bitte geben Sie einen Namen für das Feld an",
    "Acker Bezeichnung"
  ).trim();
  if (fieldName !== "") {
    if (userFields.some((proj) => proj.name === fieldName)) {
      alert(`please change name since ${fieldName} it already exists`);
      fieldName = userFieldNameInput();
    }
  } else {
    alert(`This field can not be empty. Please enter a name!`);
    fieldName = userFieldNameInput();
  }
  return fieldName;
}

const addLayerToSidebar = (userField) => {
  const accordion = document.createElement("li");
  accordion.setAttribute("class", "list-group-item");
  // accordion.focus()
  accordion.innerHTML = `  
  <div class="accordion-item">
    <div class="accordion-header" id="accordionHeader-${userField.id}">
      <h6>
        <div class="form-check form-switch">
          <input type="checkbox" class="form-check-input" id="fieldSwitch-${userField.id}" checked>
          <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseField-${userField.id}" aria-expanded="true" aria-controls="collapseField-${projectIndex}">
            ${userField.name}
          </button>
      </h6>
    </div>
    <div id="collapseField-${userField.id}" class="accordion-collapse collapse show" aria-labelledby="accordionHeader-${userField.id}">
      <span>
        <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#projectModal">
            <i class="fa-regular fa-pen-to-square field-edit"></i>
        </button>
      </span>
      <span>
        <button type="button" class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#fieldInfoModal">
            <i class="fa-solid fa-ellipsis-vertical field-menu"></i>
        </button>
      </span>
      <span>
        <button type="button" class="btn btn-outline-secondary btn-sm">
          <i class="fa-regular fa-trash-can delete"></i>
        </button>
      </span>
    </div>
    <form>
      <button id="userFieldNewCalcBtn-${userField.id}" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#projectModal">Neue Berechnung</button>
      <button id="userFieldSaveBtn-${userField.id}" class="btn btn-danger">Feld speichern</button>
    </form>
  </div> 
  `;

  accordion.userField = userField;

  userField.layer.addTo(drawnItems);
  userLayerList.appendChild(accordion);
  const switchId = `fieldSwitch-${userField.id}`;
  const inputSwitch = document.getElementById(switchId);

  inputSwitch.addEventListener("change", (e) => {
    inputSwitch.addEventListener("change", function () {
      if (inputSwitch.checked) {
        userField.layer.addTo(map);
      } else {
        userField.layer.remove();
      }
    });
  });

  inputSwitch.dispatchEvent(new Event("change"));

  const saveBtnId = `userFieldSaveBtn-${userField.id}`;
  const saveBtn = document.getElementById(saveBtnId);

  saveBtn.addEventListener("click", (e) => {
    console.log("Field save");
    console.log(e);
    handleAlerts("danger", "Field save");
    // temp
    let save = true;
    if (save) {
      $.ajax({
        type: "POST",
        url: saveUrl,
        data: {
          csrfmiddlewaretoken: csrftoken,
        },
        success: function (response) {
          console.log("Save success");
          console.log(response);
        },
        error: function (error) {
          console.log("Ajax error");
          console.log(error);
        },
      });
    } else {
      // update
      $.ajax({
        type: "POST",
        url: updateUrl + userField.id,
        data: {
          csrfmiddlewaretoken: csrf[0].value,
        },
        success: function (response) {
          console.log("Save success");
        },
        error: function (error) {
          console.log(error);
        },
      });
    }
  });
};

userLayerList.addEventListener("click", (e) => {
  //console.log(e.target)
  const listElement = e.target.closest("li");

  if (e.target.classList.contains("delete")) {
    let confirmDelete = confirm("Are you sure to delete");
    if (confirmDelete) {
      userFields = userFields.filter((uf) => uf !== listElement.userField);
      listElement.userField.geom.remove(); // removes shape from map
      listElement.remove(); // removes HTML element from sidebar
    }
  } else if (e.target.classList.contains("field-menu")) {
    console.log("field-menu clicked");
  } else if (e.target.classList.contains("field-edit")) {
    console.log("field-edit clicked");
  }
});
// Monica-Modal

// $(document).ready(function () {

//   $('#projectModal').on('show.bs.modal', function () {

//     var projectModal = $('#projectModal')

//     $('.modal-container').html(this)
//     $('#map-container').hide()
//   }),
//   $('#projectModal').on('hide.bs.modal', function () {
//     $('#map-container').show()
//   });
//   $('#chartModal').on('show.bs.modal', function () {

//     var chartModal = $('#chartModal')

//     $('.modal-container').html(this)
//     $('#map-container').hide()
//   }),
//   $('#chartModal').on('hide.bs.modal', function () {
//     $('#map-container').show()
//   })
// })

$(document).ready(function () {
  $("#chartModal").on("show.bs.modal", function () {
    var chartModal = $("#chartModal");

    $(".modal-container").html(this);
    $("#map-container").hide();
  }),
    $("#chartModal").on("hide.bs.modal", function () {
      $("#map-container").show();
    });
});
// console.log(myModal.innerHTML)

// $(document).ready(function () {
//   $('#myModal').on('show.bs.modal', function () {
//       var mod = $('.modal');
//       $('.insidemodal').html(mod);
//   });
// });
