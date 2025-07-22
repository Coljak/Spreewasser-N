import { initializeSliders } from "./custom_slider.js";

document.addEventListener("DOMContentLoaded", function () {
    // Initialize the sliders when the DOM is fully loaded
    // initializeSliders();
    const setLabel = (lbl, val) => {
        const label = $(`#slider-${lbl}-label`);
        label.text(val);
        const slider = $(`#slider-div .${lbl}-slider-handle`);
        const rect = slider[0].getBoundingClientRect();
        label.offset({
          top: rect.top - 30,
          left: rect.left
        });
      }
      
      const setLabels = (values) => {
        setLabel("min", values[0]);
        setLabel("max", values[1]);
      }
      
      
    //   $('#ex2').slider().on('slide', function(ev) {
    //     setLabels(ev.value);
    //   });
    //   setLabels($('#ex2').attr("data-value").split(","));
});



var map = L.map("map").setView([51.42, 10], 6), 
  feature_group = new L.featureGroup([]), raster_group = new L.LayerGroup([]), 
  southWest = L.latLng(45, 1), northEast = L.latLng(57, 20), 
  OpenStreetMap_DE = L.tileLayer.wms("https://ows.terrestris.de/osm/service?", 
    { layers: "OSM-WMS", 
      attribution: 'Basis: <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> Contributors' 
    }); 
      
      OpenStreetMap_DE.addTo(map); 
      var layerOrder = new Array, 
      BundesLaenderPegel = new L.geoJson(JSON_BundesLaenderPegel, 
        { onEachFeature: pop_Pegel, pointToLayer: function (a, b) 
          { return L.circleMarker(b, { radius: 4, fillColor: getColorPegel(a.properties.Pegel_Url, a.properties.Pegel_Nr), color: "#2b2b2b", weight: 1, opacity: 1, fillOpacity: 1 }) } }); function pop_Pegel(c, b) { "" === String(c.properties.Pegel_Url) ? purl = "" : purl = '<a href="' + String(c.properties.Pegel_Url) + '" target="_blank"</a>Weitere&nbsp;' + String(c.properties.Pegel_Url_Txt) + "</a>", "bw" === String(c.properties.Hrsg_Id) && (purl = '<a href="' + String(c.properties.Pegel_Url) + '#X5" target="_blank"</a>Weitere&nbsp;' + String(c.properties.Pegel_Url_Txt) + "</a>"), "0" === String(c.properties.Url_Dgj_Q) ? dgjurl_q = "" : dgjurl_q = '<a href="' + String(c.properties.Url_Dgj_Q) + '" target="_blank"</a>DGJ-Seite (Q)</a>', "0" === String(c.properties.Url_Dgj_W) ? dgjurl_w = "" : dgjurl_w = '<a href="' + String(c.properties.Url_Dgj_W) + '" target="_blank"</a>DGJ-Seite (W)</a>'; var a = '<table><tr>\n<th scope="row">Pegelname&nbsp;</th>\n                          <td>' + String(c.properties.Pegelname) + '</td>\n                    </tr>\n                    <tr>\n<th scope="row">Gewässer&nbsp;</th>\n                          <td>' + String(c.properties.Gewaesser) + '</td>\n                    </tr>\n                    <tr>\n                          <td scope="row">' + dgjurl_w + '</td>\n                    </tr>\n                    <tr>\n                          <td scope="row">' + dgjurl_q + '</td>\n                    </tr>\n                    <tr>\n                         <td colspan="2">' + purl + "</td>\n                    </tr>\n             </table>"; b.bindPopup(a); var d = String(c.geometry.coordinates).split(","), f = d[0], e = d[1]; b.on("click", (function (h) { zoomToPegel(h, e, f), this.openPopup() })) } function zoomToPegel(b, a, c) { map.setView(new L.LatLng(a, c), 10) } function getColorPegel(a, b) { return "#fcd764" } var BundesLaender = new L.geoJson(JSON_BundesLaender, { onEachFeature: pop_BlLaender, style: function (a) { return { weight: .75, opacity: .5, color: "black", fillOpacity: 0 } } }); function pop_BlLaender(c, b) { "" === String(c.properties.URL_0) ? blurl1 = "" : blurl1 = '<td><a href="' + String(c.properties.URL_0) + '"target="_blank"</a>Aktuelle Rohdaten</td>', "" === String(c.properties.URL_1) ? blurl2 = "" : blurl2 = '<td><a href="' + String(c.properties.URL_1) + '"target="_blank"</a>Download geprüfter Daten</td>', "" === String(c.properties.URL_2) ? blurl3 = "" : blurl3 = '<td><a href="' + String(c.properties.URL_2) + '"target="_blank"</a>Aktuelle Rohdaten u. Download</td>'; var a = "<table></td></tr><tr>\n                        <th>" + String(c.properties.BL_NAME) + "</th  ></td>\n                        </tr><tr>" + blurl1 + "</tr><tr>" + blurl2 + "</tr>" + blurl3 + "<tr></tr></table>"; b.bindPopup(a), b.on({ mouseover: highlightFeature, mouseout: resetHighlight }) } var Flussgebiete = new L.geoJson(JSON_FLUSSGEBIETE, { style: function (a) { return { color: a.properties.border_color, fillColor: a.properties.color, weight: a.properties.radius, opacity: a.properties.transp, fillOpacity: a.properties.transp } } }); Flussgebiete.addTo(map), BundesLaenderPegel.addTo(map), map.addLayer(BundesLaenderPegel); var searchControl = new L.Control.Search({ layer: BundesLaenderPegel, propertyName: "Pegelname", circleLocation: !1, hideMarkerOnCollapse: !0, zoom: 12 }); function highlightFeature(b) { b.target.setStyle({ weight: 1, color: "#666", dashArray: "", fillOpacity: .2 }), !L.Browser.ie && L.Browser.opera } function resetHighlight(a) { BundesLaender.resetStyle(a.target) } map.addControl(searchControl); var title = new L.Control; title.onAdd = function (a) { return this._div = L.DomUtil.create("div", "info"), this.update(), this._div }, title.update = function () { this._div.innerHTML = '<div id=""><strong>DGJ-Pegeldaten (Bund und Länder)</strong></div>' }, title.addTo(map); var baseMap = { "OSM Karte": OpenStreetMap_DE }, overlayMaps = { "Bundesländer": BundesLaender, Flussgebiete: Flussgebiete }; L.easyButton('<img src="img/glyphicons-372-global-small.png">', (function () { $("#pegelinfo").css("visibility"), map.setView([51.42, 10], 6), OpenStreetMap_DE.redraw() })).addTo(map), L.control.layers("", overlayMaps, { collapsed: !1 }).addTo(map), L.control.scale({ options: { position: "bottomleft", maxWidth: 100, metric: !0, imperial: !1, updateWhenIdle: !1 } }).addTo(map), map.on("overlayadd", (function (a) { a.layer === BundesLaender && (map.removeLayer(BundesLaenderPegel), BundesLaenderPegel.addTo(map)), a.layer === Flussgebiete && (map.removeLayer(BundesLaenderPegel), BundesLaenderPegel.addTo(map)) })), OpenStreetMap_DE.on("tileerror", (function () { OpenStreetMap_DE.redraw() }));