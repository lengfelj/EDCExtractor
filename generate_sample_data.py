#!/usr/bin/env python3
"""
Generate sample lab report image for testing
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import random
import os


def generate_sample_lab_report():
    """Generate a sample lab report image"""
    
    # Create white background
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
    
    # Header
    y_pos = 20
    draw.text((width//2 - 100, y_pos), "CLINICAL LABORATORY REPORT", font=title_font, fill='black')
    
    # Patient info
    y_pos += 50
    draw.text((50, y_pos), "Patient: John Doe", font=normal_font, fill='black')
    draw.text((300, y_pos), "DOB: 01/15/1980", font=normal_font, fill='black')
    draw.text((500, y_pos), f"Date: {datetime.now().strftime('%m/%d/%Y')}", font=normal_font, fill='black')
    
    y_pos += 30
    draw.text((50, y_pos), "MRN: 123456", font=normal_font, fill='black')
    draw.text((300, y_pos), "Provider: Dr. Smith", font=normal_font, fill='black')
    
    # Line separator
    y_pos += 30
    draw.line([(50, y_pos), (width-50, y_pos)], fill='black', width=2)
    
    # Lab Results Header
    y_pos += 20
    draw.text((50, y_pos), "TEST NAME", font=header_font, fill='black')
    draw.text((300, y_pos), "RESULT", font=header_font, fill='black')
    draw.text((450, y_pos), "UNITS", font=header_font, fill='black')
    draw.text((550, y_pos), "REF RANGE", font=header_font, fill='black')
    draw.text((700, y_pos), "FLAG", font=header_font, fill='black')
    
    y_pos += 30
    draw.line([(50, y_pos), (width-50, y_pos)], fill='gray', width=1)
    
    # Lab Results Data
    lab_data = [
        ("Glucose", 95, "mg/dL", "70-100", ""),
        ("Hemoglobin", 14.5, "g/dL", "13.5-17.5", ""),
        ("White Blood Cells", 11.2, "K/uL", "4.5-11.0", "H"),
        ("Platelets", 250, "K/uL", "150-400", ""),
        ("Creatinine", 0.9, "mg/dL", "0.6-1.2", ""),
        ("BUN", 18, "mg/dL", "7-20", ""),
        ("Sodium", 140, "mEq/L", "136-145", ""),
        ("Potassium", 4.2, "mEq/L", "3.5-5.0", ""),
        ("ALT", 25, "U/L", "10-40", ""),
        ("AST", 22, "U/L", "10-40", ""),
    ]
    
    y_pos += 20
    for test, value, unit, ref_range, flag in lab_data:
        draw.text((50, y_pos), test, font=normal_font, fill='black')
        draw.text((300, y_pos), str(value), font=normal_font, fill='black')
        draw.text((450, y_pos), unit, font=normal_font, fill='black')
        draw.text((550, y_pos), ref_range, font=normal_font, fill='black')
        if flag:
            draw.text((700, y_pos), flag, font=normal_font, fill='red')
        y_pos += 25
    
    # Vital Signs Section
    y_pos += 40
    draw.line([(50, y_pos), (width-50, y_pos)], fill='black', width=2)
    y_pos += 20
    draw.text((50, y_pos), "VITAL SIGNS", font=header_font, fill='black')
    
    y_pos += 30
    draw.text((50, y_pos), "PARAMETER", font=header_font, fill='black')
    draw.text((300, y_pos), "VALUE", font=header_font, fill='black')
    draw.text((450, y_pos), "UNITS", font=header_font, fill='black')
    draw.text((600, y_pos), "TIME", font=header_font, fill='black')
    
    y_pos += 20
    draw.line([(50, y_pos), (width-50, y_pos)], fill='gray', width=1)
    
    # Vital Signs Data
    vital_data = [
        ("Blood Pressure", "120/80", "mmHg", "09:15"),
        ("Heart Rate", "72", "bpm", "09:15"),
        ("Temperature", "98.6", "°F", "09:15"),
        ("Respiratory Rate", "16", "breaths/min", "09:15"),
        ("O2 Saturation", "98", "%", "09:15"),
        ("Weight", "175", "lbs", "09:00"),
        ("Height", "70", "inches", "09:00"),
    ]
    
    y_pos += 20
    for param, value, unit, time in vital_data:
        draw.text((50, y_pos), param, font=normal_font, fill='black')
        draw.text((300, y_pos), value, font=normal_font, fill='black')
        draw.text((450, y_pos), unit, font=normal_font, fill='black')
        draw.text((600, y_pos), time, font=normal_font, fill='black')
        y_pos += 25
    
    # Save image
    output_path = "sample_data/sample_lab_report.png"
    os.makedirs("sample_data", exist_ok=True)
    img.save(output_path)
    print(f"✓ Generated sample lab report: {output_path}")
    
    return output_path


if __name__ == "__main__":
    generate_sample_lab_report()