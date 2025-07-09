import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import pandas as pd
from datetime import datetime

from extractors import DocumentProcessor
from processors import AIExtractor
from automation import FormFiller
from models import ClinicalDataExtraction

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="EHR to EDC Transfer POC",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'form_filled' not in st.session_state:
    st.session_state.form_filled = False


def main():
    st.title("🏥 EHR to EDC Data Transfer - Proof of Concept")
    st.markdown("### AI-Powered Clinical Data Extraction and Form Automation")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", 
                               value=os.getenv("OPENAI_API_KEY", ""))
        
        # Confidence threshold
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.85, 0.05)
        
        # Form configuration
        st.subheader("EDC Form Settings")
        form_url = st.text_input("EDC Form URL", placeholder="https://edc-system.com/form")
        auto_fill = st.checkbox("Auto-fill form", value=True)
        
    # Main content area
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("1. Source Document")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload medical document",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload a document containing lab results or vital signs"
        )
        
        if uploaded_file:
            # Save uploaded file temporarily
            temp_path = Path(f"temp_{uploaded_file.name}")
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            # Display uploaded document
            if uploaded_file.type == "application/pdf":
                st.info("PDF uploaded - will process first page")
            else:
                st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
            
            # Extract button
            if st.button("🔍 Extract Clinical Data", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        # Process document
                        processor = DocumentProcessor()
                        image_base64, image_format = processor.process_document(temp_path)
                        
                        # Extract data using AI
                        extractor = AIExtractor(api_key=api_key)
                        extraction = extractor.extract_clinical_data(image_base64, image_format)
                        
                        # Store in session state
                        st.session_state.extracted_data = extraction
                        st.success("✅ Data extraction completed!")
                        
                    except Exception as e:
                        st.error(f"Error during extraction: {str(e)}")
                    finally:
                        # Clean up temp file
                        if temp_path.exists():
                            temp_path.unlink()
    
    with col2:
        st.header("2. Extracted Data")
        
        if st.session_state.extracted_data:
            extraction = st.session_state.extracted_data
            
            # Display confidence level
            confidence_level = extraction.get_confidence_level()
            confidence_color = {
                "high": "green",
                "medium": "orange", 
                "low": "red"
            }[confidence_level.value]
            
            st.metric("Overall Confidence", 
                     f"{extraction.overall_confidence:.2%}",
                     delta=confidence_level.value.upper(),
                     delta_color="normal" if confidence_level.value != "low" else "inverse")
            
            # Lab Results
            if extraction.lab_results:
                st.subheader("📊 Lab Results")
                lab_data = []
                for lab in extraction.lab_results:
                    lab_data.append({
                        "Test": lab.test_name,
                        "Value": f"{lab.value} {lab.unit}",
                        "Reference": lab.reference_range or "N/A",
                        "Flag": lab.abnormal_flag or "N",
                        "Confidence": f"{lab.confidence:.2%}"
                    })
                st.dataframe(pd.DataFrame(lab_data), use_container_width=True)
            
            # Vital Signs
            if extraction.vital_signs or extraction.blood_pressure:
                st.subheader("❤️ Vital Signs")
                vital_data = []
                
                # Add blood pressure if present
                if extraction.blood_pressure:
                    bp = extraction.blood_pressure
                    vital_data.append({
                        "Parameter": "Blood Pressure",
                        "Value": f"{bp.systolic}/{bp.diastolic} {bp.unit}",
                        "Position": bp.position or "N/A",
                        "Confidence": f"{bp.confidence:.2%}"
                    })
                
                # Add other vitals
                for vital in extraction.vital_signs:
                    vital_data.append({
                        "Parameter": vital.parameter.replace("_", " ").title(),
                        "Value": f"{vital.value} {vital.unit}",
                        "Position": vital.position or "N/A",
                        "Confidence": f"{vital.confidence:.2%}"
                    })
                
                st.dataframe(pd.DataFrame(vital_data), use_container_width=True)
            
            # Export options
            st.subheader("📤 Export Data")
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                json_data = extraction.model_dump_json(indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"clinical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                # Fill form button
                if form_url and auto_fill:
                    if st.button("🖊️ Fill EDC Form", type="primary"):
                        with st.spinner("Filling form..."):
                            try:
                                # Create form configuration
                                form_config = {
                                    "url": form_url,
                                    "wait_selector": "form",
                                    "lab_fields": {
                                        "glucose": "#glucose",
                                        "hemoglobin": "#hgb",
                                        "white_blood_cells": "#wbc"
                                    },
                                    "vital_fields": {
                                        "heart_rate": "#hr",
                                        "temperature": "#temp",
                                        "respiratory_rate": "#rr"
                                    },
                                    "blood_pressure_fields": {
                                        "systolic": "#bp_systolic",
                                        "diastolic": "#bp_diastolic"
                                    },
                                    "screenshot_path": "form_filled.png"
                                }
                                
                                # Fill form
                                with FormFiller(headless=False) as filler:
                                    filler.fill_form_from_extraction(extraction, form_config)
                                
                                st.success("✅ Form filled successfully!")
                                st.session_state.form_filled = True
                                
                            except Exception as e:
                                st.error(f"Error filling form: {str(e)}")
    
    # Instructions section
    with st.expander("📖 Instructions"):
        st.markdown("""
        ### How to use this POC:
        
        1. **Upload a document** containing lab results or vital signs (PDF, PNG, JPG)
        2. Click **Extract Clinical Data** to process the document with AI
        3. Review the extracted data and confidence scores
        4. Export data as JSON or fill an EDC form automatically
        
        ### Supported Data Types:
        - **Lab Results**: Glucose, CBC, Chemistry panels, etc.
        - **Vital Signs**: Blood pressure, heart rate, temperature, respiratory rate, O2 saturation
        
        ### Notes:
        - Ensure your OpenAI API key is set in the sidebar
        - Higher confidence thresholds provide more reliable extractions
        - The form automation requires the EDC system URL
        """)


if __name__ == "__main__":
    main()