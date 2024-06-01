import os
import json
from collections import defaultdict
import re

# Path to the images folder
# images_dir = 'shuffle_residual'
# images_dir = 'add3_remove_8'
# images_dir = 'modp_models_corr'
# images_dir = 'modp_models_dot'
# images_dir = 'add3_dot'
# images_dir = 'add3_corr'

# dirs =  ['add3_dot', 'add3_corr', 'modp_corr', 'modp_dot', 'paridy_corr', 'paridy_dot']
dirs =  ['add3_remove_8']

vistype = 'Self-Cosine-Similarity Matrices'
for images_dir in dirs:

    # Output HTML file
    output_file = f'{images_dir}.html'

    # Get list of image files including SVG
    image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f)) and f.lower().endswith('.svg')]

    # Group images by model
    from collections import OrderedDict
    images_by_model = defaultdict(list)
    for file in image_files:
        model_name = file[::]
        # model_name = model_name.replace('_shuffle_', 'SMILE')
        # model_name = model_name.replace('shuffle', 's')
        # model_name = model_name.replace('SMILE', '_shuffle_')

        # model_name = model_name.replace('_remove_', 'SMILE')
        # model_name = model_name.replace('remove', 'r')
        # model_name = model_name.replace('SMILE', '_remove_')
        model_name = '_'.join(model_name.split('_')[:-3])  # Extracting model name part (assumed to be second part of filename)
        
        # timestamp = re.search(r'_T(\d+)', file).group(0)
        # model_name = model_name.replace('trained', '').replace('untrained', '')
        print(model_name)
        images_by_model[model_name].append(file)

    # Sort images by model name

    images_by_model = OrderedDict(sorted(images_by_model.items(), key=lambda x: x[0]))
    print('number of models:', len(images_by_model))

    new_images_by_model = OrderedDict()
    n_layers = 6
    for model_name in images_by_model:
        files = sorted(images_by_model[model_name])[::-1]
        accs = ' -> '.join([re.search(r'acc=(\d+)', file).group(1) for file in files])
        # accs = '\t Accuracy Transition: ' + accs
        # model_name = f'{{{model_name}}}' + accs
        # type_num = 1
        # if 'pm' in model_name:
        #     type_num += 1
        # if 'shuffle' in model_name:
        #     type_num += 1
        # if 'remove' in model_name:
        #     type_num += 1
        # model_name = f'Model Type {type_num}:\t' + model_name
        result_path = model_name
        residual_mode = ''
        if 'shuffle' in result_path:
            residual_mode = 'Shuffle first N'
        elif 'remove' in result_path:
            residual_mode = 'Removing residual connections in the first N positions'
        elif 'pm' in result_path:
            residual_mode = 'Sum all to one'
        else:
            residual_mode = 'Remove all'
        
        pe_type = 'NoPE' if 'nope' in result_path \
            else 'Sin' if 'sin' in result_path \
            else 'Original'

        if residual_mode == 'Remove all':
            if 'res=' not in result_path:
                missing_rc_str = '{}'
            else: # get the layers without residual connections
                pattern = r"res=\[(.*?)\]"
                residual_list = re.findall(pattern, result_path)[0]
                residual_list = [int(num) for num in residual_list.split(", ")] if residual_list!='' else []
                missing_rc = [i for i in range(n_layers) if i not in residual_list]
                missing_rc_str = '{' + ','.join([str(i) for i in missing_rc])+ '}'
        else:
            
            pattern = r'(?<=pm)(.*?)(?=/|$)'
            match = re.search(pattern, result_path)
            if match:
                removal_str = match.group(1)
            else:
                print('No match found')
                print(result_path)

            pattern = r'(?<=remove_)(.*?)_'
            match = re.search(pattern, result_path)
            if match:
                N = match.group(1)
            else:
                print('No match found')
                print(result_path)

            if residual_mode == 'Shuffle first N':
                removal_str = removal_str.replace('shuffle', '1')
                residual_mode = residual_mode.replace('N', N)
            elif residual_mode == 'Removing residual connections in the first N positions':
                removal_str = removal_str.replace('remove', '1')
                residual_mode = residual_mode.replace('N', N)
            else:
                removal_str = ''.join(['1' if str(rs) in removal_str else '0' for rs in range(n_layers) ])
            removal_list = [num for num in range(n_layers) if removal_str[num]=='1']
            missing_rc_str = '{' + ','.join([str(i) for i in removal_list])+ '}'                     
        has_lwp = 'Yes' if 'lwp' in result_path and pe_type!='NoPE' else 'No'
        seed = re.search(r"sd(\d+)", result_path).group(1)

        model_name =       \
    f'''
    Type:        "{pe_type}" + "{residual_mode}"
    Layerwise PE:       {has_lwp} 
    Layers Affected:        {missing_rc_str}    
    Accuracy Transition: {accs}
    Seed: {seed}
    '''

    #     model_name = \
    # f'''
    # PE Type:        "{pe_type}"
    # Layers Without RC:        {missing_rc_str}    
    # Accuracy (Init->Trained): {accs}
    # Seed: {seed}
    # '''
        # print(model_name)
        new_images_by_model[model_name] = sorted(files)[::-1]

    from functools import reduce
    def determine_order(model_name):
        # get number insider { }
        pattern = r'(?<={)(.*?)(?=})'
        match = re.search(pattern, model_name)
        if match:
            match_str = match.group(1)
            n_list = match.group(1).split(',')
        # n_list += [0] * (n_layers - len(n_list))
        # quantity = reduce(lambda x, y: x*10 + y, [int(n) for n in n_list][::-1])
        quantity = sum([int(n) for n in n_list])+1 if len(n_list) and len(n_list[0]) else 0
        quantity += len(n_list) *100
        # to binary
        print(n_list, quantity)
        return quantity

    new_images_by_model = OrderedDict(sorted(new_images_by_model.items(), key=lambda x: determine_order(x[0]))) 

    for k in new_images_by_model:
        print(k)


    print('number of models:', len(new_images_by_model))

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
                        img.src = '%s/' + file;
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
    """ % (json.dumps(images_by_model), images_dir)
    # json.dumps(images_by_model), images_dir)
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
                white-space: pre-wrap; /* Allows multiline titles */
            }}
            .row {{
                display: flex;
                flex-wrap: nowrap; /* Prevents images from wrapping onto multiple lines */
                gap: 5px; /* Reduced gap between images */
                overflow-x: auto; /* Adds horizontal scrollbar if needed */
            }}
            .row img {{
                max-width: 1600px; /* Ensures images scale down if necessary */
                height: auto;
                flex-shrink: 0; /* Prevents images from shrinking */
            }}
        </style>
    </head>
    <body>
        <h1>{vistype}</h1>
        <div id="gallery"></div>
        {script_content}
    </body>
    </html>
    """
        # <h1>Model Image Gallery</h1>


    # Write the HTML content to the output file
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f'{output_file} has been generated with the image list.')