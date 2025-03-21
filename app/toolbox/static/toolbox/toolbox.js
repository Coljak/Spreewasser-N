export class ToolboxProject {
  constructor (project = {}) {
    this.id = project.id ?? null;
    this.name = project.name ?? '';
    this.updated = project.updated ?? null;
    this.description = project.description ?? '';
    this.userField = project.userField ?? null;
    this.type = project.type ?? 'injection';
  }

    // Convert instance to JSON for storage
    toJson() {
      return JSON.stringify(this);
  }

  // Save project to localStorage
  saveToLocalStorage() {
      localStorage.setItem('toolbox_project', this.toJson());
  }

  // Load project from localStorage
  static loadFromLocalStorage() {
      const storedProject = localStorage.getItem('toolbox_project');
      return storedProject ? ToolboxProject.fromJson(JSON.parse(storedProject)) : null;
  }

  // Static method to create ToolboxProject from JSON
  static fromJson(json) {
      return new ToolboxProject(json);
  }
};

export async function toolboxSinks() {
  try {
      const response = await fetch('toolbox_sinks/');
      if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const geojsonData = await response.json();

      // Create a Leaflet GeoJSON layer
      const toolboxSinks = L.geoJSON(geojsonData, {
          attribution: 'Toolbox Sinks',
          onEachFeature: function (feature, layer) {
              layer.bindTooltip(feature.properties.name);
          }
      });

      return toolboxSinks; // Return the Leaflet layer
  } catch (error) {
      console.error("Error loading project region:", error);
      return null;
  }
};



