import logging

def setup_logging():
    # Create a custom logger
    logger = logging.getLogger("ftp_app")
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler("ftp_app.log")
    file_handler.setLevel(logging.INFO)
    
    # Create formatters and add them to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    
    return logger
