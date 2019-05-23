import os
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename
from call_bert import rankSimilarity


UPLOAD_FOLDER = './test_uploads'
ALLOWED_EXTENSIONS = set(['csv', 'txt'])


app = Flask(__name__)

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/')
# def home():
# 	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/hi', methods=['PUT'])
def salvador():
	name = request.get_json()['name']
	return 'Hello, {name}'.format(name=name)


@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			flash('File(s) successfully uploaded')
			return redirect('/')

@app.route('/match', methods=['PUT'])
def get_match():
	input_str = request.get_json()['input']
	top_n = request.get_json()['top_n']

	match_result = rankSimilarity(input_str, top_n)
	return jsonify(match_result)


if __name__ == "__main__":
	app.run()