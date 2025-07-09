import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import pandas as pd
import time
from datetime import datetime

from extractors import DocumentProcessor
from processors import AIExtractor
from automation import FormFiller
from models import ClinicalDataExtraction

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="Clinical Research Workflow",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'form_filled' not in st.session_state:
    st.session_state.form_filled = False


def generate_filled_form(extraction, html_content):
    """Generate an HTML form pre-filled with extracted data"""
    filled_html = html_content
    
    # Fill lab results
    for lab in extraction.lab_results:
        field_name = lab.test_name.lower().replace(' ', '_')
        if 'glucose' in field_name:
            filled_html = filled_html.replace('id="lab_glucose_value"', f'id="lab_glucose_value" value="{lab.value}"')
        elif 'hemoglobin' in field_name:
            filled_html = filled_html.replace('id="lab_hgb_value"', f'id="lab_hgb_value" value="{lab.value}"')
        elif 'white_blood_cells' in field_name or 'wbc' in field_name:
            filled_html = filled_html.replace('id="lab_wbc_value"', f'id="lab_wbc_value" value="{lab.value}"')
        elif 'creatinine' in field_name:
            filled_html = filled_html.replace('id="lab_creat_value"', f'id="lab_creat_value" value="{lab.value}"')
        elif 'albumin' in field_name:
            filled_html = filled_html.replace('id="lab_albumin_value"', f'id="lab_albumin_value" value="{lab.value}"')
        elif 'alt' in field_name and 'alanine' in field_name:
            filled_html = filled_html.replace('id="lab_alt_value"', f'id="lab_alt_value" value="{lab.value}"')
        elif 'ast' in field_name and 'aspartate' in field_name:
            filled_html = filled_html.replace('id="lab_ast_value"', f'id="lab_ast_value" value="{lab.value}"')
        elif field_name == 'alt':
            filled_html = filled_html.replace('id="lab_alt_value"', f'id="lab_alt_value" value="{lab.value}"')
        elif field_name == 'ast':
            filled_html = filled_html.replace('id="lab_ast_value"', f'id="lab_ast_value" value="{lab.value}"')
    
    # Fill vital signs
    for vital in extraction.vital_signs:
        param = vital.parameter.lower()
        if 'heart_rate' in param:
            filled_html = filled_html.replace('id="vital_hr"', f'id="vital_hr" value="{vital.value}"')
        elif 'temperature' in param:
            filled_html = filled_html.replace('id="vital_temp"', f'id="vital_temp" value="{vital.value}"')
        elif 'respiratory_rate' in param:
            filled_html = filled_html.replace('id="vital_rr"', f'id="vital_rr" value="{vital.value}"')
        elif 'oxygen_saturation' in param:
            filled_html = filled_html.replace('id="vital_spo2"', f'id="vital_spo2" value="{vital.value}"')
    
    # Fill blood pressure - only if values exist
    if extraction.blood_pressure:
        if extraction.blood_pressure.systolic is not None:
            filled_html = filled_html.replace('id="bp_sys"', f'id="bp_sys" value="{extraction.blood_pressure.systolic}"')
        if extraction.blood_pressure.diastolic is not None:
            filled_html = filled_html.replace('id="bp_dia"', f'id="bp_dia" value="{extraction.blood_pressure.diastolic}"')
    
    return filled_html


def animate_form_filling_iframe(extraction, status_text, progress_bar):
    """Animate the form filling process with real form updates"""
    import time
    
    progress = 60
    total_fields = len(extraction.lab_results) + len(extraction.vital_signs) + (1 if extraction.blood_pressure else 0)
    
    if total_fields == 0:
        return
    
    progress_increment = 35 / total_fields  # 35% of progress bar for form filling
    
    # Get the base form HTML
    form_path = Path("sample_data/test_edc_form.html")
    if not form_path.exists():
        return
        
    with open(form_path, 'r') as f:
        base_form_html = f.read()
    
    # Create a partial extraction for progressive filling
    partial_extraction = ClinicalDataExtraction(source_document="partial_fill")
    
    # Fill lab results one by one
    for i, lab in enumerate(extraction.lab_results):
        field_name = lab.test_name.lower().replace(' ', '_')
        
        # Add this lab result to our partial extraction
        partial_extraction.lab_results.append(lab)
        
        if 'glucose' in field_name:
            status_text.text(f"📊 Filling {lab.test_name}: {lab.value} {lab.unit}")
        elif 'hemoglobin' in field_name:
            status_text.text(f"📊 Filling {lab.test_name}: {lab.value} {lab.unit}")
        elif 'white_blood_cells' in field_name or 'wbc' in field_name:
            status_text.text(f"📊 Filling {lab.test_name}: {lab.value} {lab.unit}")
        elif 'creatinine' in field_name:
            status_text.text(f"📊 Filling {lab.test_name}: {lab.value} {lab.unit}")
        else:
            status_text.text(f"📊 Filling {lab.test_name}: {lab.value} {lab.unit}")
        
        # Update the form in real-time by updating session state
        # Note: The form will refresh on the next Streamlit rerun
        st.session_state.extracted_data = partial_extraction
        
        time.sleep(0.8)  # Pause for dramatic effect
        progress += progress_increment
        progress_bar.progress(min(int(progress), 95))
    
    # Fill vital signs one by one
    for vital in extraction.vital_signs:
        param = vital.parameter.lower()
        
        # Add this vital sign to our partial extraction
        partial_extraction.vital_signs.append(vital)
        
        if 'heart_rate' in param:
            display_name = 'Heart Rate'
        elif 'temperature' in param:
            display_name = 'Temperature'
        elif 'respiratory_rate' in param:
            display_name = 'Respiratory Rate'
        elif 'oxygen_saturation' in param:
            display_name = 'Oxygen Saturation'
        else:
            display_name = param.replace('_', ' ').title()
        
        status_text.text(f"❤️ Filling {display_name}: {vital.value} {vital.unit}")
        
        # Update the form in real-time by updating session state
        # Note: The form will refresh on the next Streamlit rerun
        st.session_state.extracted_data = partial_extraction
        
        time.sleep(0.8)
        progress += progress_increment
        progress_bar.progress(min(int(progress), 95))
    
    # Fill blood pressure
    if extraction.blood_pressure:
        partial_extraction.blood_pressure = extraction.blood_pressure
        
        status_text.text(f"🩺 Filling Blood Pressure: {extraction.blood_pressure.systolic}/{extraction.blood_pressure.diastolic} {extraction.blood_pressure.unit}")
        
        # Final form update
        st.session_state.extracted_data = partial_extraction
        
        time.sleep(0.8)
        progress += progress_increment
        progress_bar.progress(min(int(progress), 95))


def merge_extractions(existing_extraction, new_extraction):
    """Merge new extraction data with existing data, avoiding duplicates"""
    if not existing_extraction or existing_extraction.overall_confidence == 0:
        return new_extraction
    
    # Create merged extraction starting with existing data
    merged = ClinicalDataExtraction(
        source_document=f"{existing_extraction.source_document} + {new_extraction.source_document}",
        patient_id=existing_extraction.patient_id or new_extraction.patient_id
    )
    
    # Start with existing data
    merged.lab_results = existing_extraction.lab_results.copy()
    merged.vital_signs = existing_extraction.vital_signs.copy()
    merged.blood_pressure = existing_extraction.blood_pressure
    
    # Add new lab results (avoid duplicates by test name)
    existing_lab_names = {lab.test_name.lower() for lab in merged.lab_results}
    for new_lab in new_extraction.lab_results:
        if new_lab.test_name.lower() not in existing_lab_names:
            merged.lab_results.append(new_lab)
        else:
            # Update existing lab result with newer confidence if higher
            for i, existing_lab in enumerate(merged.lab_results):
                if existing_lab.test_name.lower() == new_lab.test_name.lower():
                    if new_lab.confidence > existing_lab.confidence:
                        merged.lab_results[i] = new_lab
                    break
    
    # Add new vital signs (avoid duplicates by parameter)
    existing_vital_params = {vital.parameter.lower() for vital in merged.vital_signs}
    for new_vital in new_extraction.vital_signs:
        if new_vital.parameter.lower() not in existing_vital_params:
            merged.vital_signs.append(new_vital)
        else:
            # Update existing vital sign with newer confidence if higher
            for i, existing_vital in enumerate(merged.vital_signs):
                if existing_vital.parameter.lower() == new_vital.parameter.lower():
                    if new_vital.confidence > existing_vital.confidence:
                        merged.vital_signs[i] = new_vital
                    break
    
    # Update blood pressure if new one has higher confidence or if we don't have one
    if new_extraction.blood_pressure:
        if not merged.blood_pressure or new_extraction.blood_pressure.confidence > merged.blood_pressure.confidence:
            merged.blood_pressure = new_extraction.blood_pressure
    
    # Recalculate overall confidence
    merged.calculate_overall_confidence()
    
    return merged


def animate_form_filling(extraction, base_html, form_container, status_text, progress_bar):
    """Legacy function - keeping for compatibility"""
    return animate_form_filling_iframe(extraction, status_text, progress_bar)


def main():
    # Add custom CSS for two-application look
    st.markdown("""
    <style>
    .main-container {
        display: flex;
        gap: 20px;
        height: 100vh;
    }
    
    .edc-application {
        flex: 1;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        overflow: hidden;
    }
    
    .edc-header {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: bold;
        font-size: 16px;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .edc-content {
        background: white;
        padding: 20px;
        height: calc(100vh - 120px);
        overflow-y: auto;
    }
    
    .ai-application {
        flex: 1;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        overflow: hidden;
    }
    
    .ai-header {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        color: white;
        padding: 15px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: bold;
        font-size: 16px;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .ai-content {
        background: white;
        padding: 20px;
        height: calc(100vh - 120px);
        overflow-y: auto;
    }
    
    .window-controls {
        display: flex;
        gap: 8px;
    }
    
    .window-control {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
    }
    
    .window-control.close { background: #ff5f57; }
    .window-control.minimize { background: #ffbd2e; }
    .window-control.maximize { background: #28ca42; }
    
    .stProgress .st-bo {
        background-color: #e0e0e0;
    }
    .stProgress .st-bp {
        background-color: #f5576c;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    
    .animate-bounce {
        animation: bounce 0.5s ease-in-out;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    /* Hide streamlit elements */
    .stDeployButton { display: none; }
    .stDecoration { display: none; }
    
    /* Style the window headers */
    .edc-application, .ai-application {
        margin-bottom: 20px;
    }
    
    /* Add some spacing between windows and content */
    div[data-testid="column"] {
        padding: 0 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Configuration in sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("OpenAI API Key", type="password", 
                               value=os.getenv("OPENAI_API_KEY", ""))
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.85, 0.05)
        
        st.markdown("---")
        st.markdown("**Workflow:**")
        st.markdown("1. **MediRave** EDC form is open")
        st.markdown("2. Use **Joe's AI Extractor**")
        st.markdown("3. Watch auto-fill magic!")
    
    # Create two columns for the main layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    # Left side - MediRave EDC Application
    with col1:
        st.markdown("""
        <div class="edc-application">
            <div class="edc-header">
                <div>🏥 VeedaData MediRave™ EDC System v2.1</div>
                <div class="window-controls">
                    <div class="window-control close"></div>
                    <div class="window-control minimize"></div>
                    <div class="window-control maximize"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Content inside the window
        with st.container():
            st.markdown("**Study:** PROTOCOL-2024-001 | **Subject:** TEST-001 | **Visit:** Screening")
            
            # Status indicator
            if st.session_state.extracted_data and st.session_state.extracted_data.overall_confidence > 0:
                extraction = st.session_state.extracted_data
                if "+" in extraction.source_document:
                    st.success("✅ Form auto-filled from multiple documents by Joe's AI Extractor Pro")
                else:
                    st.success("✅ Form auto-filled by Joe's AI Extractor Pro")
            else:
                st.info("⏳ Waiting for data extraction...")
            
            # Form display - always show the form
            form_path = Path("sample_data/test_edc_form.html")
            
            # Always display the form
            if form_path.exists():
                with open(form_path, 'r') as f:
                    base_form_html = f.read()
                
                # If we have extracted data, fill the form with it
                if st.session_state.extracted_data and st.session_state.extracted_data.overall_confidence > 0:
                    filled_form_html = generate_filled_form(st.session_state.extracted_data, base_form_html)
                    components.html(filled_form_html, height=500, scrolling=True)
                else:
                    # Show empty form
                    components.html(base_form_html, height=500, scrolling=True)
            else:
                st.error("EDC form template not found!")
            
            # Form actions
            st.markdown("---")
            col_save, col_refresh, col_submit = st.columns(3)
            with col_save:
                if st.button("💾 Save", disabled=True, key="save_btn"):
                    st.info("Demo mode")
            with col_refresh:
                if st.button("🔄 Refresh", disabled=True, key="refresh_btn"):
                    st.info("Demo mode")
            with col_submit:
                if st.button("✅ Submit", disabled=True, key="submit_btn"):
                    st.info("Demo mode")
    
    # Right side - AI Extraction Application
    with col2:
        st.markdown("""
        <div class="ai-application">
            <div class="ai-header">
                <div>🤖 Joe's AI Extractor Pro</div>
                <div class="window-controls">
                    <div class="window-control close"></div>
                    <div class="window-control minimize"></div>
                    <div class="window-control maximize"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Content inside the window
        with st.container():
            st.markdown("### 📄 Source Document")
            st.markdown("*Upload your lab report, vital signs sheet, or medical record*")
            
            # File upload
            uploaded_file = st.file_uploader(
                "Choose file",
                type=['pdf', 'png', 'jpg', 'jpeg'],
                help="Support: PDF, PNG, JPG, JPEG"
            )
        
            if uploaded_file:
                # Save uploaded file temporarily
                temp_path = Path(f"temp_{uploaded_file.name}")
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                # Extract button - moved higher up
                if st.button("🚀 Extract & Auto-Fill MediRave", type="primary"):
                    # Progress tracking below the button
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Step 1: Process document
                        status_text.text("🔍 Processing document...")
                        progress_bar.progress(20)
                        
                        processor = DocumentProcessor()
                        image_base64, image_format = processor.process_document(temp_path)
                        
                        # Step 2: AI Analysis
                        status_text.text("🤖 AI analyzing document...")
                        progress_bar.progress(40)
                        
                        extractor = AIExtractor(api_key=api_key)
                        new_extraction = extractor.extract_clinical_data(image_base64, image_format)
                        
                        # Step 3: Merge with existing data
                        status_text.text("📝 Merging with existing data...")
                        progress_bar.progress(50)
                        
                        # Merge with existing extraction data
                        existing_extraction = st.session_state.get('extracted_data')
                        merged_extraction = merge_extractions(existing_extraction, new_extraction)
                        
                        # Step 4: Start populating form with animation
                        status_text.text("📝 Populating MediRave form...")
                        progress_bar.progress(60)
                        
                        # Simulate real-time form filling with delays
                        animate_form_filling_iframe(merged_extraction, status_text, progress_bar)
                        
                        # Store merged data in session state
                        st.session_state.extracted_data = merged_extraction
                        
                        # Final success message with celebration
                        progress_bar.progress(100)
                        if merged_extraction.overall_confidence > 0:
                            # Celebration animation
                            time.sleep(0.5)
                            status_text.markdown(f"""
                            <div class="success-message animate-bounce">
                                🎉 <strong>SUCCESS!</strong> Auto-filled {len(merged_extraction.lab_results)} lab results and {len(merged_extraction.vital_signs)} vital signs with {merged_extraction.overall_confidence:.1%} confidence!
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Add balloons for extra celebration
                            st.balloons()
                            
                            # Force immediate form update by triggering a rerun
                            st.rerun()
                            
                        else:
                            status_text.warning("⚠️ Extraction completed but no clear data found. Try a different document or check image quality.")
                        
                    except Exception as e:
                        status_text.error(f"❌ Error during extraction: {str(e)}")
                        progress_bar.progress(0)
                        # Still create empty extraction to prevent further errors
                        st.session_state.extracted_data = ClinicalDataExtraction(
                            source_document="error",
                            overall_confidence=0.0
                        )
                    finally:
                        # Clean up temp file
                        if temp_path.exists():
                            temp_path.unlink()
                
                # Display uploaded document below the button
                st.markdown("---")
                st.markdown("**📄 Uploaded Document:**")
                if uploaded_file.type == "application/pdf":
                    st.info("📄 PDF uploaded - will process first page")
                else:
                    st.image(uploaded_file, caption="Source Document", use_column_width=True)
            
            st.markdown("---")
            st.header("📊 Extraction Results")
            
            if st.session_state.extracted_data:
                extraction = st.session_state.extracted_data
                
                # Display confidence level
                confidence_level = extraction.get_confidence_level()
                
                st.metric("Overall Confidence", 
                         f"{extraction.overall_confidence:.2%}",
                         delta=confidence_level.value.upper(),
                         delta_color="normal" if confidence_level.value != "low" else "inverse")
                
                # Show completion stats
                result_col1, result_col2, result_col3 = st.columns(3)
                with result_col1:
                    st.metric("Lab Results", len(extraction.lab_results))
                with result_col2:
                    st.metric("Vital Signs", len(extraction.vital_signs))
                with result_col3:
                    st.metric("Fields Filled", len(extraction.lab_results) + len(extraction.vital_signs))
                
                # Export options
                st.subheader("📤 Export Data")
                json_data = extraction.model_dump_json(indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"clinical_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.info("👆 Upload a document and click extract to see results")
            
            # Instructions within the AI application
            st.markdown("---")
            with st.expander("📖 How This Works"):
                st.markdown("""
                ### Real-World CRC Workflow:
                
                **Step 1:** Your MediRave EDC form is already open (left window)
                
                **Step 2:** Upload your source document here
                
                **Step 3:** Click "Extract & Auto-Fill MediRave"
                
                **Step 4:** Watch the magic happen in real-time!
                
                ### What Makes This Exciting:
                - **Live Cross-Application Updates** - See MediRave form fill as AI extracts
                - **Professional UI** - Window controls, gradients, realistic styling
                - **Instant Gratification** - Watch tedious work get automated
                """)


if __name__ == "__main__":
    main()