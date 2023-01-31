console.log('user_dashboard.js is loaded!')

const osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const osm = L.tileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib})

const satelliteUrl = 'http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
const satelliteAttrib = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
const satellite = L.tileLayer(satelliteUrl, {maxZoom: 18, attribution: satelliteAttrib})

const topoUrl = 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png'
const topoAttrib = 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
const topo = L.tileLayer(topoUrl, {maxZoom: 18, attribution: topoAttrib})

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

var drawControl = new L.Control.Draw({
  position: 'topright',
  draw: {
        circlemarker: false,
        polyline: false,
        polygon: {
          allowIntersection: false,
          showArea: true
      }
    }
});

map.addControl(drawControl)


// Leaflet Control bottom-right
// Leaflet Control top-left
const sidebarLeft = L.control.sidebar('sidebar',{
  closeButton: true,
  position: 'left'
}).addTo(map);

const sidebar = document.getElementById('sidebar')
const baseLayers = document.getElementById('baseLayerList')

//add map scale
const mapScale = new L.control.scale({
  position: 'bottomright'
}).addTo(map);


const layerSwitcher = L.control.layers(baseMaps).addTo(map);
const layerSwitcherObject = layerSwitcher.getContainer();
const htmlParent = document.querySelector('#map > div.leaflet-control-container > div.leaflet-top.leaflet-right > div.leaflet-control-layers.leaflet-control > section > div.leaflet-control-layers-base')
baseLayers.append(htmlParent)
const layerControls = document.querySelectorAll('#baseLayerList > div')

const htmlChildren = document.querySelectorAll('#baseLayerList > div > label')
console.log(htmlChildren.length)
console.log(htmlChildren)

// reverse order to prepend baselayers before project region
for (let i = htmlChildren.length - 1; i >= 0; i--) {
  console.log(htmlChildren[i])
  let li = document.createElement('li')
  li.classList.add('list-group-item')
  li.appendChild(htmlChildren[i])
  baseLayers.prepend(li)
}

const pilotGeojson = L.geoJSON(pilotRegion).addTo(map);

// SIDEBAR 
// const projectRegionSwitch = document.getElementById('projectRegionSwitch')
var pilotCheckbox = document.getElementById('projectRegionSwitch');
pilotCheckbox.addEventListener('change', function (){
  if (pilotCheckbox.checked) {
    pilotGeojson.addTo(map)
    console.log('Checked');
  } else {
    pilotGeojson.remove()
    console.log('Not checked');
  }
});

  
// User stuff
const userProjects = [];
let projectIndex = 0
const userLayerList = document.getElementById("userLayerList")


map.on(L.Draw.Event.CREATED, function (event) {
  // console.log('event drawcreated' + JSON.stringify(event.layer))
  let layer = event.layer;
  let type = event.layerType;
  let shape = layer.toGeoJSON()
  console.log('shape')
  console.log(shape)
  // userProject.userFieldShape = shape
  let shape_for_db = JSON.stringify(shape)

  let fieldName = shapeNameInput()
  projectIndex = userProjects.length
  shape.id = projectIndex
  layer.id = projectIndex
  const currentProject = new Project(fieldName, layer, shape)
  currentProject.id = projectIndex
  userProjects.push(currentProject)
  
  addLayerToSidebar(currentProject)
  const switchId = `fieldSwitch_${projectIndex}`
  const inputSwitch = document.getElementById(switchId)
  // switchId.checked = false
  
  inputSwitch.addEventListener('change', e => {
      console.log("event has been fired")
      console.log(currentProject.geom.id)
      inputSwitch.addEventListener('change', function (){
        
      if (inputSwitch.checked) {
        currentProject.geom.addTo(map)
      } else {
        currentProject.geom.remove()
      }
    });
  })
  // inputSwitch.checked = true
  currentProject.geom.addTo(map)
  inputSwitch.dispatchEvent(new Event('change'));
  
});
// todo check if fieldname already exists, else add number
function shapeNameInput() {
  let fieldName = prompt("Bitte geben Sie einen Namen für das Feld an", "Acker Bezeichnung");
  if (fieldName != null) { 
  }
  return fieldName;
}

class Project {
  constructor(name, geom, shape) {
    // this.user = user
    this.name = name
    this.geom = geom
    this.shape = shape
    this.id = null
  }
}

// add li to ul
const addLayerToSidebar = (project) =>  {
  console.log('Project')
  console.log(project)
  const li = document.createElement('li');
  li.setAttribute('class', 'list-group-item')
  li.innerHTML = `
  <div class="custom-control custom-switch">
    <input type="checkbox" class="custom-control-input" id="fieldSwitch_${projectIndex}" checked>
    <label class="custom-control-label" for="fieldSwitch_${projectIndex}">${project.name}</label>
  </div>
  `
  userLayerList.appendChild(li)  
}
// hiding the default layer switcher icon
document.querySelector('#map > div.leaflet-control-container > div.leaflet-top.leaflet-right > div.leaflet-control-layers.leaflet-control').hidden = true
