from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import aioftp
import uvicorn
import logging
import os
from logging_config import setup_logging

app = FastAPI()

# In-memory storage for FTP credentials
ftp_credentials = {}
upload_folder = ""

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


# Route to upload a file to the FTP server
@app.post("/ftp/upload_folder")
async def upload_folder_to_ftp():
    if not ftp_credentials:
        raise HTTPException(status_code=400, detail="FTP credentials not set")
    if not upload_folder:
        raise HTTPException(status_code=400, detail="Folder path not set")

    try:
        # Connect to the FTP server using aioftp
        async with aioftp.Client.context(
            ftp_credentials['host'],
            port=ftp_credentials['port'],
            user=ftp_credentials['username'],
            password=ftp_credentials['password']
        ) as client:
            for filename in os.listdir(upload_folder):
                local_path = os.path.join(upload_folder, filename)
                if os.path.isfile(local_path):
                    remote_path = ftp_credentials['remotepath'] + '/' + filename
                    with open(local_path, "rb") as file:
                        file_data = file.read()
                        logger.info(f"Uploading file: {filename} to {remote_path}")
                        await client.upload_stream(aioftp.StreamIO(file_data), remote_path)

        return {"message": "All files from folder uploaded successfully"}

    except Exception as e:
        # Log the error
        logger.error(f"Error uploading files from folder: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "_main_":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Run the FastAPI server (use the command below)
# uvicorn main:app --reload
