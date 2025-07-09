from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LabResult(BaseModel):
    test_name: str = Field(..., description="Name of the lab test")
    value: float = Field(..., description="Numeric result value")
    unit: str = Field(..., description="Unit of measurement")
    reference_range: Optional[str] = Field(None, description="Normal reference range")
    date_collected: Optional[datetime] = Field(None, description="Date/time of collection")
    abnormal_flag: Optional[str] = Field(None, description="H/L/N flag")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence")
    
    @validator('abnormal_flag')
    def validate_abnormal_flag(cls, v):
        if v and v.upper() not in ['H', 'L', 'N', 'HIGH', 'LOW', 'NORMAL']:
            raise ValueError('Abnormal flag must be H, L, or N')
        return v.upper()[0] if v else None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class VitalSign(BaseModel):
    parameter: str = Field(..., description="Vital sign parameter name")
    value: float = Field(..., description="Measured value")
    unit: str = Field(..., description="Unit of measurement")
    date_time: Optional[datetime] = Field(None, description="Date/time of measurement")
    position: Optional[str] = Field(None, description="Patient position during measurement")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Extraction confidence")
    
    @validator('parameter')
    def standardize_parameter(cls, v):
        parameter_map = {
            'bp': 'blood_pressure',
            'hr': 'heart_rate',
            'temp': 'temperature',
            'rr': 'respiratory_rate',
            'spo2': 'oxygen_saturation',
            'o2 sat': 'oxygen_saturation'
        }
        return parameter_map.get(v.lower(), v.lower())


class BloodPressure(BaseModel):
    systolic: float = Field(..., description="Systolic pressure")
    diastolic: float = Field(..., description="Diastolic pressure")
    unit: str = Field("mmHg", description="Unit of measurement")
    date_time: Optional[datetime] = Field(None, description="Date/time of measurement")
    position: Optional[str] = Field(None, description="Patient position")
    confidence: float = Field(1.0, ge=0.0, le=1.0)


class ClinicalDataExtraction(BaseModel):
    source_document: str = Field(..., description="Source document identifier")
    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    patient_id: Optional[str] = Field(None, description="Patient identifier if available")
    
    lab_results: List[LabResult] = Field(default_factory=list)
    vital_signs: List[VitalSign] = Field(default_factory=list)
    blood_pressure: Optional[BloodPressure] = None
    
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_overall_confidence(self):
        all_confidences = []
        all_confidences.extend([lr.confidence for lr in self.lab_results])
        all_confidences.extend([vs.confidence for vs in self.vital_signs])
        if self.blood_pressure:
            all_confidences.append(self.blood_pressure.confidence)
        
        if all_confidences:
            self.overall_confidence = sum(all_confidences) / len(all_confidences)
        return self.overall_confidence
    
    def get_confidence_level(self) -> ConfidenceLevel:
        if self.overall_confidence >= 0.9:
            return ConfidenceLevel.HIGH
        elif self.overall_confidence >= 0.7:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW