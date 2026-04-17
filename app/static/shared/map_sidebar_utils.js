import { getGeolocation, bsPrimary, bsSecondary } from '/static/shared/utils.js';
import { MonicaProject } from '/static/monica/monica_model.js';
import { ToolboxProject } from '/static/toolbox/toolbox_project.js';
import { getCSRFToken, handleAlerts, getBsColor } from '/static/shared/utils.js';






// this base for some reason renders tiles with an offset
const wmtsBase = 'https://sgx.geodatenzentrum.de/wmts_basemapde_schummerung/tile/1.0.0/de_basemapde_web_raster_combshade/default/DE_EPSG_3857_ADV/{TileMatrix}/{TileRow}/{TileCol}.png';

// TileMatrix offset for DE_EPSG_3857_ADV (TileMatrix N -> leafetz = N + offset)
const TILEMATRIX_OFFSET = 5; 

    // Custom tile layer that maps Leaflet z,x,y -> WMTS TileMatrix, TileRow, TileCol
const wmtsLayer = L.TileLayer.extend({
  getTileUrl: function(coords) {
    const zLeaf = coords.z;     // Leaflet zoom
    const x = coords.x;
    const y = coords.y;

    // Convert Leaflet zoom to WMTS TileMatrix
    const tm = zLeaf - TILEMATRIX_OFFSET;

    // If the tilematrix is outside WMTS range, return a transparent PNG (or a blank)
    if (tm < 0 || tm > 13) {
      // 1x1 transparent PNG data URI
      return 'data:image/gif;base64,R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==';
    }

    // format TileMatrix as two digits (capabilities show 00, 01, 02, ...)
    const tmStr = String(tm).padStart(2, '0');

    // For DE_EPSG_3857_ADV the TileMatrix width = 2^(tm + 5) which equals 2^zLeaf,
    // so TileCol = x and TileRow = y (Leaflet and WMTS align when using the correct TileMatrix).
    const tileCol = x;
    const tileRow = y;

    // Replace placeholders in template
    return wmtsBase
      .replace('{TileMatrix}', tmStr)
      .replace('{TileRow}', tileRow)
      .replace('{TileCol}', tileCol);
  }
});

// Instantiate and add the layer
export const demOverlay = new wmtsLayer('', {
  attribution: 'Kartengrundlage: basemap.de / BKG — dl-de/by-2-0',
  minZoom: 0,
  maxZoom: 18, // Leaflet zoom; WMTS available TileMatrix 00..13 => LeafletZoom 5..18
  tileSize: 256,
  pane: 'overlayPolygonPane'
})




export class UserField {
  constructor(name, id=null, lat=null, lon=null, userProjects=[], properties={} ) {
    this.name = name;
    // this.layer = layer;
    this.id = id;
    this.lat = lat;
    this.lon = lon;
    this.userProjects = userProjects;
    this.properties = properties;
  }
};


const wmsUrl = "/toolbox/proxy/wms/"

const osmUrl = "http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors';
const osm = L.tileLayer(osmUrl, { 
  referrerPolicy: "strict-origin-when-cross-origin",
  maxZoom: 18, 
  attribution: osmAttrib, 
  pane: "baselayerPane" 
});

const satelliteUrl =
  "http://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
const satelliteAttrib =
  "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community";
const satellite = L.tileLayer(satelliteUrl, {
  maxZoom: 18,
  attribution: satelliteAttrib,
  pane: "baselayerPane"
});



const greyMapUrl = 'https://sgx.geodatenzentrum.de/wmts_topplus_open/tile/1.0.0/web_grau/default/WEBMERCATOR/{z}/{y}/{x}.png'
const greyMap = L.tileLayer(greyMapUrl, {
    attribution: '© BKG 2025 — Daten: TopPlusOpen <a href="https://www.govdata.de/dl-de/by-2-0">dl-de/by-2-0</a> ',
    maxZoom: 18,
    pane: "baselayerPane",
})
// https://sgx.geodatenzentrum.de/wmts_topplus_open/legend/web_scale.png  legende

export const projectRegion = new L.geoJSON(project_region, {
  attribution: 'Spreewasser:N Projektregion',
  pane: "overlayPolygonPane",
  style: {
    color: 'var(--bs-primary)', 
    weight: 3,                   
    fill: false,                  
    fillOpacity: 0,               
    interactive: true             
  },
  onEachFeature: function (feature, layer) {
    layer.bindTooltip(feature.properties.name, {
    direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
    offset: [0, 0],         // x, y offset in pixels
    permanent: false,       // only show on hover
    sticky: true  
    });
  }
});


// basemaps
export const baseMaps = {
    "Open Street Maps": osm,
    "Satelit": satellite,
    // Topomap: basemap,
    "Topografische Karte": greyMap,
  };

export function enhanceMap (map) {
  map.createPane("baselayerPane");
  map.getPane("baselayerPane").style.zIndex = 200;

  map.createPane("overlayRasterPane");
  map.getPane("overlayRasterPane").style.zIndex = 300;
  
  map.createPane("backgroundPane");
  map.getPane("backgroundPane").style.zIndex = 350;

  map.createPane("overlayPolygonPane");
  map.getPane("overlayPolygonPane").style.zIndex = 500;

  map.createPane("polygonPane");
  map.getPane("polygonPane").style.zIndex = 580;

  map.createPane("pinPane");
  map.getPane("pinPane").style.zIndex = 590;

  map.createPane("resultPane");
  map.getPane("resultPane").style.zIndex = 630;
  
  $(".leaflet-control-zoom").append(
    '<a class="leaflet-control-home" href="#" role="button" title="Project area" aria-label="Project area"><i class="bi bi-bullseye"></i></a>',
    '<a class="leaflet-control-geolocation" href="#" role="button" title="My location" aria-label="User location"><i class="bi bi-geo"></i></a>'
  );

  const baseMapSwitches = L.control.layers(baseMaps, null, { 
    collapsed: true,
    position: "topleft"
   }).addTo(map);

  const mapScale = new L.control.scale({
    position: "bottomright",
  }).addTo(map);

  window.addEventListener('resize', () => {
    map.invalidateSize();
  });
  return map;
  };

  //Map with open street map,opentopo-map and arcgis satellite map
  // TODO change var back to const!!
export var map = enhanceMap(
  new L.Map("map", {
    zoomSnap: 0.25,
    wheelPxPerZoomLevel: 250,
    maxZoom: 18,
    minZoom: 3,
    inertia: true,
    tapHold: true,
  }).addLayer(osm)
);

document.dispatchEvent(new CustomEvent('leaflet-map-ready', { detail: map }));
window.DEBUG_MAP = map;
export function getCircleMarkerSettings (fillColor) {
  return {
    radius: 5,
    type: 'circle',
    weight: 2,
    fillOpacity: 1,
    color: 'black',
    fillColor: fillColor
  };
};

export function getLegendItem (label, markerSettings) {
  return {
    label: label,
    ...markerSettings
  };
};

export function getLegendSettings (title, legendItems) {
  return {
    position: 'bottomright',
    collapsed: false,
    title: title,
    legends: legendItems
  };
};

export function removeLegendFromMap(map) {      
  const existingLegend = document.querySelector('.leaflet-legend');
      if (existingLegend) {
        map.removeControl(existingLegend);
      }
};

export function openUserFieldNameModal(layer, featureGroup) {
  // Set the modal content (e.g., name input)
  const modalEl = document.querySelector('#userFieldNameModal');

  const bootstrapModal = new bootstrap.Modal(modalEl);
  bootstrapModal.show();

  $(modalEl).on('shown.bs.modal', function () {
      $('#fieldNameInput').focus();
      
  });

  // Add event listeners for the save and dismiss actions
  modalEl.querySelector('#btnUserFieldSave').onclick = () => handleSaveUserField(layer, bootstrapModal, featureGroup);
  modalEl.querySelector('#btnUserFieldDismiss').onclick = () => dismissPolygon(layer, bootstrapModal, featureGroup);
  modalEl.querySelector('#btnUserFieldDismissTop').onclick = () => dismissPolygon(layer, bootstrapModal, featureGroup);

   // Reset alert box text when the modal is hidden
  modalEl.addEventListener('hidden.bs.modal', () => {
    $('#alert-box-name').addClass('d-none');
    $('#alert-box-name').text = '0;'
    $('#fieldNameInput').val('') 
  })
};




export function initializeDrawControl(map, featureGroup) {

  
  map.on('click', function () {
    // TODO click point conversion for data retrieval
      const z = map.getZoom();
      const center = map.getCenter();
      // compute center tile coords (approx)
      const worldSize = 256 * Math.pow(2, z);
      const projection = map.options.crs.project(center); // Point in meters for EPSG3857
      // convert projection point to tile coords:
      const resolution = (2 * 20037508.342789244) / worldSize; // meter per pixel
      const tx = Math.floor((projection.x + 20037508.342789244) / (256 * resolution));
      const ty = Math.floor((20037508.342789244 - projection.y) / (256 * resolution));
      console.log('Leaflet zoom', z, 'tile x/y', tx, ty, 'WMTS TileMatrix', (z - TILEMATRIX_OFFSET));
      // const url = basemap.getTileUrl({x: tx, y: ty, z: z});
      // console.log('Example tile URL for center:', url);
    });


  // const drawControl = new L.Control.Draw({
  //   position: "topright",
  //   edit: {
  //     featureGroup: featureGroup,
  //     edit: false,
  //     remove: false,
  //   },
  //   draw: {
  //     circlemarker: false,
  //     polyline: false,
  //     circle: false,
  //     marker: false,
  //     polygon: {
  //       allowIntersection: false,
  //       showArea: true,
  //       metric: true,
  //       shapeOptions: {
  //         color: bsPrimary,
  //         fill: false,
  //       }
  //     },
      
  //   },
  // });
  // map.addControl(drawControl);
};

const polygonDrawer = new L.Draw.Polygon(map, {
  allowIntersection: false,
  showArea: true,
  drawError: {
    color: '#e1e100',
    message: '<strong>Error:</strong> invalid shape'
  },
  shapeOptions: {
    color: bsPrimary,
    fill: false,
  }
});


export function initializeMapEventlisteners (map, featureGroup, projectClass) {
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

    let vertexCount = 0;

    map.on("draw:created", function (event) {
      console.log('draw  created')
      $('#draw-hint').addClass('d-none');
      let layer = event.layer;
      // is added to the map only for display
      featureGroup.addLayer(layer);
    
      openUserFieldNameModal(layer, featureGroup);
    });

    map.on("draw:drawstart", function(event) {
      // hide the default actions list on toolbar
      const container = document.querySelector('.leaflet-draw-actions');

      $('#draw-hint').removeClass('d-none');
      $('#draw-hint').text('Klicken Sie in die Karte, um ein Polygon zu zeichnen.')
      if (container) container.style.display = 'none';
      vertexCount = 0;
      console.log('draw start',vertexCount)
    });

    map.on("draw:drawstop", function(event) {
     console.log('draw:stop')
      $('#endPolygonDraw').addClass('d-none');
      $('#draw-hint').addClass('d-none');
    });

    map.on("draw:drawvertex", function(event) {
      vertexCount +=1;
      if (vertexCount < 3) {
        $('#draw-hint').text('Klicken Sie in die Karte, um weitere Ecken des Polygons zu zeichnen.')
      } else {
        $('#draw-hint').text('Zeichnen Sie weitere Punkte oder klicken Sie auf den ersten Punkt, um das Polygon zu schließen.')
      }
      console.log('draw drawvertex', vertexCount)
    });
    

  

    featureGroup.on("click", function (event) {
      let leafletId = event.layer._leaflet_id;
  
      let userFieldId = getUserFieldIdByLeafletId(leafletId);
      let projectClass = MonicaProject
      if (window.location.pathname.endsWith('/toolbox/')) {
        projectClass = ToolboxProject
      }
      let project = projectClass.loadFromLocalStorage();
      selectUserField(userFieldId, project, featureGroup);
    });
};


// Overlays
function handleOverlaySwitch(switchInput, overlayLayers, map) {
  const overlayId = switchInput.getAttribute("data-layer");
  const overlay = overlayLayers[overlayId];
  const opacitySlider = document.getElementById(`${overlayId}Opacity`);

  if (switchInput.checked) {
  overlay.addTo(map);
  if (opacitySlider) {
      opacitySlider.disabled = false;
  };
  overlay.bringToBack(); 
  } else {
  overlay.remove();
  if (opacitySlider) {
      opacitySlider.disabled = true;
    };
  };
};

export function createNUTSSelectors({getFeatureGroup}) {
  // Create a LayerGroup to hold the displayed polygons
  const stateCountyDistrictLayer = new L.FeatureGroup({pane: "polygonPane",}).addTo(map);
  stateCountyDistrictLayer.on("click", function (event) {
    console.log("stateCountyDistrictLayer click event: ", event);
  
    // Get the clicked layer
    let clickedLayer = event.layer;
    
    // Confirm action with the user
    if (confirm("Als Suchgebiet nutzen?")) {
      openUserFieldNameModal(clickedLayer, getFeatureGroup()) 
    }
  });
  
  
  stateCountyDistrictLayer.on("click", function (event) {
    console.log("stateCountyDistrictLayer click event: ", event);
  });
  
  // Handle dropdown menu change event
  // Multiple Select from https://www.cssscript.com/select-box-virtual-scroll/
  VirtualSelect.init({ 
    ele: '#statesSelect',
    placeholder: 'Bundesland',
    required: false,
    disableSelectAll: true,
    additionalClasses: 'bootstrap-vs', 
    additionalDropboxContainerClasses: 'bootstrap-vs',
    additionalDropboxClasses: 'bootstrap-vs',
    additionalToggleButtonClasses: 'bootstrap-vs',
  });
  VirtualSelect.init({ 
    ele: '#districtsSelect',
    placeholder: 'Regierungsbezirk',
    required: false,
    disableSelectAll: true,
    additionalClasses: 'bootstrap-vs', 
    additionalDropboxContainerClasses: 'bootstrap-vs',
    additionalDropboxClasses: 'bootstrap-vs',
    additionalToggleButtonClasses: 'bootstrap-vs',
  });
  VirtualSelect.init({ 
    ele: '#countiesSelect',
    placeholder: 'Landkreis',
    required: false,
    disableSelectAll: true,
    additionalClasses: 'bootstrap-vs', 
    additionalDropboxContainerClasses: 'bootstrap-vs',
    additionalDropboxClasses: 'bootstrap-vs',
    additionalToggleButtonClasses: 'bootstrap-vs',
  });
  
  var administrativeAreaDiv = document.querySelectorAll('div.administrative-area');
  var selectedAdminAreas = {
    states: [],
    counties: [],
    districts: [],
  };
  
  
  administrativeAreaDiv.forEach(function (areaDropdown) {
    areaDropdown.addEventListener('change', function (event) {
      stateCountyDistrictLayer.clearLayers();
      var name = areaDropdown.getAttribute("name");
      var selectedOptions = areaDropdown.value;
      selectedAdminAreas[name] = selectedOptions;
  
      for (let key in selectedAdminAreas) {
        if (selectedAdminAreas[key].length > 0) {
          selectedAdminAreas[key].forEach(function (polygon) {
            var url = '/drought/load_nuts_polygon/' + key + '/' + polygon + '/';
          console.log("URL", url)
          var color = '';
          if (key == 'states') {
              color = 'purple';
          } else if (key == 'counties') {
              color = 'blue';
          } else if (key == 'districts') {
              color = 'green';
          }
          var geojsonLayer = new L.GeoJSON.AJAX(url, {
            style: {
                color: color,
                fill: false,
                weight: 3,
                fillOpacity: 0,
                interactive: true,
            },
            onEachFeature: function (feature, layer) {
                layer.bindTooltip(`${feature.properties.nuts_name}`, {
                direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
                offset: [0, 0],         // x, y offset in pixels
                permanent: false,       // only show on hover
                sticky: true  
                });
                layer.setStyle({
                  fill: false, 
                });
            }
          });
          console.log("geojsonLayer", geojsonLayer)
          geojsonLayer.addTo(stateCountyDistrictLayer);
          });
        }
      }
    }); 
  });
};
  

export function getUserFields() {
  let userFields = localStorage.getItem("userFields");
  return userFields ? JSON.parse(userFields) : {};
};

export function getLeafletIdByUserFieldId(id) {
  let userFields = getUserFields();
  const entry = Object.values(userFields).find(field => field.id == id);
  return entry ? entry.leafletId : null;
};

export function getUserFieldIdByLeafletId(leafletId) {
  let userFields = getUserFields();
  const entry = Object.values(userFields).find(field => field.leafletId == leafletId);
  console.log("getUserFieldIdByLeafletId", leafletId, entry, userFields);
  return entry ? entry.id : null;
};


export function highlightLayer(leafletId, featureGroup) {
  console.log("HIGHLIGHT", leafletId);

  // remove highlight class from all layers
  featureGroup.eachLayer(function (layer) {
    if (layer.getElement) {
      const el = layer.getElement();
      if (el) el.classList.remove("highlight");
    }
  });

  // remove highlight from all sidebar headers
  const listElements = document.querySelectorAll(".user-field-header");
  listElements.forEach(header => header.classList.remove("highlight"));

  // toggle highlight on selected layer + header
  const header = $(`#accordion-${leafletId}`);
  const layer = featureGroup.getLayer(leafletId);
  

  if (header.hasClass("highlight")) {
    header.removeClass("highlight");
    if (layer?.getElement) {
      const el = layer.getElement();
      if (el) {
        el.classList.remove("highlight");
        layer.editing.disable();
      }
    }
  } else {
    header.addClass("highlight");
    if (layer?.getElement) {
      const el = layer.getElement();
      if (el) {
        el.classList.add("highlight");
      }
    }
  }
};


export function selectUserField(userFieldId, project, featureGroup) {
    console.log("selectUserField featureGroup", project);

    const leafletId = getLeafletIdByUserFieldId(userFieldId);
    const userField = getUserFields()[leafletId];
    highlightLayer(leafletId, featureGroup);

    const needsConfirmation = (
        project && project.id &&
        (
            (project.userField && project.userField !== userFieldId) ||
            (!project.userField || project.userField === '')
        ) 
    ) || (project.toolboxType && project.toolboxType !== 'generic' && project.userField && project.userField !== userFieldId);
    console.log('needsConfirmation', needsConfirmation, userFieldId, userField);

    if (needsConfirmation) {
        const isChangingExisting = !!project.userField;

        if (project.toolboxType) {
          showUserFieldModal({
            title: "Auswahl des Suchbereichs",
            text: isChangingExisting
                ? "Wollen Sie den Suchbereich wechseln?"
                : "Falls ein Projekt geöffnet ist, wird es ohne zu speichern geschlossen.",
            onConfirm: () => {
                commitSwitchUserField(project, userFieldId, userField, featureGroup);
            }
        });
        } else {
          showUserFieldModal({
            title: "User Field Selection",
            text: isChangingExisting
                ? "You are changing a Monica Project's user field."
                : "You are changing a Monica Project without UserField to a SWN Project with UserField. The location of the project will be changed to the UserField location.",
            onConfirm: () => {
                commitSwitchUserField(project, userFieldId, userField, featureGroup);
            }
        });
      }
    } else  {
        commitSwitchUserField(project, userFieldId, userField, featureGroup);
    }
};

export function getSelectedUserField() {
  if ($('.user-field-header.highlight')[0]) {
    const userFieldId = $('.user-field-header.highlight').first().attr('user-field-id');
    return userFieldId;
  } else { return null; }
}

function showUserFieldModal({ title, text, onConfirm }) {
    const modal = document.getElementById('interactionModal');
    const modalInstance = new bootstrap.Modal(modal);

    document.getElementById('interactionModalTitle').innerHTML = title;
    document.getElementById('interactionModalText').innerHTML = text;

    $('#interactionModalOK')
        .off('click')
        .on('click', () => {
            modalInstance.hide();
            onConfirm();
        });

    modalInstance.show();
}

function commitSwitchUserField(project, userFieldId, userField, featureGroup) {
  console.log('commitSwitchUserField', userFieldId, userField);
  project['userField'] = userFieldId;
  try {
    project['latitude'] = userField.lat;
    project['longitude'] = userField.lon;
  } catch {;};
  
  project.saveToLocalStorage();
  highlightLayer(getLeafletIdByUserFieldId(userFieldId), featureGroup);
}



function revertEdit(layer) {
  if (layer._originalLatLngs) {
    const original = L.LatLngUtil.cloneLatLngs(layer._originalLatLngs);

    // Step 1: Reset shape and visuals
    layer.setLatLngs(original);
    layer.redraw();

    // Step 2: Disable editing
    if (layer.editing && layer.editing._enabled) {
      layer.editing.disable();
    }

    // Step 3: Clean up vertices handlers safely
    if (layer.editing && Array.isArray(layer.editing._verticesHandlers)) {
      layer.editing._verticesHandlers.forEach(handler => {
        if (handler._markerGroup && handler._markerGroup.clearLayers) {
          handler._markerGroup.clearLayers();
        }
      });
      layer.editing._verticesHandlers = [];
    }

    // Step 4: Reset the editing plugin completely
    layer.editing = new L.Edit.Poly(layer);

    // Step 5: Clean up the original backup
    delete layer._originalLatLngs;

    console.log("Edits truly reverted (safe).");
  }
}

// TODO: move this to three_split.js
$('#toggleBottomFullscreen').on('click', function () {
    const isFullscreen = $(this).find('i').hasClass('bi-fullscreen-exit');

    if (isFullscreen) {
      // Exit fullscreen - restore layout
      // $('.panel-top').css('height', '20%');
      // $('.panel-left').css('visibility', 'visible');
      $('#main-navbar').show();
      // $('.leaflet-control-container').show(); 
      $('#toggleBottomFullscreen').html('<i class="bi bi-arrows-fullscreen"></i>');

      setTimeout(() => map.invalidateSize(), 0);
      setTimeout(() => map.invalidateSize(), 120);
   

    } else {
      // Enter fullscreen mode - shrink top, hide left
      // $('.panel-top').css('height', '50%'); // or even '5%' if you want it smaller
      // $('.panel-left').css('visibility', 'hidden');
            // hide the sidebar
      $('#main-navbar').hide(); // hide the navbar
      // $('.leaflet-control-container').hide(); // hide Leaflet controls


      setTimeout(() => map.invalidateSize(), 0);
      setTimeout(() => map.invalidateSize(), 120);
      const highlightedElement = $('#userFieldsAccordion').find('li.highlight')
      if (highlightedElement.length > 0) {
        console.log(highlightedElement)
        
        map.fitBounds(highlightedElement[0].layer.getBounds());
      }
        $('#toggleBottomFullscreen').html('<i class="bi bi-fullscreen-exit"></i>');
      }
    });




// TODO rename to MapEventhandler
export function initializeSidebarEventHandler({ 
  sidebar, 
  map, 
  overlayLayers, 
  getUserFields, 
  getFeatureGroup, 
  getProject,
  loadProjectFromDb,
  // TODO get rid of the project argument- it is already saved to localStorage
  startApplication,
  addProject,
  }) {
    sidebar.addEventListener("change", (event) => {
      const switchInput = event.target;

      if (switchInput.classList.contains("layer-switch")) {
          const layerId = switchInput.getAttribute("data-layer");
          switchInput.checked ? map.addLayer(overlayLayers[layerId]) : map.removeLayer(overlayLayers[layerId]);
      } else if (switchInput.classList.contains("layer-opacity")) {
          const overlayId = switchInput.getAttribute("data-layer");
          overlayLayers[overlayId].setOpacity(switchInput.value);
      } else if (switchInput.classList.contains("overlay-switch")) {
        const overlay = switchInput.getAttribute("data-layer");
          handleOverlaySwitch(switchInput, overlayLayers, map);
      } else if (switchInput.classList.contains("user-field-switch")) {
        console.log('switchInput: ', switchInput);
          toggleUserField(switchInput, getFeatureGroup());
      } else if (switchInput.classList.contains('all-userfields-switch')) {
        event.stopPropagation();
        console.log('all-userfields-switch')
        $('.form-check-input.user-field-switch')
        .prop('checked', switchInput.checked)
        $('.form-check-input.user-field-switch').each((_, s) => {
          toggleUserField(s, getFeatureGroup());
        })
      }
    });

    let clickTimeout;

    sidebar.addEventListener("dblclick", (event) => {
      clearTimeout(clickTimeout); // prevent single click logic
      
      const listElement = event.target.closest("li");
      map.fitBounds(listElement.layer.getBounds());
      console.log("DOUBLE CLICK");
      
    });

    sidebar.addEventListener("click", (event) => {
      console.log("sidebar click event", event.target.classList);
      const clickedElement = event.target;
      let featureGroup = getFeatureGroup()
      // if (event.target.closest(.))
      if (event.target.closest('.all-userfields-switch')) {
        return
      } else if (event.target.closest('.accordion-button.user-field-accordion-header')) {
        console.log('closest userfield-switch')
        $('#userFieldsAccordion').toggleClass('show') 
      } else if (event.target.id === 'addUserFieldPolygon'){
        console.log('addUserFieldPolygon')
        polygonDrawer.enable();
        $('#endPolygonDraw').removeClass('d-none');
      } else if (event.target.id === 'endPolygonDraw') {
        polygonDrawer.disable();
      }
  
      
      if (clickedElement.classList.contains("user-field-action")) {
        const leafletId = clickedElement.getAttribute("leaflet-id");
        const userFieldId = clickedElement.getAttribute("user-field-id");

        console.log("user-field-action clicked", leafletId);
        let userFields = getUserFields();
        let userField = userFields[leafletId];
        

        if (clickedElement.classList.contains("delete")) {
          let confirmDelete = confirm(`Are you sure to delete ` + userFields[leafletId].name + "?");
          if (confirmDelete) {
            
            let layer = featureGroup.getLayer(leafletId);
            delete userFields[leafletId];
            featureGroup.removeLayer(layer); // removes shape from map

            const listElement = document.getElementById("accordion-"+leafletId);
            listElement.remove(); // removes HTML element from sidebar
            // removes field from dbprojectClass
            console.log("delete UserField ", userFieldId)
            fetch(`delete-user-field/${userFieldId}/`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken(),
              }
            })
            .then(response => response.json())
            .then(data => {
              handleAlerts(data.message);
              console.log("Delete Success");
            })
            .catch(error => {
              console.log(error);
            });
          }
        } else if (clickedElement.classList.contains("field-menu")) {
          selectUserField(userFieldId, getProject(), featureGroup);
          console.log('field-menu clicked');
          fetch(`field-projects-menu/${userFieldId}/`)
          .then(response => response.json())
          .then(data => {
          // TODO the hardcoded # fieldMenuModal is triggered from button
          const modalElement = document.getElementById('fieldMenuModal');
          const modalContent = modalElement.querySelector('.modal-content')

            modalContent.innerHTML = data.html;
            const fieldMenuModal = new bootstrap.Modal(modalElement);
            fieldMenuModal.show();

            modalElement.addEventListener('click', (event) => {
              if(event.target.classList.contains('open-project')) {
                const projectId = event.target.getAttribute('data-project-id');
                loadProjectFromDb(projectId)
                .then(project => startApplication(project))
                fieldMenuModal.hide();
              }
            });
          });
        } else if (clickedElement.classList.contains("field-project-add")) {
          selectUserField(userFieldId, getProject(), featureGroup);
          //set the right user field in the modal
          $('#userFieldSelect').val(userFieldId); 

          addProject(userFieldId);
          
        } else if (clickedElement.classList.contains('field-edit')) {
          selectUserField(userFieldId, getProject(), featureGroup);
          console.log('field-edit clicked');
          let layer = featureGroup.getLayer(leafletId);
        
          if (layer && layer.editing && !layer.editing._enabled) {
            console.log('Edit enabling')
            // Save original latlngs for cancel
            layer._originalLatLngs = L.LatLngUtil.cloneLatLngs(layer.getLatLngs());
            layer.editing.enable();
        
            const popupHtml = `
              <button class="btn btn-sm btn-success" id="btnUpdateUserField">Speichern</button>
              <button class="btn btn-sm btn-danger" id="btnCancelEditUserField">Abbrechen</button>
            `;
        
            // Bind and open the popup
            
        
            // Listen for popupopen ON THE MAP
            function onPopupOpen(e){
              console.log("On Popup opened");
              if (e.popup._source !== layer) return;
        
              const popupEl = e.popup.getElement();
              const saveBtn = popupEl.querySelector('#btnUpdateUserField');
              const cancelBtn = popupEl.querySelector('#btnCancelEditUserField');
              let editConfirmed = false;
        
              // Save button
              L.DomEvent.on(saveBtn, 'click', () => {
                console.log('Save clicked');
                editConfirmed = true;
                saveUserField(userField.name, userFieldId, layer);
                layer.editing.disable();
                layer.closePopup();
                layer.unbindPopup(); // Prevent popup from reopening later
              });
        
              // Cancel button
              L.DomEvent.on(cancelBtn, 'click', () => {
                console.log('Cancel clicked');
                editConfirmed = false;
                revertEdit(layer);
                layer.editing.disable();
                layer.closePopup();
                layer.unbindPopup(); // Also prevent reappearing
              });
        
              // Popup close fallback — only revert if NOT confirmed
              function onPopupClose(e){
                console.log('On Popup close', layer)
                if (e.popup._source === layer && !editConfirmed) {
                  console.log('Popup closed without save – reverting');
                  revertEdit(layer);
                  layer.editing.disable();
                  layer.unbindPopup(); // Cleanup
                  console.log('Popup closed:', layer);
                }
                map.off('popupclose', onPopupClose);
              };
        
              map.on('popupclose', onPopupClose);
              map.off('popupopen', onPopupOpen); // Prevent multiple bindings
            };
        
            map.on('popupopen', onPopupOpen);
            layer.bindPopup(popupHtml).openPopup();
          } else {
            console.log('Edit disabling');
            layer.editing.disable();
            layer.closePopup();
            layer.unbindPopup(); // Prevent popup from reopening later
          }

        }
         else { return;}
        } else if (clickedElement.closest("li") && clickedElement.closest("li").hasAttribute("leaflet-id")) {
          const listEl = clickedElement.closest("li");
        clearTimeout(clickTimeout);
        clickTimeout = setTimeout(() => {
          // clickTimeout = null;
          const leafletId = listEl.getAttribute("leaflet-id");
          console.log("user-field-header clicked", leafletId);
          selectUserField(getUserFieldIdByLeafletId(leafletId), getProject(), featureGroup);
        }, 250); }
      });
};


function toggleUserField(switchInput,  map) {
    const leafletId = switchInput.getAttribute("leaflet-id");
    const listElement = switchInput.closest("li");
    switchInput.checked ? map.addLayer(listElement.layer) : map.removeLayer(listElement.layer)
};

// Save a newly created userField in DB
function saveUserField(name, id, layer) {
  let geomJson = layer.toGeoJSON();
  return new Promise((resolve, reject) => {
    const requestData = {
      geom: JSON.stringify(geomJson.geometry),
      name: name,
      id: id,
    };
    fetch('save-user-field/', {
      method: "POST",
      credentials: "same-origin",
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken(),
      },
      body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('SaveUserField data', data)
      handleAlerts({'success': true, 'message': 'UserField saved successfully'});
      resolve(data); 
    })
    .catch(error => {
      handleAlerts({'success': false, 'message': 'Error saving UserField: ', error});
      reject(error); 
    });
  });
};


function updateFieldSelectorOption(userField, fieldSelector) {  
  const option = document.createElement("option");
  option.value = userField.id;
  option.text = userField.name;
  fieldSelector.add(option);
};



// Modal Userfield Name Input
export function handleSaveUserField(layer, bootstrapModal, featureGroup) {
 

  let userFieldsName;
  let project;
  if (window.location.pathname.endsWith('/drought/')) {
    userFieldsName = 'droughtUserFields';
    project = MonicaProject.loadFromLocalStorage();
  } else if (window.location.pathname.endsWith('toolbox/')) {
    userFieldsName = 'toolboxUserFields';
    project = ToolboxProject.loadFromLocalStorage();
  } else {
    userFieldsName = '';
  }

  const fieldNameInput = document.getElementById("fieldNameInput");
  const fieldName = fieldNameInput.value;
  let userFields = {};
  // TODO move this task to db (check if exists)
  try {
    userFields = JSON.parse(localStorage.getItem('userFields'));
  } catch { ; }

  if (fieldName.split(' ').join('') !== "") {
    if (Object.values(userFields).some((uf) => uf.name === fieldName)) {
      // handleAlerts({'success': false, 'message': `Please change the name since "${fieldName}" already exists.`});
      $('#alert-box-name').text(`${fieldName} existiert bereits.`)
      $('#alert-box-name').removeClass('d-none');
      $('#fieldNameInput').focus();
      setTimeout(() => {
        bootstrapModal.show();
      }
      , 2000);
    } else {
      

      // userField.name = fieldName;
      saveUserField(fieldName, null, layer)
      .then((data) => {
        console.log("Data: ", data);
        var layerGeoJson = addUserFieldToMap(data, featureGroup)
        // var layerGeoJson = L.geoJSON(data.geometry,
        //   {
        //     className: 'user-field',
        //     pane: 'polygonPane',
        //     onEachFeature: function (f, l) {
        //       l.bindTooltip(fieldName, {
        //           direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
        //           offset: [0, 0],         // x, y offset in pixels
        //           permanent: false,       // only show on hover
        //           sticky: true  
        //       });
        //       featureGroup.addLayer(l);
        //     },
        //   }
        // );
        const userField = new UserField(
          data.properties.name,
          data.properties.id,  
          data.properties ? data.properties : {},
        );
        layer.remove(); // removes the drawn shape from map
        const newLayer = Object.values(layerGeoJson._layers)[0];
        // featureGroup.addLayer(newLayer);
        userField.leafletId  = featureGroup.getLayerId(newLayer);
        
        userFields[userField.leafletId] = userField;
        localStorage.setItem('userFields', JSON.stringify(userFields));

        addLayerToSidebar(userField, newLayer);
        // add UserField to dropdown
        $('#userFieldSelect').append(new Option( userField.name, userField.id));

        selectUserField(userField.id, project, featureGroup)

      })

      // fieldNameInput.value = '';
      bootstrapModal.hide();
    }
  } else {

    alert("This field cannot be empty. Please enter a name!");
    // fieldNameInput.value = '';
  }
  
};



export function dismissPolygon(layer, modalInstance, featureGroup) {
  modalInstance.hide();
  // temporary layer is removed from the map
  featureGroup.removeLayer(layer);
};

const tooltip = {
  de: {
    edit: "Feld bearbeiten",
    createProject: "Projekt erstellen",
    loadProject: "Projekt laden",
    delete: "Feld löschen",
  }
}


export const addLayerToSidebar = (userField, layer) => {
    // new Accordion UserField style
    const accordion = document.createElement("li");
    accordion.setAttribute("class", "list-group-item user-field-header");
    accordion.setAttribute("id", `accordion-${userField.leafletId}`);
    accordion.setAttribute("leaflet-id", userField.leafletId);
    accordion.setAttribute("user-field-id", userField.id);
  
    accordion.innerHTML = `
      <div 
        class="d-flex justify-content-between align-items-center" 
        id="accordionHeader-${userField.leafletId}" 
        user-field-id="${userField.id}"
        leaflet-id="${userField.leafletId}"
      >
        <div class="form-check form-switch h6">  
          <input type="checkbox" class="form-check-input user-field-switch" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" id="fieldSwitch-${userField.leafletId}" checked>
          <label>${userField.name}</label>
        </div>

        <div class="d-flex gap-1">
          <form id="deleteAndCalcForm-${userField.leafletId}" class="d-flex gap-1">
            <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-edit" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.edit}">
              <span><i class="bi bi-pencil-square user-field-action field-edit" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm field-name user-field-action field-project-add" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.createProject}">
              <span><i class="bi bi-plus user-field-action field-project-add" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm user-field-action field-menu" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.loadProject}">
              <span><i class="bi bi-list user-field-action field-menu" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}"></i></span>
            </button>
            <button type="button" class="btn btn-outline-secondary btn-sm user-field-action delete" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" data-bs-toggle="tooltip" data-bs-placement="right" title="${tooltip.de.delete}">
              <span><i class="bi bi-trash user-field-action delete" leaflet-id="${userField.leafletId}" user-field-id="${userField.id}" user-field-name="${userField.name}"></i></span>
            </button>
          </form>
        </div>  
      </div>
    `;

    accordion.layer = layer;
    const userFieldsAccordion = document.getElementById("userFieldList");
    userFieldsAccordion.appendChild(accordion);
  };

function addUserFieldToMap(feature, featureGroup) {
  return L.geoJson(feature, {
    className: 'user-field',
    pane: 'polygonPane',
    style: {
      color: 'var(--bs-gray-600)', 
      weight: 3,                   
      fill: false,                  
      fillOpacity: 0,               
      interactive: true             
    },
    onEachFeature: function (feature, layer) {
      layer.bindTooltip(feature.properties.name, {
                  direction: 'left',       // 'top', 'bottom', 'left', 'right', or 'auto'
                  offset: [0, 0],         // x, y offset in pixels
                  permanent: false,       // only show on hover
                  sticky: true  
              });
      layer.userFieldId = feature.properties.id
      featureGroup.addLayer(layer)
    },
  });
}

  // Load all user fields from DB
export async function getUserFieldsFromDb (featureGroup) {
  let userFields = {};
  fetch('get-user-fields/', {
    method: "GET",
    credentials: "same-origin",
    headers: {
      Accept: "application/json",
      "X-Requested-With": "XMLHttpRequest",
    },
  })
  .then(response => response.json())
  .then(data => {
    // clear all userFields from map and sidebar
    $("#display-data").empty();
    const userFieldsDb = data.user_fields;
    
    userFieldsDb.forEach((el) => {
      let layerGeoJson = addUserFieldToMap(el, featureGroup);
      
      const userField = new UserField(
        el.properties.name,
        el.properties.id,  
        el.properties.centroid_lat || null,
        el.properties.centroid_lon || null,
        el.properties.user_projects || [], // Ensure user_projects is an array
        el.properties.properties || {}
      );

      // Add the layer to the droughtFeatureGroup layer group
      // featureGroup.addLayer(layer);
      const newLayer = Object.values(layerGeoJson._layers)[0];
      // featureGroup.addLayer(newLayer);
      userField.leafletId  = featureGroup.getLayerId(newLayer);
      userFields[userField.leafletId ] = userField;
      // console.log("getData, userFields: ", userFields);
      addLayerToSidebar(userField, newLayer);

    });
    localStorage.setItem('userFields', JSON.stringify(userFields))
  })
  .catch(error => {
    console.log(error);
  });
};

