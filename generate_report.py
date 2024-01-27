import csv
import pdfkit
import pickle
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

def read_logs_from_csv(csv_path):
    logs = []
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            logs.append(row)
    return logs

def generate_pdf(logs, output_path='log_report.pdf', template_path='template.html'):
    try:
        # Load the HTML template
        with open(template_path, 'r') as template_file:
            template_content = template_file.read()

        # Replace the [AnomaliesPlaceholder] with the actual data
        anomalies_html = ''
        for log in logs:
            anomalies_html += f"""
            <tr class="highlight">
                <td>{log.get('IP Address', '')}</td>
                <td>{log.get('Time Stamp', '')}</td>
                <td class="requested-file-path">{log.get('Requested File Path', '')}</td>
                <td>{log.get('Status Code', '')}</td>
                <td>{log.get('Anomaly Type', '')}</td>
            </tr>
            """

        # Replace the [AnomaliesPlaceholder] in the template
        template_content = template_content.replace('[AnomaliesPlaceholder]', anomalies_html)

        # Configure options for PDF generation
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': 'UTF-8',
        }

        # Generate PDF from HTML content
        pdfkit.from_string(template_content, output_path, options=options)

        print(f"PDF generated successfully: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")

def analyze_logs(csv_file):
    anomalies = []

    with open(csv_file, 'r') as csv_input:
        csv_reader = csv.DictReader(csv_input)

        for row in csv_reader:
            AnomalyType = row.get('Prediction', "Valid Request")

            # Example anomaly detection: if Anomaly type is not Valid, then collect the anomalous logs information
            if AnomalyType != "Valid Request":
                anomalies.append(row)

    return anomalies

def send_email(html_content, subject):
    # Your email configuration goes here
    sender_email = 'rimjhimagarwal21@gmail.com'
    sender_password = 'lkch squl mpek mrdk'
    receiver_email = 'rimjhimagarwal21@gmail.com'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(html_content, 'html'))

    server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())

def should_generate_email():
    global last_email_timestamp

    current_timestamp = time.time()
    elapsed_time = current_timestamp - last_email_timestamp

    # Only generate an email if 5 minutes have passed
    return elapsed_time >= 300

def main():
    csv_path = 'result.csv'  # Replace with the actual path to your CSV file
    logs = read_logs_from_csv(csv_path)

    # Generate PDF with logs using HTML template
    generate_pdf(logs, output_path='anomaly_detection_report.pdf', template_path='template.html')

    anomalies = analyze_logs(csv_path)
    if should_generate_email():
        if anomalies:
            generate_email(anomalies)

if __name__ == "__main__":
    last_email_timestamp = 0
    main()
