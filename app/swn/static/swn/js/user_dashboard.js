const csrf = document.getElementsByName("csrfmiddlewaretoken");
console.log("CSRF");
console.log(csrf);
// -----------User Field Name Modal -----------------
const btnSaveUserField = document.getElementById("btnSaveUserField2");
const btnSaveUserFieldDismiss = document.getElementById("btnSaveUserDismiss");
const btnSaveUserFieldAndCalc = document.getElementById("btnSaveAndCalc");

const projectModal = document.getElementById("projectModal")
const projectModalTitle = document.getElementById("projectModalTitle");
const chartCard = document.getElementById("chartCard")
const btnModalCal = document.getElementById("btnModalCal")

const alertBox = document.getElementById("alert-box");
//const loadUrl = window.location.href + "load/";

// const userFieldNameModal = getElementById("userFieldNameModal")

// -------------MAP --------------------------------------
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

// const imageBounds = [[47.139868905, 15.585439895], [55.063879917, 5.557237723]]
const imageBounds = [
  [47.136744752, 15.57241882],
  [55.058996788, 5.564783468],
];
const dem = L.imageOverlay(imageUrl, imageBounds, (opacity = 0.1));


function getCookie(name) {
  console.log("Dashboard.js getCookie");
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
  // Ndvi: ndvi,
  // DEM: dem_germany,
  // DEM: dem_germany,
};

const map = new L.Map("map", {
  layers: [osm],
  overlay: [dem],
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
const demSwitch = document.getElementById("DEMSwitch");
// pilotCheckbox.stopPropagation()
projectRegionSwitch.addEventListener("change", function () {
  if (projectRegionSwitch.checked) {
    pilotGeojson.addTo(map);
  } else {
    pilotGeojson.remove();
  }
});

demSwitch.addEventListener("change", function () {
  if (demSwitch.checked) {
    dem.addTo(map);
  } else {
    dem.remove();
  }
});

//---------------MAP END-------------------------------


// btnSaveUserField.addEventListener("submit", (e) => {
//   e.preventDefault();
// });

// btnSaveUserFieldAndCalc.addEventListener("submit", (e) => {
//   e.preventDefault();
// });

// btnSaveUserFieldDismiss.addEventListener("click", (e) => {
//   console.log(currentUserField);
// });

const loadUrl = "load/";
const saveUrl = "save/";
const deleteUrl = "delete/";

const saveUserField = (userField) => {
  console.log("CSRF AJAX");
  console.log(csrf[0].value);
  $.ajax({
    type: "POST",
    url: saveUrl,
    data: {
      csrfmiddlewaretoken: csrf[0].value,
      geom: JSON.stringify(userField.geom.geometry),
      name: userField.name,
    },
    success: function (response) {
      userField.id = response.id;
      addLayerToSidebar(userField);
      userFields.push(userField);
    },
    error: function (response) {
      console.log(error);
    },
  });
};

class UserField {
  constructor(name, geom_json, layer, id = null) {
    this.name = name;
    this.geom = geom_json;
    this.layer = layer;
    this.id = id;
    this.projects = [];
    console.log(
      "UserField created",
      this.name,
      this.geom,
      this.layer,
      this.user,
      this.id,
      this.projects
    );
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

// Load all user  fields
const getData = () => {
  console.log("GetData executed");
  $.ajax({
    type: "GET",
    url: loadUrl,
    success: function (response) {
      $("#display-data").empty();

      const userFieldsDb = response.user_fields;
      userFieldsDb.forEach((el) => {
        const userField = new UserField(
          el.name,
          el.geom_json,
          L.geoJSON(el.geom_json),
          el.id
        );
        userFields.push(userField);
        addLayerToSidebar(userField);
      });
    },
    error: function (error) {
      console.log(error);
    },
  });
};

map.on(L.Draw.Event.CREATED, function (event) {
  console.log("event drawcreated");
  let layer = event.layer;
  let geom = layer.toGeoJSON();
  let name = userFieldNameInput();
  let userField = new UserField((fieldName = name), geom, layer);

  saveUserField(userField);
});

// todo check if fieldname already exists, else add number
const userFieldNameInput = () => {
  // const userFieldNameModal = new bootstrap.Modal(
  //   document.getElementById("userFieldNameModal")
  // );
  // userFieldNameModal.show();
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
  // return tuple/json with parameters from selection, e.g. as json {fieldname, selection: cancel/calculate/save}
  return fieldName;
  
};

const addLayerToSidebar = (userField) => {
  const accordion = document.createElement("li");
  accordion.setAttribute("class", "list-group-item");
  // accordion.focus()
  accordion.innerHTML = `  
  <div class="accordion-item">
    <div class="accordion-header" id="accordionHeader-${userField.id}">
      <div class="row">
        <div class="column col-8">
          <h6>
            <div class="form-check form-switch">
              <input type="checkbox" class="form-check-input" id="fieldSwitch-${userField.id}" checked>
              <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseField-${userField.id}" aria-expanded="true" aria-controls="collapseField-${projectIndex}">
                ${userField.name}
              </button>
          </h6>
        </div>
        <div class="column col-4">
          <form id="deleteAndCalcForm-${userField.id}">
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
          </form>
        </div> 
      
    </div> 
  </div> 
  `;
  // adding the UserField to the HTML-list element
  accordion.userField = userField;
  //adding the geometry to the displayed drawnItems-layer
  userField.layer.addTo(drawnItems);
  //append the list element to list
  userLayerList.appendChild(accordion);

  // connect the field geometry to the switch in the sidebar
  const switchId = `fieldSwitch-${userField.id}`;
  const inputSwitch = document.getElementById(switchId);

  inputSwitch.addEventListener("change", (e) => {
    if (inputSwitch.checked) {
      userField.layer.addTo(map);
    } else {
      userField.layer.remove();
    }
  });

  inputSwitch.dispatchEvent(new Event("change"));
}
  
//   const deleteCalcId = `deleteAndCalcForm-${userField.id}`;
//   const deleteAndCalcForm = document.getElementById(deleteCalcId);

//   deleteAndCalcForm.addEventListener("submit", (e) => {
//     console.log("UserField.geom.geometry");
//     console.log(userField.geom.geometry);
//     $.ajax({
//       method: "POST",
//       url: saveUrl,
//       data: {
//         csrfmiddlewaretoken: csrftoken,
//         geom: JSON.stringify(userField.geom.geometry),
//         name: userField.name,
//       },
//       success: function (response) {
//         console.log("Save success");
//         console.log(response);
//         userField.id = response.id;
//       },
//       error: function (error) {
//         console.log("Ajax error");
//         console.log(error);
//       },
//     });
//     e.preventDefault();
//   });
// };

userLayerList.addEventListener("click", (e) => {
  console.log("userLayerList.addEventListener");
  console.log(e.target);
  const listElement = e.target.closest("li");

  if (e.target.classList.contains("delete")) {
    console.log("DELETE");
    let confirmDelete = confirm("Are you sure to delete");
    if (confirmDelete) {
      const id = listElement.userField.id;
      console.log("ID: ", id);
      userFields = userFields.filter((uf) => uf !== listElement.userField);
      console.log("userFields=....");
      listElement.userField.layer.remove(); // removes shape from map
      console.log("listElement.userField.geom.remove()");
      listElement.remove(); // removes HTML element from sidebar
      // removes field from db
      $.ajax({
        type: "POST",
        url: deleteUrl + id,
        data: {
          csrfmiddlewaretoken: csrf[0].value,
        },
        success: function (response) {

          console.log("Delete Success");
        },
        error: function (response) {
          console.log(error);
        },
      });
    }
  } else if (e.target.classList.contains("field-menu")) {
    // TODO the hardcoded modal is triggered from button
    console.log("field-menu clicked");
  } else if (e.target.classList.contains("field-edit")) {
    // TODO the hardcoded modal is triggered from button
    console.log("field-edit clicked");
    projectModalTitle.innerText = listElement.userField.name;
    console.log("listElement.layer", listElement.userField.layer);
    // console.log("Area", L.GeometryUtil.geodesicArea(listElement.userField.layer.getLatLngs()))
  }
});

const monicaFieldCalculation = () => {
  console.log("monicaFieldCalculation")
}

btnModalCal.addEventListener('click', function () {
  getChart()
  chartCard.classList.remove("d-none");

})

$('#projectModal').on('hide.bs.modal', function (e){
  if (!chartCard.classList.contains("d-none")) {
    chartCard.classList.add("d-none")
    
  }
})


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

getData();

// NDVI from https://github.com/GeoTIFF/georaster-layer-for-leaflet-example/blob/master/examples/ndvi.html

// const demUrl = "{% static 'data/dem_de_1000_rendered_img_4326.tif' %}"
// const dem_germany = L.tileLayer(demUrl, { maxZoom: 18, attribution: topoAttrib });

