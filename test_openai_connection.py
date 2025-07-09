#!/usr/bin/env python3
"""
Test OpenAI API connectivity and vision model access
"""

import os
import sys
import base64
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test OpenAI API connectivity"""
    print("🔍 Testing OpenAI Connection...")
    print("=" * 50)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: No OpenAI API key found in .env file")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ ERROR: Invalid API key format (should start with 'sk-')")
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    # Initialize client
    try:
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize OpenAI client: {e}")
        return False
    
    # Test basic text model
    print("\n📝 Testing basic text model...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello! Just testing connectivity."}],
            max_tokens=10
        )
        print("✅ Basic text model works")
        print(f"   Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ ERROR: Basic text model failed: {e}")
        return False
    
    # Test vision model with a simple image
    print("\n👁️  Testing vision model...")
    try:
        # Create a simple test image (100x100 pixel white PNG)
        from PIL import Image
        import io
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        test_image_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What do you see in this image?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{test_image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=50
        )
        print("✅ Vision model works!")
        print(f"   Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ ERROR: Vision model failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"   Status code: {e.status_code}")
        return False
    
    # Test account usage/limits
    print("\n💳 Testing account access...")
    try:
        # Try to list available models
        models = client.models.list()
        vision_models = [m for m in models.data if 'gpt-4' in m.id and 'vision' in m.id or 'gpt-4o' in m.id]
        print(f"✅ Account active, found {len(vision_models)} vision-capable models")
        for model in vision_models[:3]:  # Show first 3
            print(f"   - {model.id}")
    except Exception as e:
        print(f"⚠️  WARNING: Could not check models: {e}")
    
    print("\n🎉 OpenAI connectivity test PASSED!")
    return True

def test_clinical_extraction():
    """Test clinical data extraction specifically"""
    print("\n🏥 Testing clinical data extraction...")
    
    # Add the src directory to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        from processors.ai_extractor import AIExtractor
        
        # Create a simple test image (white background)
        from PIL import Image
        import io
        img = Image.new('RGB', (100, 100), color='white')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        test_image = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        extractor = AIExtractor()
        
        # Test with a simple prompt
        response = extractor.client.chat.completions.create(
            model=extractor.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Test message for clinical extraction"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{test_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=20
        )
        
        print("✅ Clinical extraction setup works!")
        print(f"   Model: {extractor.model}")
        print(f"   Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ ERROR: Clinical extraction failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_openai_connection()
    if success:
        test_clinical_extraction()
    else:
        print("\n❌ OpenAI connectivity test FAILED!")
        sys.exit(1)