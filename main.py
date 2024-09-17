from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from io import BytesIO
import aioftp
import uvicorn
import logging
import os
from logging_config import setup_logging

app = FastAPI()

# In-memory storage for FTP credentials
ftp_credentials = {}
upload_folder = ""

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure logging
# Set up logging
logger = setup_logging()


# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Pydantic model for FTP credentials
class FTPCredentials(BaseModel):
    host: str
    port: int
    username: str
    password: str


# Route to render the HTML form
@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


# Route to handle the upload of FTP credentials
@app.post("/ftp/upload_credentials")
async def upload_ftp_credentials(
    host: str = Form(...),
    port: int = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    remotepath: str = Form(...)
):
    ftp_credentials['host'] = host
    ftp_credentials['port'] = port
    ftp_credentials['username'] = username
    ftp_credentials['password'] = password
    ftp_credentials['remotepath'] = remotepath
    return {"message": "FTP credentials uploaded successfully"}


# Route to fetch the current FTP credentials
@app.get("/ftp/get_credentials")
async def get_ftp_credentials():
    if not ftp_credentials:
        raise HTTPException(status_code=404, detail="FTP credentials not found")
    return ftp_credentials

# Route to check the connection to the FTP server
@app.get("/ftp/check_connection")
async def check_connection():
    if not ftp_credentials:
        raise HTTPException(status_code=400, detail="FTP credentials not set")
    
    try:
        # Test connection to the FTP server
        async with aioftp.Client.context(
            ftp_credentials['host'],
            port=ftp_credentials['port'],
            user=ftp_credentials['username'],
            password=ftp_credentials['password']
        ) as client:
            # Connection is successful if no exception is raised
            return {"message": "Connection to FTP server successful"}
    
    except Exception as e:
        # Log the error
        logger.error(f"Error connecting to FTP server: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to connect to FTP server")


# Route to upload a file to the FTP server
@app.post("/ftp/upload_folder")
async def upload_folder():
    local_folder = upload_folder  # Update this to your folder path
    if not ftp_credentials:
        raise HTTPException(status_code=400, detail="FTP credentials not provided")
    if not upload_folder:
        raise HTTPException(status_code=400,detail="Folder Path not provided")

    try:
        async with aioftp.Client.context(
            ftp_credentials['host'],
            port=ftp_credentials['port'],
            user=ftp_credentials['username'],
            password=ftp_credentials['password']
        ) as client:
            await upload_directory_recursive(client, upload_folder, ftp_credentials['remotepath'])
        return {"message": "All files from folder uploaded successfully"}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return {"message": f"Upload failed: {e}"}

async def upload_directory_recursive(client, local_dir, remote_dir):
    # Ensure remote directory exists
    async with client.change_directory(remote_dir):
        for entry in os.listdir(local_dir):
            local_path = os.path.join(local_dir, entry)
            if os.path.isdir(local_path):
                # Recursively upload subdirectories
                remote_subdir = os.path.join(remote_dir, entry).replace(os.path.sep, '/')
                try:
                    async with client.make_directory(remote_subdir):
                        await upload_directory_recursive(client, local_path, remote_subdir)
                except Exception as e:
                    logger.error(f"Failed to create remote directory {remote_subdir}: {e}")
            elif os.path.isfile(local_path):
                # Upload files
                remote_file_path = os.path.join(remote_dir, entry).replace(os.path.sep, '/')
                with open(local_path, "rb") as file:
                    file_data = file.read()
                    logger.info(f"Uploading file: {entry} to {remote_file_path}")
                    await client.upload(local_path,remote_file_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Run the FastAPI server (use the command below)
# uvicorn main:app --reload
