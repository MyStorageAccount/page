import os
import json
from collections import defaultdict
import re

# Path to the images folder
images_dir = 'shuffle_residual'
# Output HTML file
output_file = 'index.html'

# Get list of image files including SVG
image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f)) and f.lower().endswith('.svg')]

# Group images by model
images_by_model = defaultdict(list)
for file in image_files:
    model_name = file[::]
    model_name = model_name.replace('_shuffle_', 'SMILE')
    model_name = model_name.replace('shuffle', 's')
    model_name = model_name.replace('SMILE', '_shuffle_')
    model_name = '_'.join(model_name.split('_')[:-3])  # Extracting model name part (assumed to be second part of filename)
    
    timestamp = re.search(r'_T(\d+)', file).group(0)
    model_name = model_name.replace(timestamp, '')

    images_by_model[model_name].append(file)


new_images_by_model = {}
for model_name in images_by_model:
    files = images_by_model[model_name]
    accs = '-'.join([re.search(r'acc=(\d+)', file).group(1) for file in files])
    accs = '\t Accuracy Transition: ' + accs
    model_name = f'{{{model_name}}}' + accs
    type_num = 1
    if 'pm' in model_name:
        type_num += 1
    if 'shuffle' in model_name:
        type_num += 1
    model_name = f'Model Type {type_num}:\t' + model_name

    new_images_by_model[model_name] = files
images_by_model = new_images_by_model
# Generate JavaScript array from image files list
script_content = """
<script>
    function loadImages() {
        const gallery = document.getElementById('gallery');
        const imagesByModel = %s;
        for (const model in imagesByModel) {
            if (imagesByModel.hasOwnProperty(model)) {
                const section = document.createElement('section');
                const title = document.createElement('h2');
                title.textContent = model;
                section.appendChild(title);
                const row = document.createElement('div');
                row.classList.add('row');
                imagesByModel[model].forEach(file => {
                    const img = document.createElement('img');
                    img.src = 'shuffle_residual/' + file;
                    img.alt = file;
                    row.appendChild(img);
                });
                section.appendChild(row);
                gallery.appendChild(section);
            }
        }
    }
    document.addEventListener('DOMContentLoaded', loadImages);
</script>
""" % json.dumps(images_by_model)

# HTML content
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Model Image Gallery</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 5px;
        }}
        section {{
            margin-bottom: 5px;
        }}
        h2 {{
            margin-bottom: 5px;
        }}
        .row {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .row img {{
            max-width: 1600px;
            height: auto;
            margin-right: 5px;
        }}
    </style>
</head>
<body>
    <h1>Model Image Gallery</h1>
    <div id="gallery"></div>
    {script_content}
</body>
</html>
"""

# Write the HTML content to the output file
with open(output_file, 'w') as f:
    f.write(html_content)

print(f'{output_file} has been generated with the image list.')