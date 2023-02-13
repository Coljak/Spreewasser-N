const osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const osm = L.tileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib})

const satelliteUrl = 'http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
const satelliteAttrib = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
const satellite = L.tileLayer(satelliteUrl, {maxZoom: 18, attribution: satelliteAttrib})

const topoUrl = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
const topoAttrib = 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
const topo = L.tileLayer(topoUrl, {maxZoom: 18, attribution: topoAttrib}) 

// create Map
const baseMaps = {
  'Open Street Maps': osm,
  'Satellit': satellite,
  'Topomap': topo
}

const map = new L.Map('map', {
  layers: [osm],
  center: new L.LatLng(52.338145830363914, 13.85877631507592 ), 
  zoom: 8
});

// Spreewasser:N overlay
const pilotGeojson = L.geoJSON(pilotRegion)

pilotGeojson.setStyle(function(feature) {
  return {
      fillColor: 'white',
      color: 'purple',
      
      // borderColor: 'black'
  }
})
pilotGeojson.addTo(map);

// Leaflet Control top-right
// https://github.com/brunob/leaflet.fullscreen
const fullScreenControl = new L.Control.FullScreen({
  position: 'topright'
})
map.addControl(fullScreenControl)


// search for locations
const GeocoderControl = new L.Control.geocoder({
  position: 'topright'
})
map.addControl(GeocoderControl)


//add map scale
const mapScale = new L.control.scale({
  position: 'bottomright'
}).addTo(map);

var drawnItems = new L.FeatureGroup();
     map.addLayer(drawnItems);
// Draw functionality
var drawControl = new L.Control.Draw({
  position: 'topright',
  draw: {
        circlemarker: false,
        polyline: false,
        polygon: {
          allowIntersection: false,
          showArea: true
        },
        
    },
    edit: {
      featureGroup: drawnItems
    }
});

map.addControl(drawControl)

// function onMapClick(e) {
//   alert("You clicked the map at " + e.latlng);
//   console.log('Target')
//   console.log(e.target.layer)
// }

// map.on('click', onMapClick);

// SIDEBAR 
// Adds the sidebar div from HTML to the map as sidebar
const sidebarLeft = L.control.sidebar('sidebar',{
  closeButton: true,
  position: 'left'
}).addTo(map);

const sidebar = document.getElementById('sidebar')
const baseLayers = document.getElementById('baseLayerList')

// LayerControl is moved to sidebar
const layerSwitcher = L.control.layers(baseMaps).addTo(map);
const layerControls = document.querySelectorAll('#map > div.leaflet-control-container > div.leaflet-top.leaflet-right > div.leaflet-control-layers.leaflet-control > section > div.leaflet-control-layers-base > label')

// reverse order to prepend baselayers before project region
for (let i = layerControls.length - 1; i >= 0; i--) {
  let li = document.createElement('li')
  li.classList.add('list-group-item')
  li.appendChild(layerControls[i])
  baseLayers.prepend(li)
}

// hiding the default layer switcher icon
document.querySelector('#map > div.leaflet-control-container > div.leaflet-top.leaflet-right > div.leaflet-control-layers.leaflet-control').hidden = true

// const projectRegionSwitch = document.getElementById('projectRegionSwitch')
const pilotCheckbox = document.getElementById('projectRegionSwitch');
// pilotCheckbox.stopPropagation()
pilotCheckbox.addEventListener('change', function (){
  if (pilotCheckbox.checked) {
    pilotGeojson.addTo(map)
  } else {
    pilotGeojson.remove()
  }
});

  
// User stuff
var userFields = [];
let projectIndex = 0
const userLayerList = document.getElementById("sidebarLayerList")


map.on(L.Draw.Event.CREATED, function (event) {
  // console.log('event drawcreated' + JSON.stringify(event.layer))
  event.layer.addTo(drawnItems)
  let layer = event.layer;
  let type = event.layerType;
  let shape = layer.toGeoJSON()
  // userProject.userFieldShape = shape
  let shape_for_db = JSON.stringify(shape)

  
  projectIndex = userFields.length - 1
  shape.id = projectIndex
  layer.id = projectIndex
  
  const currentUserField = new UserField(
    fieldName = userFieldNameInput(), 
    layer, 
    shape)
  currentUserField.id = projectIndex
  userFields.push(currentUserField)
  
  addLayerToSidebar(currentUserField)
  const switchId = `fieldSwitch-${projectIndex}`
  const inputSwitch = document.getElementById(switchId)
  
  inputSwitch.addEventListener('change', e => {
      inputSwitch.addEventListener('change', function (){
      if (inputSwitch.checked) {
        currentUserField.geom.addTo(map)
      } else {
        currentUserField.geom.remove()
      }
    });
  })
  // inputSwitch.checked = true
  currentUserField.geom.addTo(map)
  inputSwitch.dispatchEvent(new Event('change'));
  
});
// todo check if fieldname already exists, else add number
function userFieldNameInput() {
  let fieldName = prompt("Bitte geben Sie einen Namen für das Feld an", "Acker Bezeichnung").trim();
  if (fieldName !== '') { 
      if (userFields.some(proj => proj.name === fieldName)) {
        alert(`please change name since ${fieldName} it already exists`);
        fieldName = userFieldNameInput()
      } 
    } else {
      alert(`This field can not be empty. Please enter a name!`);
        fieldName = userFieldNameInput()
    }
    return fieldName;
}

class UserField {
  constructor(name, geom, shape) {
    // this.user = user
    this.name = name
    this.geom = geom
    this.shape = shape
    this.user = 0 // TODO add user
    this.id = null
    this.projects = []
  }
}

class UserProject {
  constructor(userField, cropID) {
    this.userField = userField
    this.cropID = cropID
    this.calculation = {};
    this.timestamp = Date.now()
  }
}

userLayerList.addEventListener('click', e => {
  //console.log(e.target)
  const listElement = e.target.closest('li')

  if(e.target.classList.contains('delete')) {
    let confirmDelete = confirm('Are you sure to delete')
    if (confirmDelete) {   
      userFields = userFields.filter(uf => uf !== listElement.userField)
      listElement.userField.geom.remove() // removes shape from map
      listElement.remove() // removes HTML element from sidebar

    }
  } else if(e.target.classList.contains('field-menu')) {
    console.log('field-menu clicked')
  } else if(e.target.classList.contains('field-edit')) {
    console.log('field-edit clicked')}
})

const addLayerToSidebar = (userField) =>  {
  const accordion = document.createElement('li');
  accordion.setAttribute('class', 'list-group-item')
  // accordion.focus()
  accordion.innerHTML = `  
  <div class="accordion-item">
    <div class="accordion-header" id="accordionHeader-${projectIndex}">
      <h6>
        <div class="form-check form-switch">
          <input type="checkbox" class="form-check-input" id="fieldSwitch-${projectIndex}" checked>
          <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseField-${projectIndex}" aria-expanded="true" aria-controls="collapseField-${projectIndex}">
          ${userField.name}</button>
      </h6>
    </div>
    <div id="collapseField-${projectIndex}" class="accordion-collapse collapse show" aria-labelledby="accordionHeader-${projectIndex}">
      <!-- Temporary Insert -->
    <form>
      <input type="select">Feldfrucht</input></br>
      Meteoroligischer Dürreindex 0,6</br>
      landwirtschaftlicher Dürreindex 0,57</br>
      Bodenfeuchtigkeit 15% Vol.</br>
    
    
    </form>

      
    
      <!-- Temporary Insert -->
    
    <span><button type="button" class="btn btn-outline-secondary btn-sm">
            <i class="fa-regular fa-pen-to-square field-edit"></i>
        </button></span>
          <span><button type="button" class="btn btn-outline-secondary btn-sm" data-bs-toggle="modal" data-bs-target="#projectModal">
            <i class="fa-solid fa-ellipsis-vertical field-menu"></i>
            </button></span>
            <span><button type="button" class="btn btn-outline-secondary btn-sm">
            <i class="fa-regular fa-trash-can delete"></i>
          </button></span>
    </div>
    <button id="userFieldNewCalcBtn-${projectIndex}" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#projectModal">Neue Berechnung</button>
  </div> 
  `
  accordion.userField = userField
  console.log('Accordion UserField:')
  console.log(accordion.userField)

  userLayerList.appendChild(accordion)  
}


// Monica-Modal 


$(document).ready(function () {

  $('#projectModal').on('show.bs.modal', function () {

    var projectModal = $('.modal')

    $('.modal-container').html(this)
    $('#map-container').hide()
  }),
  $('#projectModal').on('hide.bs.modal', function () {
    $('#map-container').show()
  })
})
// console.log(myModal.innerHTML)

// $(document).ready(function () {
//   $('#myModal').on('show.bs.modal', function () {
//       var mod = $('.modal'); 
//       $('.insidemodal').html(mod);
//   });
// });