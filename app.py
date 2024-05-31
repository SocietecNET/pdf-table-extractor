from flask import Flask, request, jsonify
import camelot
import os
import uuid

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')

def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        if request.headers.get('x-api-key') and request.headers.get('x-api-key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized access'}), 403
    decorated_function.__name__ = view_function.__name__
    return decorated_function

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

        html_filename = os.path.join('./tmp', f'{file_id}.html')
        csv_filename = os.path.join('./tmp', f'{file_id}.csv')

        pages = request.form.get('pages', '1')
        tables = camelot.read_pdf(filename, pages=pages)

        result = []
        for table in tables:
            # json
            json_table = table.df.to_json(orient='split')
            # csv
            table.to_csv(csv_filename, index=False, header=False)
            csv_content = open(csv_filename, 'r').read()
            # html
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
        # clean up
        for filename in [filename, csv_filename, html_filename]:
            try:
                os.remove(filename)
            except:
                pass

        return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
