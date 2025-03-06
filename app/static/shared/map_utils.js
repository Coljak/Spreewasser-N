import { getGeolocation } from '/static/shared/utils.js';

const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib =
  '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
export const osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib });

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

export const projectRegion = new L.geoJSON(project_region, {
    attribution: 'Project Region',
    onEachFeature: function (feature, layer) {
      layer.bindTooltip(feature.properties.name);
  }
});

// basemaps
export const baseMaps = {
    "Open Street Maps": osm,
    Satellit: satellite,
    Topomap: topo,
  };

  //Map with open street map,opentopo-map and arcgis satellite map
const map = new L.Map("map", {
    zoomSnap: 0.25,
    wheelPxPerZoomLevel: 500,
    inertia: true,
    tapHold: true,
  }).addLayer(osm);


export function openUserFieldNameModal(layer, featureGroup) {
  // Set the modal content (e.g., name input)
  const modal = document.querySelector('#userFieldNameModal');

  const bootstrapModal = new bootstrap.Modal(modal);
  bootstrapModal.show();

  // Add event listeners for the save and dismiss actions
  modal.querySelector('#btnUserFieldSave').onclick = () => handleSaveUserField(layer, bootstrapModal, featureGroup);
  modal.querySelector('#btnUserFieldDismiss').onclick = () => dismissPolygon(layer, bootstrapModal, featureGroup);
  modal.querySelector('#btnUserFieldDismissTop').onclick = () => dismissPolygon(layer, bootstrapModa, featureGroup);
}

export function initializeDrawControl(map, featureGroup) {
  const drawControl = new L.Control.Draw({
    position: "topright",
    edit: {
      featureGroup: featureGroup,
    },
    draw: {
      circlemarker: false,
      polyline: false,
      polygon: {
        shapeOptions: {
          color: "#000000",
        },
        allowIntersection: false,
        showArea: true,
      },
    },
  });
  map.addControl(drawControl);
};

export function initializeMapEventlisteners (map, featureGroup) {
    const chrosshair = document.getElementsByClassName("leaflet-control-home")[0];
    chrosshair.addEventListener("click", () => {
    try {
        var bounds = featureGroup.getBounds();
        map.fitBounds(bounds);
    } catch {
        return;
    }
    });

    const locationPin = document.getElementsByClassName("leaflet-control-geolocation")[0];
    locationPin.addEventListener("click", () => {
      getGeolocation()
        .then((position) => {
          map.setView([position.latitude, position.longitude], 12);
        })
        .catch((error) => {
          console.error(error.message);
          handleAlerts({ success: false, message: error.message });
        });
    });


    map.on("draw:created", function (event) {
      let layer = event.layer;
      // is added to the map only for display
      featureGroup.addLayer(layer);
    
      openUserFieldNameModal(layer, featureGroup);
    });
};

  //add map scale
const mapScale = new L.control.scale({
    position: "bottomright",
  }).addTo(map);
  

export { map };