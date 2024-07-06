from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import re

app = Flask(__name__)
CORS(app)

# Define the credit points for each subject
CREDIT_POINTS = {
    "21CS51": 3,
    "21CSL581": 1,
    "21CS52": 4,
    "21CS53": 3,
    "21CS54": 3,
    "21CSL55": 1,
    "21RMI56": 2,
    "21CIV57": 1
}

# Function to convert total marks to grade points


def marks_to_grade_points(marks):
    if marks >= 90:
        return 10
    elif marks >= 80:
        return 9
    elif marks >= 70:
        return 8
    elif marks >= 60:
        return 7
    elif marks >= 50:
        return 6
    elif marks >= 40:
        return 5
    else:
        return 0

# Function to extract subject details from text


def extract_subject_details(text):
    subjects = []
    pattern = re.compile(
        r"(\d{2}[A-Z]{2,}[0-9]{2,})\s+([\w\s&;,-]+?)(?:\s{2,}|\n)(\d{2,3})\s+(\d{2,3})\s+(\d{2,3})\s+[PFAW]+")
    matches = pattern.findall(text)
    for match in matches:
        code, name, internal, external, total = match
        subjects.append({
            "Subject Code": code,
            "Subject Name": ' '.join(name.split()),
            "Total Marks": int(total)
        })
    return subjects

# Function to extract student details from text


def extract_student_details(text):
    name_pattern = re.compile(r"Student Name\s*:\s*(.*)")
    usn_pattern = re.compile(r"University Seat Number\s*:\s*(\S+)")
    semester_pattern = re.compile(r"Semester\s*:\s*(\d+)")

    name_match = name_pattern.search(text)
    usn_match = usn_pattern.search(text)
    semester_match = semester_pattern.search(text)

    name = name_match.group(1) if name_match else "Unknown"
    usn = usn_match.group(1) if usn_match else "Unknown"
    semester = semester_match.group(1) if semester_match else "Unknown"

    return name, usn, semester


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        pdf_path = "/tmp/" + file.filename
        file.save(pdf_path)

        document = fitz.open(pdf_path)
        text = ""

        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()

        student_name, student_usn, student_semester = extract_student_details(
            text)
        subject_details = extract_subject_details(text)

        total_credit_points = 0
        total_credits = 0

        for subject in subject_details:
            code = subject['Subject Code']
            total_marks = subject['Total Marks']
            credits = CREDIT_POINTS.get(code, 0)
            grade_points = marks_to_grade_points(total_marks)
            total_credit_points += grade_points * credits
            total_credits += credits

        sgpa = total_credit_points / total_credits if total_credits > 0 else 0

        result = {
            "name": student_name,
            "usn": student_usn,
            "semester": student_semester,
            "sgpa": sgpa,
            "subjects": subject_details
        }

        return jsonify(result)

    return jsonify({"error": "File processing error"}), 500


if __name__ == '__main__':
    app.run(debug=True)
