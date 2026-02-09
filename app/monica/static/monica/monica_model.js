import { 
    MonicaCalculation, 
    MonicaProject, 
    Rotation, 
    Workstep,  
    loadProjectFromDB, 
    loadProjectToGui, 
    handleDateChange, 
    addWorkstepToGui, 
    addRotationToGui,
    createChartDataset,
    addMonicaEvents,
    bindModalEventListeners,
    updateDropdown,
    setOutputSettings,
    startMonica
} from '/static/monica/monica.js';
import { 
    getGeolocation, 
    handleAlerts, 
    getCSRFToken, 
    saveProject, 
    observeDropdown, 
    populateDropdown,  
    setLanguage, 
    addToDropdown 
} from '/static/shared/utils.js';


window.isLoading = false;

// var project = new MonicaProject();
// Event listeners
var language = 'de-DE'
document.addEventListener('DOMContentLoaded', () => {
    // var advancedMode = false;
    setLanguage(language);
    setOutputSettings();
    addMonicaEvents(); // adds all Eventlisteners
    startMonica(); // arranges and triggers the right tab


    let project = new MonicaProject(defaultProject); // with defaultProject coming from the backend via .html
    project.saveToLocalStorage();
    
    loadProjectToGui(project);
});

