function showOutput(value) {
    const output = document.getElementById('output');
    if (typeof value === 'string') {
        output.textContent = value;
        return;
    }
    output.textContent = JSON.stringify(value, null, 2);
}

function parseJsonTextarea(textareaId) {
    const raw = document.getElementById(textareaId).value.trim();
    if (!raw) {
        return null;
    }
    return JSON.parse(raw);
}

async function sendRequest(method, path, body) {
    try {
        const options = { method };
        if (body !== undefined && body !== null && method !== 'GET' && method !== 'DELETE') {
            options.headers = { 'Content-Type': 'application/json' };
            options.body = JSON.stringify(body);
        }

        const response = await fetch(path, options);
        const contentType = response.headers.get('content-type') || '';
        let data;
        if (contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        showOutput({
            method,
            path,
            status: response.status,
            ok: response.ok,
            data
        });
    } catch (error) {
        showOutput({ error: error.message });
    }
}

function sendJsonFromTextarea(method, path, textareaId) {
    try {
        const body = parseJsonTextarea(textareaId);
        sendRequest(method, path, body);
    } catch (error) {
        showOutput({ error: 'Invalid JSON', details: error.message });
    }
}

function patchEntity(prefix, idInputId, textareaId) {
    const id = document.getElementById(idInputId).value;
    if (!id) {
        showOutput({ error: 'ID is required.' });
        return;
    }
    sendJsonFromTextarea('PATCH', `${prefix}${id}`, textareaId);
}

function deleteEntity(prefix, idInputId) {
    const id = document.getElementById(idInputId).value;
    if (!id) {
        showOutput({ error: 'ID is required.' });
        return;
    }
    sendRequest('DELETE', `${prefix}${id}`);
}

function dailyQualityReport() {
    const date = document.getElementById('daily-quality-date').value;
    const query = date ? `?date=${encodeURIComponent(date)}` : '';
    sendRequest('GET', `/report/daily-quality${query}`);
}

function defectParetoReport() {
    const groupBy = document.getElementById('defect-pareto-group').value;
    sendRequest('GET', `/report/defect-pareto?group_by=${encodeURIComponent(groupBy)}`);
}

function updateExportLinks() {
    const format = document.getElementById('export-format').value;
    document.getElementById('export-defects-link').href = `/report/export/defects?format=${encodeURIComponent(format)}`;
    document.getElementById('export-inspections-link').href = `/report/export/inspections?format=${encodeURIComponent(format)}`;
}

function genericCall() {
    const method = document.getElementById('generic-method').value;
    const path = document.getElementById('generic-path').value;
    if (!path.startsWith('/')) {
        showOutput({ error: 'Path must start with /' });
        return;
    }

    if (method === 'POST' || method === 'PATCH') {
        sendJsonFromTextarea(method, path, 'generic-body');
    } else {
        sendRequest(method, path);
    }
}

function bindEndpointButtons() {
    document.querySelectorAll('[data-request-method][data-request-path]').forEach((button) => {
        button.addEventListener('click', () => {
            sendRequest(button.dataset.requestMethod, button.dataset.requestPath);
        });
    });

    document.querySelectorAll('[data-json-method][data-json-path][data-json-textarea]').forEach((button) => {
        button.addEventListener('click', () => {
            sendJsonFromTextarea(button.dataset.jsonMethod, button.dataset.jsonPath, button.dataset.jsonTextarea);
        });
    });

    document.querySelectorAll('[data-patch-prefix][data-patch-id][data-patch-textarea]').forEach((button) => {
        button.addEventListener('click', () => {
            patchEntity(button.dataset.patchPrefix, button.dataset.patchId, button.dataset.patchTextarea);
        });
    });

    document.querySelectorAll('[data-delete-prefix][data-delete-id]').forEach((button) => {
        button.addEventListener('click', () => {
            deleteEntity(button.dataset.deletePrefix, button.dataset.deleteId);
        });
    });
}

function bindReportButtons() {
    document.getElementById('daily-quality-button').addEventListener('click', dailyQualityReport);
    document.getElementById('defect-pareto-button').addEventListener('click', defectParetoReport);
    document.getElementById('export-format').addEventListener('change', updateExportLinks);
}

function bindGenericCaller() {
    document.getElementById('generic-call-button').addEventListener('click', genericCall);
}

document.addEventListener('DOMContentLoaded', () => {
    bindEndpointButtons();
    bindReportButtons();
    bindGenericCaller();
    updateExportLinks();
});
