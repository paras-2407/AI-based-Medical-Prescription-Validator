# import streamlit as st
# import pytesseract
# from PIL import Image
# import re
# import json
# import requests
# import io

# # ---- OCR and Parsing Logic ----
# def extract_text_from_image(image):
#     try:
#         text = pytesseract.image_to_string(image)
#         return text
#     except Exception as e:
#         return f"Error extracting text: {e}"

# def parse_prescription(text):
#     result = {
#         "hospital": None, "date": None, "doctor": None,
#         "patient_name": None, "age": None, "complaint": None, "medications": [], "signature": None
#     }

#     lines = [line.strip() for line in text.split('\n') if line.strip()]
#     if lines:
#         result["hospital"] = lines[0]

#     date_match = re.search(r'Date:?\s*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
#     if date_match: result["date"] = date_match.group(1)

#     doctor_match = re.search(r'Dr\.\s+([^\n]+)', text)
#     if doctor_match: result["doctor"] = doctor_match.group(0)

#     patient_match = re.search(r'Patient\s*Name:?\s*([^\n]+)', text, re.IGNORECASE)
#     if patient_match: result["patient_name"] = patient_match.group(1).strip()

#     age_match = re.search(r'Age:?\s*(\d+)', text, re.IGNORECASE)
#     if age_match: result["age"] = int(age_match.group(1))

#     complaint_match = re.search(r'Complaint:?\s*([^\n]+)', text, re.IGNORECASE)
#     if complaint_match: result["complaint"] = complaint_match.group(1).strip()

#     med_blocks = []
#     current_block = []
#     capturing = False

#     for line in lines:
#         if re.search(r'prescription|medications|syrup|tablet', line, re.IGNORECASE) and not capturing:
#             capturing = True
#             continue
#         if capturing:
#             if re.match(r'^\d+\.', line) or re.match(r'^(Syrup|Tab\.?|Tablet|Cap\.?|Capsule)', line, re.IGNORECASE):
#                 if current_block: med_blocks.append('\n'.join(current_block))
#                 current_block = [line]
#             elif current_block:
#                 current_block.append(line)
#             if re.search(r'signature|follow.up|advice', line, re.IGNORECASE):
#                 if current_block: med_blocks.append('\n'.join(current_block))
#                 capturing = False
#                 break
#     if capturing and current_block:
#         med_blocks.append('\n'.join(current_block))

#     for block in med_blocks:
#         med = {"name": None, "form": None, "strength": None, "frequency": None, "timing": None, "duration": None}
#         name_form_match = re.search(r'(Syrup|Tab\.?|Tablet|Cap\.?|Capsule)\s+([A-Za-z0-9]+)', block, re.IGNORECASE)
#         if name_form_match:
#             med["form"] = name_form_match.group(1).strip()
#             med["name"] = name_form_match.group(2).strip()
#         strength_match = re.search(r'(\d+mg\/\d+ml|\d+mg)', block)
#         if strength_match: med["strength"] = strength_match.group(1)
#         for pattern in [r'(once|twice|thrice|three times|four times|[\d]+ times)\s+a\s+day', r'(OD|BD|TDS|QID)']:
#             freq_match = re.search(pattern, block, re.IGNORECASE)
#             if freq_match:
#                 freq = freq_match.group(1)
#                 med["frequency"] = {
#                     "OD": "Once a day", "BD": "Twice a day", 
#                     "TDS": "Thrice a day", "QID": "Four times a day"
#                 }.get(freq.upper(), freq.title() + " a day")
#                 break
#         for pattern in [r'(before|after|with)\s+food', r'(morning|afternoon|evening|night)']:
#             timing_match = re.search(pattern, block, re.IGNORECASE)
#             if timing_match:
#                 med["timing"] = timing_match.group(0).title()
#                 break
#         duration_match = re.search(r'for\s+(\d+)\s+(days|weeks)', block, re.IGNORECASE)
#         if duration_match:
#             med["duration"] = f"{duration_match.group(1)} {duration_match.group(2)}"
#         if med["name"]:
#             result["medications"].append(med)

#     signature_match = re.search(r'Signature:?\s*([^\n]+)', text, re.IGNORECASE)
#     result["signature"] = signature_match.group(1).strip() if signature_match else result.get("doctor")
#     return result

# def clean_json_data(data):
#     if data["hospital"] and len(data["hospital"]) > 50:
#         data["hospital"] = data["hospital"].split('\n')[0]
#     for med in data["medications"]:
#         if med["form"]:
#             if re.search(r'tab', med["form"], re.IGNORECASE): med["form"] = "Tablet"
#             elif re.search(r'cap', med["form"], re.IGNORECASE): med["form"] = "Capsule"
#             elif re.search(r'syr', med["form"], re.IGNORECASE): med["form"] = "Syrup"
#     return data

# # ---- Streamlit UI ----
# st.set_page_config(page_title="Prescription JSON & API", layout="wide")
# st.title("🧾 Prescription Parser + API Caller")
# st.markdown("Upload a scanned prescription image. We'll extract, parse, and call an API using the structured data.")

# uploaded_file = st.file_uploader("📤 Upload Prescription Image", type=["png", "jpg", "jpeg"])

# if uploaded_file:
#     st.image(uploaded_file, caption="Uploaded Prescription", use_column_width=True)
#     img = Image.open(uploaded_file)

#     with st.spinner("Extracting text from image..."):
#         text = extract_text_from_image(img)
    
#     if text.startswith("Error"):
#         st.error(text)
#     else:
#         st.success("Text extracted successfully.")
#         st.subheader("📄 Extracted Text")
#         st.text_area("Raw OCR Text", text, height=150)

#         with st.spinner("Parsing prescription..."):
#             json_data = clean_json_data(parse_prescription(text))
#             json_str = json.dumps(json_data, indent=2)

#         st.subheader("🧬 Parsed JSON")
#         st.json(json_data)

#         # Optional: Save JSON
#         st.download_button("💾 Download JSON", json_str, file_name="parsed_prescription.json", mime="application/json")

#         # ---- Call API with this JSON ----
#         st.subheader("🚀 Send to API")
#         api_url = st.text_input("API Endpoint URL", placeholder="https://your-api-url.com/process")

#         if st.button("Send to API"):
#             if not api_url:
#                 st.error("Please enter an API URL.")
#             else:
#                 try:
#                     with st.spinner("Sending request..."):
#                         response = requests.post(api_url, json=json_data)
#                         if response.status_code == 200:
#                             st.success("API call successful!")
#                             try:
#                                 st.json(response.json())
#                             except:
#                                 st.text(response.text)
#                         else:
#                             st.error(f"API call failed. Status code: {response.status_code}")
#                             st.text(response.text)
#                 except Exception as e:
#                     st.error(f"Error while calling API: {str(e)}")



import streamlit as st
import pytesseract
from PIL import Image
import re
import json
import requests
import tempfile

# ------------------ Core OCR & Parsing Functions ------------------ #

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

def parse_prescription(text):
    result = {
        "hospital": None,
        "date": None,
        "doctor": None,
        "patient_name": None,
        "age": None,
        "complaint": None,
        "medications": [],
        "signature": None
    }
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    if lines:
        result["hospital"] = lines[0]

    date_match = re.search(r'Date:?\s*(\d{1,2}/\d{1,2}/\d{4})', text, re.IGNORECASE)
    if date_match:
        result["date"] = date_match.group(1)

    doctor_match = re.search(r'Dr\.\s+([^\n]+)', text)
    if doctor_match:
        result["doctor"] = doctor_match.group(0)

    patient_match = re.search(r'Patient\s*Name:?\s*([^\n]+)', text, re.IGNORECASE)
    if patient_match:
        result["patient_name"] = patient_match.group(1).strip()

    age_match = re.search(r'Age:?\s*(\d+)', text, re.IGNORECASE)
    if age_match:
        result["age"] = int(age_match.group(1))


    complaint_match = re.search(r'Complaint:?\s*([^\n]+)', text, re.IGNORECASE)
    if complaint_match: result["complaint"] = complaint_match.group(1).strip()

    med_blocks = []
    current_block = []
    capturing = False

    for i, line in enumerate(lines):
        if re.search(r'prescription|medications|syrup|tablet', line, re.IGNORECASE) and not capturing:
            capturing = True
            continue

        if capturing:
            if (re.match(r'^\d+\.', line) or re.match(r'^(Syrup|Tab\.?|Tablet|Cap\.?|Capsule)', line, re.IGNORECASE)):
                if current_block:
                    med_blocks.append('\n'.join(current_block))
                current_block = [line]
            elif current_block:
                current_block.append(line)

            if re.search(r'signature|follow.up|advice', line, re.IGNORECASE):
                if current_block:
                    med_blocks.append('\n'.join(current_block))
                capturing = False
                break

    if capturing and current_block:
        med_blocks.append('\n'.join(current_block))

    for block in med_blocks:
        med = {
            "name": None,
            "form": None,
            "strength": None,
            "frequency": None,
            "timing": None,
            "duration": None
        }

        name_form_match = re.search(r'(Syrup|Tab\.?|Tablet|Cap\.?|Capsule)\s+([A-Za-z0-9]+)', block, re.IGNORECASE)
        if name_form_match:
            med["form"] = name_form_match.group(1).strip()
            med["name"] = name_form_match.group(2).strip()

        strength_match = re.search(r'(\d+mg\/\d+ml|\d+mg)', block)
        if strength_match:
            med["strength"] = strength_match.group(1)

        freq_patterns = [r'(once|twice|thrice|three times|four times|[\d]+ times)\s+a\s+day', r'(OD|BD|TDS|QID)']
        for pattern in freq_patterns:
            freq_match = re.search(pattern, block, re.IGNORECASE)
            if freq_match:
                freq = freq_match.group(1)
                med["frequency"] = {
                    "OD": "Once a day", "BD": "Twice a day", "TDS": "Thrice a day", "QID": "Four times a day"
                }.get(freq.upper(), freq.title() + " a day")
                break

        timing_patterns = [r'(before|after|with)\s+food', r'(morning|afternoon|evening|night)']
        for pattern in timing_patterns:
            timing_match = re.search(pattern, block, re.IGNORECASE)
            if timing_match:
                med["timing"] = timing_match.group(0).title()
                break

        duration_match = re.search(r'for\s+(\d+)\s+(days|weeks)', block, re.IGNORECASE)
        if duration_match:
            med["duration"] = f"{duration_match.group(1)} {duration_match.group(2).lower()}"

        if med["name"]:
            result["medications"].append(med)

    signature_match = re.search(r'Signature:?\s*([^\n]+)', text, re.IGNORECASE)
    if signature_match:
        result["signature"] = signature_match.group(1).strip()
    elif doctor_match:
        result["signature"] = doctor_match.group(0)

    return result

def clean_json_data(data):
    if data["hospital"] and len(data["hospital"]) > 50:
        data["hospital"] = data["hospital"].split('\n')[0]

    for med in data["medications"]:
        if med["form"]:
            if re.search(r'tab', med["form"], re.IGNORECASE):
                med["form"] = "Tablet"
            elif re.search(r'cap', med["form"], re.IGNORECASE):
                med["form"] = "Capsule"
            elif re.search(r'syr', med["form"], re.IGNORECASE):
                med["form"] = "Syrup"
    return data

# ------------------ Streamlit UI ------------------ #
# After imports and before functions, update the st.set_page_config:
st.set_page_config(
    layout="wide",
    page_title="🩺 Prescription Validator Pro",
    page_icon="💊",
    initial_sidebar_state="collapsed"
)

# Replace the existing st.markdown CSS with this enhanced version:
st.markdown("""
    <style>
    /* Main theme and colors */
    :root {
        --primary-color: #6200EE;
        --secondary-color: #03DAC6;
        --background-dark: #1a1a1a;
        --card-background: #2d2d2d;
        --text-color: #e0e0e0;
        --border-color: #404040;
    }

    /* Global styles */
    .stApp {
        background-color: var(--background-dark);
        color: var(--text-color);
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--secondary-color) !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px !important;
    }

    /* Card containers */
    .stMarkdown, div[data-testid="stExpander"] {
        background-color: var(--card-background);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }

    /* File uploader */
    .stFileUploader {
        background-color: var(--card-background) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 2px dashed var(--border-color) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), #7c4dff) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
    }

    /* Code blocks */
    pre {
        background-color: #2b2b2b !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        border: 1px solid var(--border-color) !important;
        font-family: 'Fira Code', monospace !important;
    }

    /* Spinner */
    .stSpinner > div {
        border-color: var(--secondary-color) !important;
    }

    /* Success/Error messages */
    .stSuccess, .stError {
        border-radius: 10px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }

    .stSuccess {
        background-color: rgba(4, 200, 100, 0.1) !important;
        border-left: 4px solid #04c864 !important;
    }

    .stError {
        background-color: rgba(255, 76, 76, 0.1) !important;
        border-left: 4px solid #ff4c4c !important;
    }

    /* Images */
    img {
        border-radius: 10px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
    }

    /* Dividers */
    hr {
        border-color: var(--border-color) !important;
        margin: 2rem 0 !important;
    }

    /* Text inputs and text areas */
    .stTextInput > div > div > input,
    .stTextArea > div > textarea {
        background-color: var(--card-background) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }

    /* Tooltips */
    .stTooltipIcon {
        color: var(--secondary-color) !important;
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: var(--secondary-color) !important;
    }

    /* Expander arrows */
    .streamlit-expanderHeader {
        color: var(--secondary-color) !important;
        font-weight: 600 !important;
    }

    /* Tables */
    .stTable {
        background-color: var(--card-background) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)
# st.set_page_config(layout="centered", page_title="🩺 Prescription to JSON Validator", page_icon="💊")

# st.markdown("""
#     <style>
#     body {
#         background-color: #1e1e1e;
#         color: #f5f5f5;
#     }
#     .stApp {
#         background-color: #1e1e1e;
#         color: #f5f5f5;
#     }
#     .stButton>button {
#         background-color: #6200EE;
#         color: white;
#     }
#     .stTextInput>div>div>input {
#         color: white;
#         background-color: #2b2b2b;
#     }
#     .css-1cpxqw2 {
#         color: white;
#     }
#     pre {
#         background-color: #2d2d2d !important;
#         color: #d4d4d4;
#         padding: 10px;
#         border-radius: 10px;
#     }
#     </style>
# """, unsafe_allow_html=True)

st.title("💊 Medical Prescription Validator")

uploaded_image = st.file_uploader("Upload a prescription image", type=["png", "jpg", "jpeg"])

if uploaded_image:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        temp_file.write(uploaded_image.getbuffer())
        temp_path = temp_file.name

    st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    st.markdown("---")

    with st.spinner("🔍 Extracting and parsing text..."):
        extracted_text = extract_text_from_image(temp_path)
        parsed_json = clean_json_data(parse_prescription(extracted_text))

    st.subheader("📝 Extracted & Parsed JSON:")
    st.code(json.dumps(parsed_json, indent=2), language="json")

    if st.button("📡 Validate"):
        with st.spinner("Generating validation report..."):
            try:
                response = requests.post("http://127.0.0.1:8000/validate-prescription/", json=parsed_json)
                response.raise_for_status()
                result = response.json()

                st.subheader("✅ Prescription Validation Report")

                if "report" in result:
                    st.markdown(result["report"], unsafe_allow_html=True)
                else:
                    st.code(json.dumps(result, indent=2), language="json")

            except requests.exceptions.RequestException as e:
                st.error(f"API call failed: {e}")