from flask import Flask, request, jsonify
import camelot
import os
import uuid
import base64
import pymupdf4llm
import tempfile
import fitz
from helpers.facedection import get_faces
from helpers.svg import get_images_from_svg

app = Flask(__name__)

API_KEY = os.getenv('EXTRACT_TABLES_KEY')

def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized access'}), 403
    decorated_function.__name__ = view_function.__name__
    return decorated_function

def process_pdf(filename, pages):
    html_filename = os.path.join('./tmp', f'{uuid.uuid4()}.html')
    csv_filename = os.path.join('./tmp', f'{uuid.uuid4()}.csv')

    tables = camelot.read_pdf(filename, pages=pages)
    result = []

    for table in tables:
        json_table = table.df.to_json(orient='split')
        table.to_csv(csv_filename, index=False, header=False)
        csv_content = open(csv_filename, 'r').read()
        table.df = table.df.map(lambda x: x.replace('\n', "\r\n") if isinstance(x, str) else x)
        table.to_html(html_filename, index=False, header=False)
        html_content = open(html_filename, 'r').read()
        open(html_filename, 'w').write(html_content.replace("\\r\\n", '<br>'))
        html_content = open(html_filename, 'r').read()
        result.append(dict(
            parsing_report=table.parsing_report,
            bbox=table._bbox,
            raw=json_table,
            csv=csv_content,
            html=html_content
        ))

    for filename in [filename, csv_filename, html_filename]:
        try:
            os.remove(filename)
        except:
            pass

    return result

@app.route('/extract_tables', methods=['POST'])
@require_api_key
def extract_table():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file:
        file_id = str(uuid.uuid4())
        filename = os.path.join('./uploads', f'{file_id}.pdf')
        file.save(filename)

        pages = request.form.get('pages', '1')
        result = process_pdf(filename, pages)

        return jsonify(result), 200

@app.route('/extract_tables_base64', methods=['POST'])
@require_api_key
def extract_table_base64():
    data = request.get_json()
    if 'file' not in data or 'pages' not in data:
        return jsonify({'error': 'Invalid request, "file" and "pages" are required'}), 400
    
    try:
        pdf_content = base64.b64decode(data['file'])
    except Exception as e:
        return jsonify({'error': f'Invalid base64 data: {str(e)}'}), 400
    
    file_id = str(uuid.uuid4())
    filename = os.path.join('./uploads', f'{file_id}.pdf')
    with open(filename, 'wb') as f:
        f.write(pdf_content)

    pages = data['pages']
    result = process_pdf(filename, pages)

    return jsonify(result), 200

@app.route('/convert_pdf_to_markdown', methods=['POST'])
@require_api_key
def pdf2markdown():
    try:
        # Get the base64 encoded PDF string from the request
        pdf_base64 = request.json.get('pdf_base64', None)        
        if not pdf_base64:
            return jsonify({'error': 'No PDF data provided'}), 400

        # Decode the base64 PDF string
        pdf_bytes = base64.b64decode(pdf_base64)

        # Create a temporary file to store the decoded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
        
        # Convert the PDF to markdown using the temp file path
        md_text = pymupdf4llm.to_markdown(temp_pdf_path, margins=0, )

        # Remove the temporary file
        os.remove(temp_pdf_path)

        # Return the markdown text
        return jsonify({'markdown': md_text})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/convert_pdf_to_svg', methods=['POST'])
@require_api_key
def convert_pdf_to_svgs():
    data = request.json
    base64_pdf = data.get('pdf_base64')
    if not base64_pdf:
        return jsonify({"error": "No PDF data provided"}), 400
    try:
        pdf_data = base64.b64decode(base64_pdf)
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        svg_list = []
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            svg = page.get_svg_image()
            svg_list.append(svg)
        return jsonify({"svg": svg_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
@app.route('/convert_pdf_to_html', methods=['POST'])
@require_api_key
def convert_pdf_to_htmls():
    data = request.json
    base64_pdf = data.get('pdf_base64')
    if not base64_pdf:
        return jsonify({"error": "No PDF data provided"}), 400
    try:
        pdf_data = base64.b64decode(base64_pdf)
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        html_list = []
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            html = page.get_text("html")
            html_list.append(html)
        return jsonify({"html": html_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/extract_pdf_images', methods=['POST'])
@require_api_key
def extract_pdf_images():
    data = request.json
    base64_pdf = data.get('pdf_base64')
    if not base64_pdf:
        return jsonify({"error": "No PDF data provided"}), 400
    try:
        pdf_data = base64.b64decode(base64_pdf)
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        base64image_list = []
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            svg_content = page.get_svg_image()
            for base64image in get_images_from_svg(svg_content):
                base64image_list.append(base64image.replace("\r\n", ""))
        # check for faces
        image_list = []
        for base64image in base64image_list:
            is_photo = len(get_faces(base64image)) > 0
            image_list.append(dict(image=base64image, is_photo=is_photo))
        return jsonify({"images": image_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500    


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
