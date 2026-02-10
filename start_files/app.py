from fastapi import Depends, FastAPI, HTTPException, Request
from start_files.config import get_templates
from start_files.routes.routes import router
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import logging
import os


load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI()
    #app.add_middleware(BlockApiMiddleware)
    app.mount("/static", StaticFiles(directory="start_files/static"), name="static")
    app.include_router(router)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/inventory.log")
        ]
    )
    
    # Initialize state variables
    templates = get_templates()
    app.state.templates = templates
    
    return app



