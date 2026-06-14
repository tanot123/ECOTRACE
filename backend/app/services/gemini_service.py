import google.generativeai as genai
import json
import base64
from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
# Use a multimodal model, e.g., gemini-2.5-flash which is fast and supports images
# We will use gemini-2.5-flash as it is the standard vision model currently.
model = genai.GenerativeModel('gemini-2.5-flash')

class GeminiService:
    @staticmethod
    async def analyze_image(image_bytes: bytes, scan_type: str, mime_type: str = "image/jpeg") -> dict:
        image_part = {
            "mime_type": mime_type,
            "data": base64.b64encode(image_bytes).decode('utf-8')
        }

        if scan_type == "receipt":
            prompt = """
            You are an expert sustainability advisor and waste management specialist.
            Analyze this grocery receipt image and extract all purchased items.
            For each item, provide recycling and sustainability information.

            Respond ONLY with valid JSON in this exact format, with no markdown formatting or extra text:
            {
              "store_name": "string or null",
              "date": "YYYY-MM-DD or null",
              "items": [
                {
                  "name": "item name as shown on receipt",
                  "quantity": 1,
                  "packaging_type": "plastic | cardboard | glass | metal | paper | mixed | none",
                  "recyclable": true,
                  "compostable": false,
                  "recycling_instruction": "specific instruction for this item's packaging",
                  "eco_tip": "optional sustainability tip for this product category",
                  "bin_color": "blue"
                }
              ],
              "trip_sustainability_score": 8,
              "overall_tips": ["array of general sustainability tips based on this shopping trip"]
            }
            Rules:
            - If you cannot read an item clearly, skip it.
            - bin_color: blue=recycling, green=compost, black=landfill, special=needs special disposal.
            - If the image is not a receipt, respond with: {"error": "NOT_A_RECEIPT", "message": "Not a receipt"}
            """
        elif scan_type == "packaging":
            prompt = """
            You are an expert waste management and recycling specialist.
            Analyze this image of product packaging or material.

            Respond ONLY with valid JSON in this exact format, with no markdown formatting or extra text:
            {
              "material_type": "plastic_#1_PET | cardboard | glass_clear | etc",
              "material_name": "human-readable material name",
              "recyclable": true,
              "compostable": false,
              "recycling_symbol": "♻️ 1",
              "bin_color": "blue",
              "disposal_instructions": ["Step 1", "Step 2"],
              "environmental_impact": {
                "decomposition_time": "450 years",
                "better_alternative": "Use reusable bags",
                "fun_fact": "A fun fact"
              },
              "confidence": "high"
            }
            Rules:
            - If not packaging/material, respond with: {"error": "NOT_PACKAGING", "message": "..."}
            """
        else: # barcode
            prompt = """
            You are a product identification and sustainability expert.
            Analyze this image of a product barcode or label.

            Respond ONLY with valid JSON in this exact format, with no markdown formatting or extra text:
            {
              "barcode_number": "string or null",
              "product_name": "identified product name",
              "brand": "brand name or null",
              "category": "food | beverage | household",
              "packaging_materials": [
                {
                  "component": "bottle",
                  "material": "plastic",
                  "recyclable": true,
                  "instruction": "rinse and recycle"
                }
              ],
              "overall_recyclable": true,
              "compostable": false,
              "bin_color": "blue",
              "eco_rating": 3,
              "sustainable_alternative": "suggestion or null",
              "confidence": "high"
            }
            Rules:
            - If not a product/barcode, respond with: {"error": "NOT_A_PRODUCT", "message": "..."}
            """

        response = await model.generate_content_async([prompt, image_part])
        
        # Clean response string (remove ```json wrappers if Gemini accidentally includes them)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        return json.loads(text)
