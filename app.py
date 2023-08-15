from flask import Flask, render_template, request
import boto3
import openai
import subprocess

app = Flask(__name__)

# Set your OpenAI API key
openai.api_key = "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"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["file"]

        if uploaded_file.filename != "":
            # Amazon Textract code
            with open(uploaded_file.filename, 'rb') as document:
                imageBytes = bytearray(document.read())
            textract = boto3.client('textract')
            response = textract.detect_document_text(Document={'Bytes': imageBytes})
            ocr_generated_text = ""
            for item in response["Blocks"]:
                if item["BlockType"] == "LINE":
                    ocr_generated_text += item["Text"] + "\n"

            # OpenAI GPT-3 code
            example_text="Invoicing Street Address Template.com City , ST ZIP Code BILL TO Name Address City , State ZIP Country Phone Email pp1 pp2 Pp3 P.O. # # / Taxable NOTES : Your Company Name looooo0000 ロ Phone Number , Web Address , etc. Sales Rep . Name Ship Date Description test item 1 for online invoicing test item 2 for onvoice invoicing template This template connects to an online SQL Server SHIP TO Name Address City , State ZIP Country Contact Ship Via Quantity 1 2 3 PST GST INVOICE THANK YOU FOR YOUR BUSINESS ! DATE : INVOICE # : Client # Terms Unit Price 3.00 4.00 5.50 SUBTOTAL 8.000 % 6.000 % SHIPPING & HANDLING TOTAL PAID TOTAL DUE Due Date Line Total 3.00 8.00 16.50 27.50 27.50 27.50"
            system_role = "Extract entities and values as a key-value pair from the text provided"
            example_entities = """
            Company Name: Your Company Name 
            Phone Number: looooo0000 
            Web Address: Template.com 
            Ship To Name: 
            Address: 
            City: 
            State: 
            Zip Code: 
            Country: 
            Contact:  
            Quantity: 1 
            Quantity: 2 
            Quantity: 3  
            Unit Price: 3.00 
            Unit Price: 4.00 
            Unit Price: 5.50 
            Subtotal: 8.00 
            Taxable: 
            Line Total: 3.00 
            Subtotal: 8.00 
            Shipping & Handling: 6.00 
            Total Paid: 27.50
            Total Due: 27.50"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": example_text},
            {"role": "assistant", "content": example_entities},
            {"role": "user", "content": ocr_generated_text}
    ],
                temperature=0.2
            )

            extracted_entities = response["choices"][0]["message"]["content"]
            improved_output = ""
            for line in extracted_entities.split("\n"):
                key_value = line.split(":", 1)
                if len(key_value) == 2:
                    key, value = key_value
                    improved_output += f"{key.strip()}: {value.strip()}\n"
                else:
                    improved_output += f"{line.strip()}\n"

            return render_template("index.html", ocr_generated_text=ocr_generated_text, extracted_entities=improved_output)

    return render_template("index.html", ocr_generated_text=None, extracted_entities=None)

if __name__ == "__main__":
    app.run(debug=True)
