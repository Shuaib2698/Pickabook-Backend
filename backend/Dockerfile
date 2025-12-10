FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads results templates

# Create a simple template for demo - FIXED VERSION
RUN echo "Creating template..." && \
    python -c "from PIL import Image, ImageDraw; \
    img = Image.new('RGB', (1024, 1024), color='white'); \
    draw = ImageDraw.Draw(img); \
    draw.rectangle([200, 200, 824, 824], outline='blue', width=5); \
    draw.text((412, 900), 'Personalized Storybook', fill='black'); \
    img.save('templates/storybook_template.png')"

    # ... (rest of Dockerfile remains the same until the template creation part)

# Create a simple template for demo - USING SCRIPT VERSION
RUN mkdir -p templates
COPY create_template.py .
RUN python create_template.py

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]