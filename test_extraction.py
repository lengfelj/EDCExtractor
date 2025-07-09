#!/usr/bin/env python3
"""
Test script to demonstrate EHR to EDC extraction capabilities
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from extractors import DocumentProcessor
from processors import AIExtractor
from models import ClinicalDataExtraction


def test_extraction(file_path: str):
    """Test extraction on a sample document"""
    
    # Load environment
    load_dotenv()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: Please set OPENAI_API_KEY in .env file")
        return
    
    # Process document
    print(f"Processing document: {file_path}")
    processor = DocumentProcessor()
    
    try:
        image_base64, image_format = processor.process_document(file_path)
        print("✓ Document processed successfully")
        
        # Extract data
        print("Extracting clinical data...")
        extractor = AIExtractor()
        extraction = extractor.extract_clinical_data(image_base64, image_format)
        
        # Display results
        print("\n" + "="*50)
        print("EXTRACTION RESULTS")
        print("="*50)
        
        print(f"\nOverall Confidence: {extraction.overall_confidence:.2%}")
        print(f"Confidence Level: {extraction.get_confidence_level().value.upper()}")
        
        # Lab Results
        if extraction.lab_results:
            print(f"\n📊 Lab Results ({len(extraction.lab_results)} found):")
            print("-" * 40)
            for lab in extraction.lab_results:
                print(f"  {lab.test_name}: {lab.value} {lab.unit}")
                if lab.reference_range:
                    print(f"    Reference: {lab.reference_range}")
                if lab.abnormal_flag:
                    print(f"    Flag: {lab.abnormal_flag}")
                print(f"    Confidence: {lab.confidence:.2%}")
                print()
        
        # Vital Signs
        if extraction.vital_signs:
            print(f"\n❤️ Vital Signs ({len(extraction.vital_signs)} found):")
            print("-" * 40)
            for vital in extraction.vital_signs:
                print(f"  {vital.parameter}: {vital.value} {vital.unit}")
                if vital.position:
                    print(f"    Position: {vital.position}")
                print(f"    Confidence: {vital.confidence:.2%}")
                print()
        
        # Blood Pressure
        if extraction.blood_pressure:
            print("\n🩺 Blood Pressure:")
            print("-" * 40)
            bp = extraction.blood_pressure
            print(f"  {bp.systolic}/{bp.diastolic} {bp.unit}")
            if bp.position:
                print(f"  Position: {bp.position}")
            print(f"  Confidence: {bp.confidence:.2%}")
        
        # Save results
        output_file = Path("extraction_results.json")
        with open(output_file, 'w') as f:
            f.write(extraction.model_dump_json(indent=2))
        print(f"\n✓ Results saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_extraction(sys.argv[1])
    else:
        print("Usage: python test_extraction.py <path_to_medical_document>")
        print("\nExample: python test_extraction.py sample_data/lab_report.pdf")