console.log('user_dashboard.js is loaded!')




function main_map_init(map, options) {
  console.log(options) /* set drawControl: true
  /* make it get the geoIP and send to view map.setView([51.2, 7], 9); */
  var marker = L.marker([51.2, 7]).addTo(map);
  
  const sidebarLeft = L.control.sidebar('sidebar',{
    closeButton: true,
    position: 'left'
  } ).addTo(map);



  var drawnItems = L.featureGroup().addTo(map)
  map.addLayer(drawnItems);

  var drawControl = new L.Control.Draw({
    draw: {
        position: 'right', 
        circle: false,
        polyline: false,
        polygon: {
            title: 'Draw a sexy polygon!',
            allowIntersection: false,
            drawError: {
                color: '#b00b09',
                timeout: 1000
            },
            shapeOptions: {
                color: '#bada55'
            }
        },
        
    },
    edit: {
      featureGroup: drawnItems
    }
    
});

map.addControl(drawControl);
L.DomUtil.addClass(map._div, '')

};


