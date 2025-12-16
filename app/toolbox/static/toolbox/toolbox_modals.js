import { ToolboxProject } from '/static/toolbox/toolbox_project.js';
import {handleAlerts} from '/static/shared/utils.js';
import { setProjectInfoHeader } from '/static/toolbox/toolbox.js';
import { startToolbox } from '/static/toolbox/toolbox_three_split.js';

export function saveNewProjectModalEvents() {
    $('#saveToolboxProjectButton').on('click', async function () {
        const projectNameInput = $('#id_project_name');
        const projectName = projectNameInput.val().trim();

        // Validate project name
        if (!projectName) {
        projectNameInput.addClass('is-invalid');
        projectNameInput.focus();
        return;
        } else {
        projectNameInput.removeClass('is-invalid');
        }

        const project = ToolboxProject.loadFromLocalStorage();
        // const isNewProject = (project.toolboxType === 'generic');
        const pageReload = $('#saveToolboxProjectButton').data('page-reload')
        project.name = projectName;
        // project.userField = $('#userFieldSelect').val();
        project.toolboxType = $('#projectTypeSelect').val();
        project.description = $('#id_project_description').val().trim();
        project.saveToLocalStorage();
        try {
        setProjectInfoHeader(project);
        } catch {;}
        

        $('#toolboxProjectModal').modal('hide');
        try {
        const data = await project.saveToDB(); 
        console.log('data', data);

        if (data.success) {

            handleAlerts({ success: data.success, message: data.message });
            if (pageReload) {
            startToolbox(project); 
            } else {
            $('#id_toolbox_project').prepend(
                $('<option>', { value: project.id, text: project.name })
            );
            $('#id_toolbox_project').val(project.id);
            }

            // }
        } else {
            
            handleAlerts(data.message);
        }

        } catch (err) {
        console.error('Failed to save project:', err);
        handleAlerts({ success: false, message: 'Error saving project.' });
        }
    });
  
    
};
    