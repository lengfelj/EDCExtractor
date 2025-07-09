import os
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
import logging
from models.clinical_data import ClinicalDataExtraction, LabResult, VitalSign, BloodPressure

logger = logging.getLogger(__name__)


class AIExtractor:
    """Uses AI models to extract clinical data from documents"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Use gpt-4o for best quality, gpt-4o-mini for speed/cost
    
    def extract_clinical_data(self, image_base64: str, image_format: str) -> ClinicalDataExtraction:
        """Extract lab results and vital signs from image"""
        try:
            # Prepare the prompt
            prompt = self._create_extraction_prompt()
            
            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical data extraction expert. Extract clinical data accurately and provide confidence scores."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_format};base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            # Parse the response
            extracted_data = self._parse_ai_response(response.choices[0].message.content)
            return extracted_data
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            raise
    
    def _create_extraction_prompt(self) -> str:
        """Create detailed prompt for data extraction"""
        return """
        Analyze this medical document and extract ALL lab results and vital signs.
        
        For LAB RESULTS, extract:
        - Test name
        - Numeric value
        - Unit of measurement
        - Reference range (if shown)
        - Collection date/time
        - Abnormal flags (H/L/N)
        
        For VITAL SIGNS, extract:
        - Parameter name (blood pressure, heart rate, temperature, respiratory rate, O2 saturation)
        - Value
        - Unit
        - Measurement date/time
        - Patient position (if mentioned)
        
        For BLOOD PRESSURE specifically:
        - Extract systolic and diastolic values separately
        
        Return the data in this exact JSON format:
        {
            "lab_results": [
                {
                    "test_name": "Glucose",
                    "value": 95,
                    "unit": "mg/dL",
                    "reference_range": "70-100",
                    "date_collected": "2024-01-15T08:30:00",
                    "abnormal_flag": "N",
                    "confidence": 0.95
                }
            ],
            "vital_signs": [
                {
                    "parameter": "heart_rate",
                    "value": 72,
                    "unit": "bpm",
                    "date_time": "2024-01-15T09:00:00",
                    "position": "sitting",
                    "confidence": 0.98
                }
            ],
            "blood_pressure": {
                "systolic": 120,
                "diastolic": 80,
                "unit": "mmHg",
                "date_time": "2024-01-15T09:00:00",
                "position": "sitting",
                "confidence": 0.97
            }
        }
        
        IMPORTANT:
        - Extract ALL visible data, not just examples
        - Use confidence scores between 0 and 1 based on clarity
        - If date/time is not visible, set to null
        - If a field is not present or unclear, omit it entirely from the JSON
        - Only include fields where you can extract actual values
        - Standardize units (e.g., "beats/min" -> "bpm")
        - For blood pressure, only include if you can identify systolic/diastolic values
        """
    
    def _parse_ai_response(self, response: str) -> ClinicalDataExtraction:
        """Parse AI response into structured data"""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            
            data = json.loads(json_str)
            
            # Create extraction object
            extraction = ClinicalDataExtraction(
                source_document="ai_extraction"
            )
            
            # Parse lab results - skip invalid ones
            for lab_data in data.get("lab_results", []):
                try:
                    # Skip if missing required fields
                    if not lab_data.get("test_name") or lab_data.get("value") is None:
                        continue
                    lab_result = LabResult(**lab_data)
                    extraction.lab_results.append(lab_result)
                except Exception as e:
                    logger.warning(f"Skipping invalid lab result: {e}")
                    continue
            
            # Parse vital signs - skip invalid ones
            for vital_data in data.get("vital_signs", []):
                try:
                    # Skip if missing required fields
                    if not vital_data.get("parameter") or vital_data.get("value") is None:
                        continue
                    vital_sign = VitalSign(**vital_data)
                    extraction.vital_signs.append(vital_sign)
                except Exception as e:
                    logger.warning(f"Skipping invalid vital sign: {e}")
                    continue
            
            # Parse blood pressure - skip if invalid
            if data.get("blood_pressure"):
                try:
                    bp_data = data["blood_pressure"]
                    # Only create if we have at least one valid value
                    if bp_data.get("systolic") is not None or bp_data.get("diastolic") is not None:
                        extraction.blood_pressure = BloodPressure(**bp_data)
                except Exception as e:
                    logger.warning(f"Skipping invalid blood pressure: {e}")
            
            # Calculate overall confidence
            extraction.calculate_overall_confidence()
            
            return extraction
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.debug(f"Response was: {response}")
            
            # Return empty extraction instead of failing
            return ClinicalDataExtraction(
                source_document="ai_extraction_failed",
                overall_confidence=0.0
            )