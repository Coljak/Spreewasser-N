(function(){"use strict";try{if(typeof document!="undefined"){var e=document.createElement("style");e.appendChild(document.createTextNode(`.leaflet-pane.leaflet-lhl-raised-pane {
	z-index: 620;
}

.leaflet-pane.leaflet-lhl-almost-over-pane {
	z-index: 201;
}`)),document.head.appendChild(e)}}catch(n){console.error("vite-plugin-css-injected-by-js",n)}})();
var __defProp = Object.defineProperty;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __publicField = (obj, key, value) => {
  __defNormalProp(obj, typeof key !== "symbol" ? key + "" : key, value);
  return value;
};
(function(global, factory) {
  typeof exports === "object" && typeof module !== "undefined" ? factory(exports, require("leaflet")) : typeof define === "function" && define.amd ? define(["exports", "leaflet"], factory) : (global = typeof globalThis !== "undefined" ? globalThis : global || self, factory((global.L = global.L || {}, global.L.HighlightableLayers = {}), global.L));
})(this, function(exports2, leaflet) {
  "use strict";
  const panes = "";
  leaflet.Map.addInitHook(function() {
    this.createPane("lhl-raised");
    this.createPane("lhl-almost-over");
  });
  function setLayerPane(layer, pane) {
    if (layer.options.pane == pane)
      return;
    layer.options.pane = pane;
    if (layer["_map"])
      layer["_map"].removeLayer(layer).addLayer(layer);
  }
  function setLayerRenderer(layer, renderer) {
    if (layer.options.renderer == renderer)
      return;
    layer.options.renderer = renderer;
    if (layer._renderer) {
      layer._renderer._removePath(layer);
      layer._renderer = renderer;
      layer._renderer._layers[leaflet.Util.stamp(layer)] = layer;
      layer._renderer._updateStyle(layer);
      layer._renderer._addPath(layer);
    }
  }
  function getBrightness(colour) {
    const r = parseInt(colour.substr(0, 2), 16) / 255;
    const g = parseInt(colour.substr(2, 2), 16) / 255;
    const b = parseInt(colour.substr(4, 2), 16) / 255;
    return Math.sqrt(0.241 * r * r + 0.691 * g * g + 0.068 * b * b);
  }
  function clone(obj) {
    return Object.assign(Object.create(Object.getPrototypeOf(obj)), obj);
  }
  function generatePolygonStyles(options, renderer) {
    const isBright = getBrightness(options.color.replace(/^#/, "")) > 0.7;
    const outlineColor = options.outlineColor ?? (isBright ? "#000000" : "#ffffff");
    const lineWeight = options.outlineColor == null && options.outlineWeight == null && isBright ? Math.round(options.weight / 1.6) : options.weight;
    const outlineWeight = options.outlineWeight ?? lineWeight * 2;
    return {
      main: {
        ...options,
        renderer,
        weight: outlineWeight,
        opacity: 0
      },
      fill: {
        ...options,
        renderer,
        stroke: false
      },
      outline: {
        ...options,
        color: outlineColor,
        weight: outlineWeight,
        renderer,
        fill: false
      },
      border: {
        ...options,
        weight: lineWeight,
        renderer,
        fill: false
      }
    };
  }
  function generatePolylineStyles(options, renderer) {
    const isBright = getBrightness(options.color.replace(/^#/, "")) > 0.7;
    const outlineColor = options.outlineColor ?? (isBright ? "#000000" : "#ffffff");
    const lineWeight = options.outlineColor == null && options.outlineWeight == null && isBright ? Math.round(options.weight / 1.6) : options.weight;
    const outlineWeight = options.outlineWeight ?? lineWeight * 2;
    return {
      outline: {
        ...options,
        color: outlineColor,
        weight: outlineWeight,
        renderer
      },
      line: {
        ...options,
        weight: lineWeight,
        renderer
      },
      main: {
        opacity: 0,
        weight: Math.max(20, outlineWeight, lineWeight),
        pane: "lhl-almost-over"
      }
    };
  }
  function createHighlightableLayerClass(BaseClass, cloneMethods = [], defaultOptions) {
    const result = class HighlightableLayer extends BaseClass {
      constructor(...args) {
        super(...args);
        __publicField(this, "realOptions");
        __publicField(this, "layers");
        __publicField(this, "_isAdding", false);
        this.realOptions = Object.assign(Object.create(Object.getPrototypeOf(this.options)), {
          generateStyles: generatePolygonStyles,
          ...defaultOptions,
          ...this.options
        });
        this.layers = {};
        for (const layerName of Object.keys(this.realOptions.generateStyles(this.realOptions, new leaflet.SVG()) ?? {})) {
          if (layerName !== "main") {
            this.layers[layerName] = new BaseClass(...args);
            this.layers[layerName].options.interactive = false;
            if (BaseClass === leaflet.Polyline || BaseClass.prototype instanceof leaflet.Polyline) {
              this.layers[layerName]._updateBounds = function() {
                if (this._rawPxBounds)
                  BaseClass.prototype._updateBounds.call(this);
              };
            }
          }
        }
      }
      beforeAdd(map) {
        this._renderer = map._createRenderer();
        map.addLayer(this._renderer);
        return this;
      }
      onAdd(map) {
        super.onAdd(map);
        for (const layerName of Object.keys(this.layers)) {
          map.addLayer(this.layers[layerName]);
        }
        Promise.resolve().then(() => {
          this.setStyle({});
        });
        return this;
      }
      onRemove(map) {
        for (const layerName of Object.keys(this.layers)) {
          map.removeLayer(this.layers[layerName]);
        }
        map.removeLayer(this._renderer);
        super.onRemove(map);
        return this;
      }
      setStyle(style) {
        var _a, _b;
        Object.assign(this.realOptions, style);
        const renderer = this._renderer || new leaflet.SVG();
        renderer.options.pane = this.realOptions.raised ? "lhl-raised" : this.realOptions.pane;
        if (renderer._container)
          renderer.getPane().appendChild(renderer._container);
        const styles = ((_b = (_a = this.realOptions).generateStyles) == null ? void 0 : _b.call(_a, Object.assign(clone(this.realOptions), { opacity: 1 }), renderer)) ?? { main: clone(this.realOptions) };
        if (styles.main.pane)
          setLayerPane(this, styles.main.pane);
        if (styles.main.renderer)
          setLayerRenderer(this, styles.main.renderer);
        super.setStyle(styles.main);
        for (const layerName of Object.keys(this.layers)) {
          if (styles[layerName].pane)
            setLayerPane(this.layers[layerName], styles[layerName].pane);
          if (styles[layerName].renderer)
            setLayerRenderer(this.layers[layerName], styles[layerName].renderer);
          this.layers[layerName].setStyle(styles[layerName]);
        }
        if (renderer._container)
          renderer._container.style.opacity = `${this.realOptions.opacity ?? 1}`;
        return this;
      }
      _updateBounds() {
        if (!(this instanceof leaflet.Polyline) || this._rawPxBounds)
          super._updateBounds();
      }
    };
    for (const method of ["redraw", ...cloneMethods]) {
      result.prototype[method] = function(...args) {
        const r = Object.getPrototypeOf(result.prototype)[method].apply(this, args);
        for (const layerName of Object.keys(this.layers)) {
          this.layers[layerName][method].apply(this.layers[layerName], args);
        }
        return r;
      };
    }
    return result;
  }
  const HighlightableCircle = createHighlightableLayerClass(leaflet.Circle, ["setRadius", "setLatLng"]);
  const HighlightableCircleMarker = createHighlightableLayerClass(leaflet.CircleMarker, ["setRadius", "setLatLng"]);
  const HighlightablePolygon = createHighlightableLayerClass(leaflet.Polygon, ["setLatLngs"]);
  const HighlightablePolyline = createHighlightableLayerClass(leaflet.Polyline, ["setLatLngs"], {
    generateStyles: generatePolylineStyles
  });
  const HighlightableRectangle = createHighlightableLayerClass(leaflet.Rectangle, ["setBounds"]);
  exports2.HighlightableCircle = HighlightableCircle;
  exports2.HighlightableCircleMarker = HighlightableCircleMarker;
  exports2.HighlightablePolygon = HighlightablePolygon;
  exports2.HighlightablePolyline = HighlightablePolyline;
  exports2.HighlightableRectangle = HighlightableRectangle;
  exports2.clone = clone;
  exports2.createHighlightableLayerClass = createHighlightableLayerClass;
  exports2.generatePolygonStyles = generatePolygonStyles;
  exports2.generatePolylineStyles = generatePolylineStyles;
  exports2.getBrightness = getBrightness;
  exports2.setLayerPane = setLayerPane;
  exports2.setLayerRenderer = setLayerRenderer;
  Object.defineProperty(exports2, Symbol.toStringTag, { value: "Module" });
});
//# sourceMappingURL=L.HighlightableLayers.js.map
