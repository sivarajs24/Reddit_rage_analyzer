import os
import json
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

# We'll use LLaMA 3.3 70B via Groq which is blazing fast and excellent at JSON
MODEL_NAME = 'llama-3.3-70b-versatile'

class AnalysisResult(BaseModel):
    most_hated_features: List[str] = Field(description="List of the most hated features")
    common_bug_patterns: List[str] = Field(description="List of common bug patterns")
    emotional_intensity: str = Field(description="Emotional intensity: High/Medium/Low")
    overall_sentiment: str = Field(description="Overall sentiment: Positive/Neutral/Negative/Very Negative")
    key_recurring_complaints: List[str] = Field(description="List of key recurring complaints")
    summary_paragraph: str = Field(description="A professional 3-4 sentence summary of the general consensus and main issues")
    top_keywords: List[str] = Field(description="List of top keywords associated with the complaints")

def analyze_complaints(product_name: str, retrieved_docs: list) -> dict:
    """
    Analyzes the retrieved Reddit complaints using Groq API and returns a structured JSON result.
    """
    if not retrieved_docs:
        return {"error": "No documents provided for analysis."}
        
    if not os.getenv("GROQ_API_KEY"):
        return {"error": "GROQ_API_KEY is not set in .env."}

    # Compile documents into a single text block
    context = ""
    for i, doc in enumerate(retrieved_docs):
        context += f"--- Complaint {i+1} ---\n"
        context += f"{doc.page_content}\n\n"

    # Define the prompt for Groq
    prompt = f"""
    You are an expert AI product analyst. Your task is to analyze the following Reddit complaints about the product '{product_name}'.
    
    Based ONLY on the complaints provided below, generate a comprehensive analysis and return the result as a strictly formatted JSON object. 
    The JSON structure MUST exactly match the following schema:
    {AnalysisResult.model_json_schema()}
    
    --- COMPLAINTS DATA ---
    {context}
    """

    try:
        # Initialize Groq client
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that only outputs strictly valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result_text = chat_completion.choices[0].message.content
        result_json = json.loads(result_text)
        
        # Validate against Pydantic model to ensure structure
        validated_result = AnalysisResult(**result_json)
        return validated_result.model_dump()

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Groq response: {e}")
        return {"error": "Failed to parse AI response into JSON format."}
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {"error": str(e)}
