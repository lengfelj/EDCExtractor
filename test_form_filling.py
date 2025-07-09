#!/usr/bin/env python3
"""
Test script to demonstrate automated form filling
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from extractors import DocumentProcessor
from processors import AIExtractor
from automation import FormFiller
from models import ClinicalDataExtraction

def test_form_filling():
    """Test automated form filling with extracted data"""
    
    print("🏥 Testing Automated Form Filling...")
    print("="*50)
    
    # First, extract data from sample
    print("1. Extracting data from sample lab report...")
    try:
        processor = DocumentProcessor()
        image_base64, image_format = processor.process_document("sample_data/sample_lab_report.png")
        
        extractor = AIExtractor()
        extraction = extractor.extract_clinical_data(image_base64, image_format)
        
        print(f"✅ Extracted {len(extraction.lab_results)} lab results")
        print(f"✅ Extracted {len(extraction.vital_signs)} vital signs")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return
    
    # Create form configuration
    form_config = {
        "url": f"file://{os.path.abspath('sample_data/test_edc_form.html')}",
        "wait_selector": "form",
        "lab_fields": {
            "glucose": "#lab_glucose_value",
            "hemoglobin": "#lab_hgb_value", 
            "white_blood_cells": "#lab_wbc_value",
            "creatinine": "#lab_creat_value"
        },
        "vital_fields": {
            "heart_rate": "#vital_hr",
            "temperature": "#vital_temp",
            "respiratory_rate": "#vital_rr",
            "oxygen_saturation": "#vital_spo2"
        },
        "blood_pressure_fields": {
            "systolic": "#bp_sys",
            "diastolic": "#bp_dia"
        },
        "screenshot_path": "filled_form_screenshot.png"
    }
    
    print("\n2. Filling EDC form automatically...")
    try:
        with FormFiller(headless=False) as filler:
            filler.fill_form_from_extraction(extraction, form_config)
        
        print("✅ Form filled successfully!")
        print("📸 Screenshot saved: filled_form_screenshot.png")
        print("🌐 Check your browser - the form should be filled!")
        
    except Exception as e:
        print(f"❌ Form filling failed: {e}")
        print("Note: Make sure the sample EDC form exists and Playwright is installed")

if __name__ == "__main__":
    test_form_filling()