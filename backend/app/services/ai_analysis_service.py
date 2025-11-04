"""
AI Analysis Service
Gemini 2.0 Flash Integration

Provides document analysis using Google's Gemini AI
"""
import os
import time
import logging
from typing import Dict, Optional
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import json

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """Service for AI-powered document analysis"""
    
    def __init__(self):
        """Initialize Gemini AI"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment")
            self.model = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("Gemini AI initialized successfully")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text content
        """
        try:
            doc = DocxDocument(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """
        Extract text from file based on type
        
        Args:
            file_path: Path to file
            file_type: File extension (pdf, docx, dwg, etc)
            
        Returns:
            Extracted text content
        """
        file_type = file_type.lower()
        
        if file_type == "pdf":
            return self.extract_text_from_pdf(file_path)
        elif file_type in ["docx", "doc"]:
            return self.extract_text_from_docx(file_path)
        elif file_type == "dwg":
            # DWG files require special CAD libraries
            # For now, return placeholder
            return "[DWG file - CAD drawing. Text extraction not available]"
        else:
            logger.warning(f"Unsupported file type: {file_type}")
            return ""
    
    def analyze_document(
        self,
        file_path: str,
        file_type: str,
        filename: str
    ) -> Dict:
        """
        Analyze document using Gemini AI
        
        Args:
            file_path: Path to document file
            file_type: File extension
            filename: Original filename
            
        Returns:
            Analysis results dictionary
        """
        start_time = time.time()
        
        # Check if model is available
        if not self.model:
            return {
                "summary": "AI analysis unavailable - API key not configured",
                "extracted_data": "{}",
                "ocr_text": "",
                "key_entities": {},
                "confidence_score": 0.0,
                "processing_time": 0.0,
                "analyzed_by": "gemini-2.0-flash-exp (unavailable)"
            }
        
        try:
            # Extract text from document
            logger.info(f"Extracting text from {filename}")
            text_content = self.extract_text_from_file(file_path, file_type)
            
            if not text_content:
                return {
                    "summary": "Unable to extract text from document",
                    "extracted_data": "{}",
                    "ocr_text": "",
                    "key_entities": {},
                    "confidence_score": 0.0,
                    "processing_time": time.time() - start_time,
                    "analyzed_by": "gemini-2.0-flash-exp"
                }
            
            # Prepare prompt for Gemini
            prompt = f"""
Analyze the following document and provide:

1. A concise 3-sentence summary
2. Key data extracted (dates, numbers, names, etc.) in JSON format
3. Key entities (persons, companies, locations, dates) in JSON format
4. Confidence score (0-1) for the analysis quality

Document filename: {filename}
Document type: {file_type}

Document content:
{text_content[:10000]}  # Limit to first 10k chars

Please respond in the following JSON format:
{{
    "summary": "3-sentence summary here",
    "extracted_data": {{"key1": "value1", "key2": "value2"}},
    "key_entities": {{
        "persons": ["name1", "name2"],
        "companies": ["company1"],
        "locations": ["location1"],
        "dates": ["date1"]
    }},
    "confidence_score": 0.95
}}
"""
            
            # Call Gemini AI
            logger.info(f"Analyzing document with Gemini AI: {filename}")
            response = self.model.generate_content(prompt)
            
            # Parse response
            try:
                # Try to extract JSON from response
                response_text = response.text
                
                # Find JSON in response (might be wrapped in markdown)
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text
                
                analysis_result = json.loads(json_text)
                
                processing_time = time.time() - start_time
                
                return {
                    "summary": analysis_result.get("summary", "No summary available"),
                    "extracted_data": json.dumps(analysis_result.get("extracted_data", {})),
                    "ocr_text": text_content[:5000],  # Store first 5k chars
                    "key_entities": analysis_result.get("key_entities", {}),
                    "confidence_score": float(analysis_result.get("confidence_score", 0.85)),
                    "processing_time": processing_time,
                    "analyzed_by": "gemini-2.0-flash-exp"
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Gemini response: {e}")
                # Fallback: use raw response as summary
                processing_time = time.time() - start_time
                
                return {
                    "summary": response.text[:500] if response.text else "Analysis completed",
                    "extracted_data": "{}",
                    "ocr_text": text_content[:5000],
                    "key_entities": {},
                    "confidence_score": 0.75,
                    "processing_time": processing_time,
                    "analyzed_by": "gemini-2.0-flash-exp"
                }
        
        except Exception as e:
            logger.error(f"Error analyzing document: {e}", exc_info=True)
            processing_time = time.time() - start_time
            
            return {
                "summary": f"Error during analysis: {str(e)}",
                "extracted_data": "{}",
                "ocr_text": "",
                "key_entities": {},
                "confidence_score": 0.0,
                "processing_time": processing_time,
                "analyzed_by": "gemini-2.0-flash-exp (error)"
            }
    
    def is_available(self) -> bool:
        """Check if AI analysis is available"""
        return self.model is not None


# Singleton instance
ai_service = AIAnalysisService()
