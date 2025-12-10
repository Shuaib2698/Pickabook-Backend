# create_template.py
from PIL import Image, ImageDraw
import os

# Ensure the templates directory exists
os.makedirs('templates', exist_ok=True)

img = Image.new('RGB', (1024, 1024), color='white')
draw = ImageDraw.Draw(img)
draw.rectangle([200, 200, 824, 824], outline='blue', width=5)
draw.text((412, 900), 'Personalized Storybook', fill='black')
img.save('templates/storybook_template.png')
print('Template created successfully.')