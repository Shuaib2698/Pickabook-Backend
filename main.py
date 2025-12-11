import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import aiofiles
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

# Initialize FastAPI app
app = FastAPI(
    title="Pickabook AI Personalization API",
    description="API for personalizing storybook illustrations with AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://pickabook-frontend-kappa.vercel.app/","https://vercel.com/shuaib2698s-projects/pickabook/BCKuhnVgL2yJjs27w8T27APTfavU","https://pickabook-ochre.vercel.app/",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class UploadResponse(BaseModel):
    task_id: str
    message: str
    status: str = "processing"

class ProcessingStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    result_url: Optional[str] = None
    error: Optional[str] = None

# Constants
UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
TEMPLATE_DIR = "templates"

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

# Task storage
tasks = {}

@app.get("/")
async def root():
    return {
        "message": "Pickabook AI Personalization API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "upload_dir": os.path.exists(UPLOAD_DIR),
            "result_dir": os.path.exists(RESULT_DIR),
            "template_dir": os.path.exists(TEMPLATE_DIR)
        }
    }

@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload an image for processing"""
    try:
        # Generate unique ID
        task_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        file_path = os.path.join(UPLOAD_DIR, f"{task_id}_original.{file_extension}")
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Initialize task status
        tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "result_url": None,
            "error": None,
            "file_path": file_path
        }
        
        # Start background processing
        asyncio.create_task(process_image(task_id, file_path))
        
        return UploadResponse(
            task_id=task_id,
            message="Image uploaded successfully. Processing started."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_image(task_id: str, image_path: str):
    """Process image in background"""
    try:
        # Update progress
        tasks[task_id]["progress"] = 10
        
        # Step 1: Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not read image")
        
        tasks[task_id]["progress"] = 30
        
        # Step 2: Create or load template
        template_path = os.path.join(TEMPLATE_DIR, "storybook_template.png")
        if not os.path.exists(template_path):
            # Create a simple template
            template = Image.new('RGB', (1024, 1024), color='white')
            draw = ImageDraw.Draw(template)
            # Draw a decorative border
            draw.rectangle([50, 50, 974, 974], outline='gold', width=10)
            draw.rectangle([100, 100, 924, 924], outline='brown', width=5)
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            draw.text((350, 50), "Pickabook", fill="blue", font=font)
            draw.text((250, 900), "Personalized Story", fill="darkred", font=font)
            
            # Save template
            template.save(template_path)
            print(f"Created template at: {template_path}")
        
        template = Image.open(template_path)
        
        tasks[task_id]["progress"] = 50
        
        # Step 3: Process image (simple resize and paste)
        # Convert OpenCV image to PIL
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        
        # Resize to fit template
        pil_image = pil_image.resize((400, 400))
        
        # Create result image
        result = template.copy()
        
        # Paste at center
        paste_x = (1024 - 400) // 2  # 312
        paste_y = (1024 - 400) // 2  # 312
        result.paste(pil_image, (paste_x, paste_y))
        
        # Add decorative border
        draw = ImageDraw.Draw(result)
        draw.rectangle([paste_x-5, paste_y-5, paste_x+405, paste_y+405], 
                      outline='gold', width=5)
        
        tasks[task_id]["progress"] = 80
        
        # Step 4: Save result
        result_filename = f"{task_id}_final.png"
        result_path = os.path.join(RESULT_DIR, result_filename)
        result.save(result_path)
        
        # Update task status
        tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "result_url": f"/api/download/{result_filename}"
        })
        
        print(f"Task {task_id} completed successfully")
        
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        tasks[task_id].update({
            "status": "failed",
            "error": str(e)
        })

@app.get("/api/result/{task_id}", response_model=ProcessingStatus)
async def get_result(task_id: str):
    """Get the processing status and result for a task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    status = tasks[task_id]
    return ProcessingStatus(
        task_id=task_id,
        status=status["status"],
        progress=status.get("progress"),
        result_url=status.get("result_url"),
        error=status.get("error")
    )

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a processed file"""
    file_path = os.path.join(RESULT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=f"pickabook_{filename}",
        media_type="image/png"
    )

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Pickabook AI Personalization API")
    print("=" * 50)
    print(f"API URL: http://localhost:8000")
    print(f"Docs: http://localhost:8000/docs")
    print(f"Health: http://localhost:8000/api/health")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
