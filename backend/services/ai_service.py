import cv2
import numpy as np
import pytesseract
from PIL import Image
import openai
import io
import base64
from typing import Dict, List, Optional, Tuple
import json
import requests
from google.cloud import vision
import tensorflow as tf
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import torch

from config.settings import settings

class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.vision_client = vision.ImageAnnotatorClient() if settings.GOOGLE_CLOUD_VISION_CREDENTIALS else None
        
        # Initialize BLIP model for image captioning
        try:
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        except:
            self.blip_processor = None
            self.blip_model = None
        
        # Initialize sentiment analysis
        try:
            self.sentiment_analyzer = pipeline("sentiment-analysis")
        except:
            self.sentiment_analyzer = None

    async def process_image(self, image_data: bytes, file_type: str) -> Dict:
        """Main image processing pipeline"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            extracted_text = await self._extract_text_ocr(processed_image)
            
            # Detect objects and scenes
            objects_detected = await self._detect_objects(processed_image)
            
            # Generate image caption
            caption = await self._generate_caption(processed_image)
            
            # Analyze and simplify content
            simplified_content = await self._simplify_content(extracted_text, caption)
            
            # Generate summary
            summary = await self._generate_summary(extracted_text, caption, objects_detected)
            
            return {
                "success": True,
                "extracted_text": extracted_text,
                "objects_detected": objects_detected,
                "caption": caption,
                "simplified_content": simplified_content,
                "summary": summary,
                "confidence_scores": {
                    "text_extraction": self._calculate_text_confidence(extracted_text),
                    "object_detection": self._calculate_object_confidence(objects_detected),
                    "caption_quality": self._calculate_caption_confidence(caption)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "extracted_text": "",
                "objects_detected": [],
                "caption": "",
                "simplified_content": "",
                "summary": ""
            }

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Enhance image quality for better OCR and analysis"""
        # Convert PIL to OpenCV
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoisingColored(opencv_image, None, 10, 10, 7, 21)
        
        # Enhance contrast
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Convert back to PIL
        return Image.fromarray(cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB))

    async def _extract_text_ocr(self, image: Image.Image) -> str:
        """Extract text from image using OCR"""
        try:
            # Try Tesseract first
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            # If Google Vision API is available, use it for better accuracy
            if self.vision_client and len(text.strip()) < 10:
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='PNG')
                image_bytes = image_bytes.getvalue()
                
                vision_image = vision.Image(content=image_bytes)
                response = self.vision_client.text_detection(image=vision_image)
                texts = response.text_annotations
                
                if texts:
                    text = texts[0].description
            
            return text.strip()
            
        except Exception as e:
            print(f"OCR error: {e}")
            return ""

    async def _detect_objects(self, image: Image.Image) -> List[Dict]:
        """Detect objects in the image"""
        objects = []
        
        try:
            # Use Google Vision API for object detection if available
            if self.vision_client:
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='PNG')
                image_bytes = image_bytes.getvalue()
                
                vision_image = vision.Image(content=image_bytes)
                response = self.vision_client.object_localization(image=vision_image)
                
                for obj in response.localized_object_annotations:
                    objects.append({
                        "name": obj.name,
                        "confidence": obj.score,
                        "bounding_box": {
                            "vertices": [
                                {"x": vertex.x, "y": vertex.y} 
                                for vertex in obj.bounding_poly.normalized_vertices
                            ]
                        }
                    })
            
            # Fallback to basic analysis
            if not objects:
                objects = await self._basic_object_detection(image)
                
        except Exception as e:
            print(f"Object detection error: {e}")
            
        return objects

    async def _basic_object_detection(self, image: Image.Image) -> List[Dict]:
        """Basic object detection using OpenCV"""
        try:
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Load pre-trained models (you would need to download these)
            # This is a simplified example
            objects = []
            
            # Face detection
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                objects.append({
                    "name": "face",
                    "confidence": 0.8,
                    "bounding_box": {
                        "x": x, "y": y, "width": w, "height": h
                    }
                })
            
            return objects
            
        except Exception as e:
            print(f"Basic object detection error: {e}")
            return []

    async def _generate_caption(self, image: Image.Image) -> str:
        """Generate descriptive caption for the image"""
        try:
            if self.blip_model and self.blip_processor:
                # Use BLIP model for image captioning
                inputs = self.blip_processor(image, return_tensors="pt")
                out = self.blip_model.generate(**inputs, max_length=50)
                caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
                return caption
            
            # Fallback to OpenAI Vision API if available
            elif self.openai_client:
                # Convert image to base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe this image in one concise sentence."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{img_str}"}
                                }
                            ]
                        }
                    ],
                    max_tokens=100
                )
                return response.choices[0].message.content
            
            return "Image uploaded successfully"
            
        except Exception as e:
            print(f"Caption generation error: {e}")
            return "Image analysis completed"

    async def _simplify_content(self, text: str, caption: str) -> str:
        """Simplify and explain complex content"""
        if not text and not caption:
            return "No text content to simplify."
        
        try:
            if self.openai_client:
                content = f"Text from image: {text}\nImage description: {caption}"
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI assistant that simplifies complex content. Make text easy to understand using simple language and clear explanations."
                        },
                        {
                            "role": "user",
                            "content": f"Please simplify and explain this content in easy-to-understand language:\n\n{content}"
                        }
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content
            
            # Basic simplification fallback
            if text:
                sentences = text.split('.')
                simplified = []
                for sentence in sentences[:3]:  # Take first 3 sentences
                    if len(sentence.strip()) > 10:
                        simplified.append(sentence.strip() + ".")
                return " ".join(simplified)
            
            return caption
            
        except Exception as e:
            print(f"Content simplification error: {e}")
            return text or caption

    async def _generate_summary(self, text: str, caption: str, objects: List[Dict]) -> str:
        """Generate comprehensive summary of image content"""
        try:
            if self.openai_client:
                object_names = [obj['name'] for obj in objects]
                
                prompt = f"""
                Create a comprehensive summary of this image based on:
                - Extracted text: {text}
                - Visual description: {caption}
                - Objects detected: {', '.join(object_names)}
                
                Provide a clear, informative summary in 2-3 sentences.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an AI that creates concise, informative summaries."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                return response.choices[0].message.content
            
            # Fallback summary
            parts = []
            if caption:
                parts.append(f"Image shows: {caption}")
            if text:
                parts.append(f"Contains text: {text[:100]}...")
            if objects:
                parts.append(f"Objects detected: {', '.join([obj['name'] for obj in objects[:3]])}")
            
            return ". ".join(parts) if parts else "Image processed successfully."
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return "Image analysis completed with extracted content."

    def _calculate_text_confidence(self, text: str) -> float:
        """Calculate confidence score for text extraction"""
        if not text:
            return 0.0
        
        # Simple heuristic based on text length and character variety
        confidence = min(len(text) / 100, 1.0)  # Normalize by expected length
        
        # Boost confidence if text has good structure
        if any(char.isalnum() for char in text):
            confidence += 0.2
        if '.' in text or ',' in text:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _calculate_object_confidence(self, objects: List[Dict]) -> float:
        """Calculate average confidence for object detection"""
        if not objects:
            return 0.0
        
        confidences = [obj.get('confidence', 0.5) for obj in objects]
        return sum(confidences) / len(confidences)

    def _calculate_caption_confidence(self, caption: str) -> float:
        """Calculate confidence score for caption quality"""
        if not caption:
            return 0.0
        
        # Simple heuristic based on caption completeness
        word_count = len(caption.split())
        confidence = min(word_count / 10, 1.0)  # Normalize by expected word count
        
        return confidence

    async def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of extracted text"""
        try:
            if self.sentiment_analyzer and text:
                result = self.sentiment_analyzer(text)
                return {
                    "label": result[0]['label'],
                    "score": result[0]['score']
                }
            return {"label": "NEUTRAL", "score": 0.5}
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {"label": "NEUTRAL", "score": 0.5}

    async def generate_contextual_response(self, image_content: Dict, user_message: str) -> str:
        """Generate contextual response based on image content and user query"""
        try:
            if not self.openai_client:
                return "I can see your image, but I need OpenAI API access to provide detailed responses."
            
            context = f"""
            Image Analysis:
            - Text extracted: {image_content.get('extracted_text', 'None')}
            - Description: {image_content.get('caption', 'None')}
            - Objects detected: {', '.join([obj['name'] for obj in image_content.get('objects_detected', [])])}
            - Summary: {image_content.get('summary', 'None')}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that helps users understand and work with image content. Use the provided image analysis to answer questions and provide helpful insights."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this image analysis:\n{context}\n\nUser question: {user_message}"
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Contextual response error: {e}")
            return "I understand your question about the image. Could you be more specific about what you'd like to know?"