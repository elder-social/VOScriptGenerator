from flask import Flask, render_template, request, send_file
from flask_cors import CORS
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.shared import Inches
import io

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Route to serve the HTML file
@app.route('/')
def home():
    return render_template('index.html')  # Renders the index.html from the templates folder

# API endpoint to generate Word file
@app.route('/generate', methods=['POST'])
def generate_file():
    try:
        # Get the text from the POST request
        data = request.json  # Expecting JSON data
        print("Received data:", data)  # Log incoming data (debugging)

        # Safely get 'text' from the data
        text = data.get('text', '').strip()  # Use .get() to avoid KeyError
        if not text:
            return {"error": "No text provided"}, 400  # Return error if text is empty

        # Split the text into paragraphs
        paragraphs = text.split('\n')

        # Create a Word document
        document = Document()

        # Set the document orientation to landscape
        section = document.sections[0]
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = Inches(11.69)  # A4 landscape width
        section.page_height = Inches(8.27)  # A4 landscape height

        # Set up the table with 3 columns
        table = document.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'VO No'
        hdr_cells[1].text = 'VO Script'
        hdr_cells[2].text = 'Visuals/Edit Notes'

        # Adjust column widths
        widths = [Inches(1), Inches(5.345), Inches(5.345)]  # Adjust for landscape
        for i, cell in enumerate(hdr_cells):
            cell.width = widths[i]

        # Populate the table
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():  # Skip empty lines
                row_cells = table.add_row().cells
                row_cells[0].text = f"VO{i+1}"  # VO numbering
                row_cells[1].text = paragraph
                row_cells[2].text = ''  # Leave Visuals/Edit Notes blank

        # Adjust column widths for all rows
        for row in table.rows:
            for i, cell in enumerate(row.cells):
                cell.width = widths[i]

        # Save the document to memory
        doc_stream = io.BytesIO()
        document.save(doc_stream)
        doc_stream.seek(0)

        # Return the file to the user
        return send_file(
            doc_stream,
            as_attachment=True,
            download_name="generated_file.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        print("Error occurred:", e)  # Log any errors for debugging
        return {"error": str(e)}, 500  # Return any error that occurs

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
