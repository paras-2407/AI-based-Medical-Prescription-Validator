# 💊 Medical Prescription Validator

An end-to-end NLP-based system that analyzes scanned medical prescriptions using OCR, validates medication safety using clinical datasets (RxNorm, openFDA, DailyMed), and generates human-readable reports using a fine-tuned Flan-T5-small model.

---

## 🧠 Features

- 📷 **OCR Parsing**: Extracts structured data (medication name, strength, form, frequency, etc.) from scanned prescription images using Tesseract.
- ⚕️ **Medication Validation**: Verifies dosage, form suitability, and indication using trusted medical sources:
  - RxNorm API
  - openFDA API
  - DailyMed drug labels
- 🧾 **Patient-Friendly Reports**: Generates fluent summaries using a fine-tuned `flan-t5-small` transformer model.
- 🌐 **Streamlit Frontend**: Interactive UI for uploading images or JSON data and visualizing validation results.

---

## 🔧 Tech Stack

- `Python` (3.10+)
- `Streamlit` for frontend
- `Tesseract OCR` via `pytesseract`
- `HuggingFace Transformers` for summarization
- `RxNorm`, `openFDA`, `DailyMed` for clinical validation
- `FastAPI` for backend integration

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/prescription-validator.git
cd prescription-validator
pip install -r requirements.txt
