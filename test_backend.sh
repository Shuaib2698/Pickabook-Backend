#!/bin/bash
echo "Testing Pickabook Backend..."
echo "=============================="

# Check if backend is running
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✓ Backend is running on port 8000"
    
    # Test health endpoint
    echo "Health check:"
    curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/api/health
    echo ""
    
    # Create a test image
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (500, 500), color='lightblue')
draw = ImageDraw.Draw(img)
draw.ellipse((150, 150, 350, 350), fill='yellow')
draw.ellipse((200, 200, 230, 230), fill='black')
draw.ellipse((270, 200, 300, 230), fill='black')
draw.arc((200, 250, 300, 350), 0, 180, fill='red', width=5)
img.save('test_child.png')
print('✓ Test image created: test_child.png')
"
    
    # Test upload - FIXED curl command
    echo "Testing upload:"
    curl -X POST -F "image=@test_child.png" http://localhost:8000/api/upload
    echo ""
    
else
    echo "✗ Backend is NOT running on port 8000"
    echo "Try running: uvicorn main:app --reload --host 0.0.0.0 --port 8000"
fi

echo "=============================="
