from playwright.sync_api import sync_playwright, Page, Browser
from typing import Dict, Any, Optional, List
import logging
import time
from models.clinical_data import ClinicalDataExtraction, LabResult, VitalSign

logger = logging.getLogger(__name__)


class FormFiller:
    """Automates web form filling for EDC systems"""
    
    def __init__(self, headless: bool = False, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
    
    def __enter__(self):
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_browser()
    
    def start_browser(self):
        """Initialize browser instance"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(self.timeout)
    
    def close_browser(self):
        """Clean up browser resources"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
    
    def navigate_to_form(self, url: str):
        """Navigate to EDC form URL"""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        logger.info(f"Navigating to: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
    
    def fill_lab_results(self, lab_results: List[LabResult], field_mapping: Dict[str, str]):
        """Fill lab result fields"""
        for lab in lab_results:
            try:
                # Map lab test name to field selector
                field_key = self._normalize_field_name(lab.test_name)
                if field_key in field_mapping:
                    selector = field_mapping[field_key]
                    
                    # Fill value field
                    value_selector = f"{selector}_value"
                    if self.page.locator(value_selector).count() > 0:
                        self.page.fill(value_selector, str(lab.value))
                        logger.info(f"Filled {lab.test_name} value: {lab.value}")
                    
                    # Fill unit field if exists
                    unit_selector = f"{selector}_unit"
                    if self.page.locator(unit_selector).count() > 0:
                        self.page.fill(unit_selector, lab.unit)
                    
                    # Fill date field if exists
                    date_selector = f"{selector}_date"
                    if lab.date_collected and self.page.locator(date_selector).count() > 0:
                        date_str = lab.date_collected.strftime("%Y-%m-%d")
                        self.page.fill(date_selector, date_str)
                
            except Exception as e:
                logger.error(f"Error filling lab result {lab.test_name}: {e}")
    
    def fill_vital_signs(self, vital_signs: List[VitalSign], field_mapping: Dict[str, str]):
        """Fill vital sign fields"""
        for vital in vital_signs:
            try:
                field_key = self._normalize_field_name(vital.parameter)
                if field_key in field_mapping:
                    selector = field_mapping[field_key]
                    
                    # Handle blood pressure specially
                    if vital.parameter == "blood_pressure" and "/" in str(vital.value):
                        systolic, diastolic = str(vital.value).split("/")
                        
                        # Fill systolic
                        systolic_selector = f"{selector}_systolic"
                        if self.page.locator(systolic_selector).count() > 0:
                            self.page.fill(systolic_selector, systolic.strip())
                        
                        # Fill diastolic
                        diastolic_selector = f"{selector}_diastolic"
                        if self.page.locator(diastolic_selector).count() > 0:
                            self.page.fill(diastolic_selector, diastolic.strip())
                    else:
                        # Fill standard vital sign
                        if self.page.locator(selector).count() > 0:
                            self.page.fill(selector, str(vital.value))
                            logger.info(f"Filled {vital.parameter}: {vital.value}")
                
            except Exception as e:
                logger.error(f"Error filling vital sign {vital.parameter}: {e}")
    
    def fill_form_from_extraction(self, extraction: ClinicalDataExtraction, form_config: Dict[str, Any]):
        """Fill entire form from extracted data"""
        try:
            # Navigate to form
            if "url" in form_config:
                self.navigate_to_form(form_config["url"])
            
            # Wait for form to load
            if "wait_selector" in form_config:
                self.page.wait_for_selector(form_config["wait_selector"])
            
            # Fill lab results
            if extraction.lab_results and "lab_fields" in form_config:
                self.fill_lab_results(extraction.lab_results, form_config["lab_fields"])
            
            # Fill vital signs
            if extraction.vital_signs and "vital_fields" in form_config:
                self.fill_vital_signs(extraction.vital_signs, form_config["vital_fields"])
            
            # Handle blood pressure separately if needed
            if extraction.blood_pressure and "blood_pressure_fields" in form_config:
                bp_config = form_config["blood_pressure_fields"]
                if "systolic" in bp_config:
                    self.page.fill(bp_config["systolic"], str(extraction.blood_pressure.systolic))
                if "diastolic" in bp_config:
                    self.page.fill(bp_config["diastolic"], str(extraction.blood_pressure.diastolic))
            
            # Submit form if configured
            if form_config.get("auto_submit", False) and "submit_button" in form_config:
                self.page.click(form_config["submit_button"])
                logger.info("Form submitted")
            
            # Take screenshot for verification
            if "screenshot_path" in form_config:
                self.page.screenshot(path=form_config["screenshot_path"])
                logger.info(f"Screenshot saved to {form_config['screenshot_path']}")
            
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            raise
    
    def _normalize_field_name(self, name: str) -> str:
        """Normalize field names for mapping"""
        return name.lower().replace(" ", "_").replace("-", "_")