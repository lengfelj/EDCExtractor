# EHR to EDC Data Transfer POC

An AI-powered proof of concept for automatically extracting clinical data from Electronic Health Records (EHR) and transferring it to Electronic Data Capture (EDC) systems.

## Overview

This POC demonstrates the capability to:
- Process various source documents (screenshots, PDFs, scanned documents)
- Extract lab results and vital signs using AI/LLM
- Automatically fill web-based EDC forms
- Validate and track data transfer confidence

## Features

- **Multi-format Document Support**: Handle screenshots, PDFs, and scanned medical documents
- **AI-Powered Extraction**: Use vision-language models to understand and extract clinical data
- **Focus Areas**: Lab results and vital signs
- **Web Automation**: Automatically populate EDC forms
- **Validation**: Built-in data validation and confidence scoring

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Source Data    │────▶│  AI Processing   │────▶│ Form Automation │
│ (PDF/Image/Doc) │     │  (GPT-4 Vision)  │     │  (Playwright)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │ Data Mapping │
                        │ & Validation │
                        └──────────────┘
```

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.env.example`)
4. Run the demo: `python src/main.py`

## Project Structure

```
EHR-to-EDC-POC/
├── src/
│   ├── extractors/      # Document processing modules
│   ├── processors/      # AI/LLM integration
│   ├── automation/      # Web form automation
│   ├── models/          # Data models
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── docs/                # Documentation
└── sample_data/         # Sample documents for testing
```


https://github.com/user-attachments/assets/8af3c165-964f-4e0c-89ac-e1722867bf5e


## License

This is a proof of concept for demonstration purposes.
