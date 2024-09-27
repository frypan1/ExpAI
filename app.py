from flask import Flask, render_template, request, redirect, url_for
import openai
import os
from werkzeug.utils import secure_filename
from ocr import process_image
from db_manipulation import *

# Initialize Flask app
app = Flask(__name__)

# Set your OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

UPLOAD_FOLDER = 'static/uploads' 
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_invoice_details(invoice_text):
    """
    Extract relevant information from the invoice text using OpenAI API.
    """
    try:
        prompt = f"""
        Extract the following details from the invoice:
        1. Date of purchase
        2. Category (like groceries, entertainment, dining, etc.)
        3. Amount spent
        4. Product or service name

        Invoice text:
        {invoice_text}

        Return the details in the following format (one entry per line):
        Date: YYYY-MM-DD, Category: <category>, Amount: <numeric_amount>, Product Name: <product_name>.
        Only return the numeric value for the amount without currency symbols.
        """

        # Ensure that both 'model' and 'prompt' are passed
        response = openai.completions.create(
            model="gpt-3.5-turbo-instruct",  # Specify the model
            prompt=prompt,
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error extracting invoice details: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No File Part', 400
    
    file = request.files['image']
    
    if file.filename == '':
        return 'No Selected file', 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        extracted_text = process_image(file_path)
        return redirect(url_for('extract', invoice_text=extracted_text))

@app.route('/extract', methods=['GET'])
def extract():
    invoice_text = request.args.get('invoice_text')
    extracted_details_text = extract_invoice_details(invoice_text)
    if extracted_details_text:
        return render_template('review.html', extracted_details=extracted_details_text)
    else:
        return redirect(url_for('index'))

@app.route('/confirm', methods=['POST'])
def confirm():
    # Extract and parse the invoice details again
    details_text = request.form['extracted_details']
    expense_details_list = []
    
    for part in details_text.splitlines():
        if part.strip():  # Ensure it's not an empty line
            details = {}
            for item in part.split(", "):
                key, value = item.split(": ")
                details[key.strip()] = value.strip()
            expense_details_list.append(details)
    
    insert_into_database(expense_details_list)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
