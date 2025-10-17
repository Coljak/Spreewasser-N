import { getGeolocation, handleAlerts, getCSRFToken, saveProject, observeDropdown, populateDropdown,  setLanguage, addToDropdown } from '/static/shared/utils.js';
export class ToolboxProject {
  constructor(project = {}) {
    this.id = project.id ?? null;
    this.name = project.name ?? '';
    this.updated = project.updated ?? null;
    this.description = project.description ?? '';
    this.userField = project.userField ?? null;
    this.toolboxType = project.toolboxType ?? 'generic';
    this.isSaved = project.isSaved ?? false;

    return new Proxy(this, {
      set: (target, prop, value) => {
        if (prop !== 'isSaved' && target[prop] !== value) {
          target.isSaved = false; // mark modified
        }
        target[prop] = value;
        return true;
      }
    });
  }

  toJson() {
    return JSON.stringify(this);
  }

  saveToLocalStorage() {
    localStorage.setItem('toolbox_project', this.toJson());
    console.log('saveToLocalStorage');
  }

  /** Save project to backend */
  async saveToDB() {
    try {
      const response = await fetch('save-project/', {
        method: 'POST', // POST for new, PUT for existing
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
         },
        body: this.toJson()
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      
      // Optionally update local id and mark as saved
      if (data.project_id) this.id = data.project_id;
      this.isSaved = true;
      this.saveToLocalStorage();
      console.log('Project saved to backend');
      return data;
    } catch (err) {
      console.error('Failed to save project:', err);
      throw err;
    }
  }

  static subclassRegistry = {};

  static registerSubclass(toolboxType, subclass) {
    ToolboxProject.subclassRegistry[toolboxType] = subclass;
  }

  static loadFromLocalStorage() {
    const stored = localStorage.getItem('toolbox_project');
    if (!stored) return null;

    const json = JSON.parse(stored);
    const cls = ToolboxProject.subclassRegistry[json.toolboxType];
    return cls ? cls.fromJson(json) : new ToolboxProject(json);
  }

  static fromJson(json) {
    return new ToolboxProject(json);
  }
}
