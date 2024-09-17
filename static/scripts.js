async function submitForm(event, url, formData, responseElementId) {
    event.preventDefault();
    const responseElement = document.getElementById(responseElementId);
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        });
        const result = await response.json();
        responseElement.innerText = result.message;
    } catch (error) {
        responseElement.innerText = `Error: ${error.message}`;
    }
}

async function fetchCredentials() {
    try {
        const response = await fetch('/ftp/get_credentials');
        const result = await response.json();
        document.getElementById('credentials').innerText = JSON.stringify(result, null, 2);
    } catch (error) {
        document.getElementById('credentials').innerText = `Error: ${error.message}`;
    }
}

async function checkConnection() {
    try {
        const response = await fetch('/ftp/check_connection');
        const result = await response.json();
        document.getElementById('connection-status').innerText = result.message;
    } catch (error) {
        document.getElementById('connection-status').innerText = `Error: ${error.message}`;
    }
}

async function uploadFolder() {
    try {
        const response = await fetch('/ftp/upload_folder', { method: 'POST' });
        const result = await response.json();
        document.getElementById('upload-folder-status').innerText = result.message;
    } catch (error) {
        document.getElementById('upload-folder-status').innerText = `Error: ${error.message}`;
    }
}

async function stopUpload() {
    try {
        const response = await fetch('/ftp/stop_upload', { method: 'POST' });
        const result = await response.json();
        document.getElementById('stop-upload-status').innerText = result.message;
    } catch (error) {
        document.getElementById('stop-upload-status').innerText = `Error: ${error.message}`;
    }
}

