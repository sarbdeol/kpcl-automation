// KPCL Automation Configuration Page JavaScript

class ConfigManager {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadCurrentConfig();
    }
    
    bindEvents() {
        // App settings form
        document.getElementById('app-settings-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAppSettings();
        });
        
        // Form data form
        document.getElementById('form-data-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveFormData();
        });
        
        // Export configuration
        document.getElementById('export-config-btn').addEventListener('click', () => {
            this.exportConfiguration();
        });
        
        // Import configuration
        document.getElementById('import-config-file').addEventListener('change', (e) => {
            const importBtn = document.getElementById('import-config-btn');
            importBtn.disabled = !e.target.files.length;
        });
        
        document.getElementById('import-config-btn').addEventListener('click', () => {
            this.importConfiguration();
        });
    }
    
    loadCurrentConfig() {
        // Configuration is already loaded via template
        // This method can be extended to dynamically load config
        console.log('Configuration page loaded');
    }
    
    async saveAppSettings() {
        const form = document.getElementById('app-settings-form');
        const formData = new FormData(form);
        
        // Convert FormData to object
        const config = {};
        for (let [key, value] of formData.entries()) {
            if (key === 'headless') {
                config[key] = value === 'on';
            } else if (key === 'max_retries' || key === 'retry_interval') {
                config[key] = parseInt(value);
            } else if (key === 'schedule_time') {
                config[key] = value + ':01'; // Add seconds
            } else {
                config[key] = value;
            }
        }
        
        // Handle unchecked checkbox
        if (!formData.has('headless')) {
            config.headless = false;
        }
        
        try {
            const response = await fetch('/api/save_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ config })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('App settings saved successfully', 'success');
            } else {
                this.showNotification(data.message || 'Failed to save settings', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to save app settings', 'error');
            console.error('Save app settings error:', error);
        }
    }
    
    async saveFormData() {
        const form = document.getElementById('form-data-form');
        const formData = new FormData(form);
        
        // Convert FormData to object
        const form_data = {};
        for (let [key, value] of formData.entries()) {
            form_data[key] = value;
        }
        
        try {
            const response = await fetch('/api/save_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ form_data })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Form data saved successfully', 'success');
            } else {
                this.showNotification(data.message || 'Failed to save form data', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to save form data', 'error');
            console.error('Save form data error:', error);
        }
    }
    
    exportConfiguration() {
        // Get current form values
        const appConfig = this.getAppConfigFromForm();
        const formData = this.getFormDataFromForm();
        
        const exportData = {
            version: '1.0.0',
            exported_at: new Date().toISOString(),
            app_config: appConfig,
            form_data: formData
        };
        
        // Create and download file
        const blob = new Blob([JSON.stringify(exportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `kpcl-config-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Configuration exported successfully', 'success');
    }
    
    async importConfiguration() {
        const fileInput = document.getElementById('import-config-file');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showNotification('Please select a configuration file', 'warning');
            return;
        }
        
        try {
            const text = await file.text();
            const config = JSON.parse(text);
            
            // Validate configuration structure
            if (!config.app_config || !config.form_data) {
                throw new Error('Invalid configuration file format');
            }
            
            // Apply configuration to forms
            this.applyConfigToForms(config.app_config, config.form_data);
            
            // Save to server
            const response = await fetch('/api/save_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    config: config.app_config,
                    form_data: config.form_data
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('Configuration imported and saved successfully', 'success');
                
                // Clear file input
                fileInput.value = '';
                document.getElementById('import-config-btn').disabled = true;
            } else {
                this.showNotification(data.message || 'Failed to save imported configuration', 'error');
            }
            
        } catch (error) {
            this.showNotification('Failed to import configuration: Invalid file', 'error');
            console.error('Import configuration error:', error);
        }
    }
    
    getAppConfigFromForm() {
        const form = document.getElementById('app-settings-form');
        const formData = new FormData(form);
        
        const config = {};
        for (let [key, value] of formData.entries()) {
            if (key === 'headless') {
                config[key] = true;
            } else if (key === 'max_retries' || key === 'retry_interval') {
                config[key] = parseInt(value);
            } else if (key === 'schedule_time') {
                config[key] = value + ':01';
            } else {
                config[key] = value;
            }
        }
        
        // Handle unchecked checkbox
        if (!formData.has('headless')) {
            config.headless = false;
        }
        
        return config;
    }
    
    getFormDataFromForm() {
        const form = document.getElementById('form-data-form');
        const formData = new FormData(form);
        
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }
    
    applyConfigToForms(appConfig, formData) {
        // Apply app config
        const appForm = document.getElementById('app-settings-form');
        
        if (appConfig.schedule_time) {
            const timeInput = appForm.querySelector('[name="schedule_time"]');
            timeInput.value = appConfig.schedule_time.substring(0, 5); // Remove seconds
        }
        
        if (appConfig.max_retries !== undefined) {
            const retriesInput = appForm.querySelector('[name="max_retries"]');
            retriesInput.value = appConfig.max_retries;
        }
        
        if (appConfig.retry_interval !== undefined) {
            const intervalInput = appForm.querySelector('[name="retry_interval"]');
            intervalInput.value = appConfig.retry_interval;
        }
        
        if (appConfig.browser) {
            const browserSelect = appForm.querySelector('[name="browser"]');
            browserSelect.value = appConfig.browser;
        }
        
        if (appConfig.headless !== undefined) {
            const headlessCheckbox = appForm.querySelector('[name="headless"]');
            headlessCheckbox.checked = appConfig.headless;
        }
        
        // Apply form data
        const dataForm = document.getElementById('form-data-form');
        
        Object.keys(formData).forEach(key => {
            const input = dataForm.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = formData[key];
            }
        });
    }
    
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const toastBody = toast.querySelector('.toast-body');
        
        // Set message and type
        toastBody.textContent = message;
        
        // Update toast styling based on type
        toast.className = 'toast';
        switch (type) {
            case 'success':
                toast.classList.add('border-success');
                toastBody.className = 'toast-body text-success';
                break;
            case 'error':
                toast.classList.add('border-danger');
                toastBody.className = 'toast-body text-danger';
                break;
            case 'warning':
                toast.classList.add('border-warning');
                toastBody.className = 'toast-body text-warning';
                break;
            default:
                toast.classList.add('border-info');
                toastBody.className = 'toast-body text-info';
        }
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
    
    validateConfiguration(config) {
        const errors = [];
        
        // Validate app config
        if (config.app_config) {
            const appConfig = config.app_config;
            
            if (appConfig.max_retries && (appConfig.max_retries < 1 || appConfig.max_retries > 10)) {
                errors.push('Max retries must be between 1 and 10');
            }
            
            if (appConfig.retry_interval && (appConfig.retry_interval < 5 || appConfig.retry_interval > 300)) {
                errors.push('Retry interval must be between 5 and 300 seconds');
            }
            
            if (appConfig.browser && !['chrome', 'firefox'].includes(appConfig.browser)) {
                errors.push('Browser must be either chrome or firefox');
            }
        }
        
        // Validate form data
        if (config.form_data) {
            const formData = config.form_data;
            const requiredFields = [
                'ash_utilization', 'pickup_time', 'vehicle_type',
                'authorised_person', 'vehicle_no', 'dl_no', 'driver_mob_no'
            ];
            
            requiredFields.forEach(field => {
                if (!formData[field] || formData[field].trim() === '') {
                    errors.push(`${field} is required`);
                }
            });
        }
        
        return errors;
    }
}

// Initialize configuration manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.configManager = new ConfigManager();
});
