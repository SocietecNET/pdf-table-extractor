from flask import Flask, request, jsonify
import camelot
import os
import uuid
import base64

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
