from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os
import json
from typing import Dict, Any, Optional
from tripcraft_config import extract_json_from_text, validate_itinerary_json

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

USE_OPENAI_FALLBACK = os.getenv("OPENAI_API_KEY") is not None

# Load tokenizer & model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
)

def format_chat_prompt(user_prompt: str, system_prompt: Optional[str] = None) -> str:
    """Format prompt for TinyLlama chat model"""
    if system_prompt is None:
        system_prompt = "You are TripCraft, a professional travel itinerary assistant. Generate detailed, realistic travel plans in valid JSON format."

    return f"""<|system|>
{system_prompt}
<|user|>
{user_prompt}
<|assistant|>"""


# Create text-generation pipeline
llm_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=800,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id
)

def llm(prompt: str, system_prompt: Optional[str] = None, return_json: bool = True) -> str:
    """Generate response using TinyLlama or OpenAI fallback.

    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt override
        return_json: If True, attempt to extract and validate JSON

    Returns:
        Generated text or JSON string
    """
    if USE_OPENAI_FALLBACK:
        return llm_with_openai(prompt, system_prompt, return_json)

    chat_prompt = format_chat_prompt(prompt, system_prompt)
    outputs = llm_pipeline(chat_prompt, return_full_text=False)
    generated_text = outputs[0]["generated_text"].strip()

    if return_json:
        try:
            json_data = extract_json_from_text(generated_text)
            return json.dumps(json_data, indent=2)
        except Exception:
            return generated_text

    return generated_text


def llm_with_openai(prompt: str, system_prompt: Optional[str] = None, return_json: bool = True) -> str:
    """Fallback to OpenAI API when available"""
    try:
        import openai

        openai.api_key = os.getenv("OPENAI_API_KEY")

        if system_prompt is None:
            system_prompt = "You are TripCraft, a professional travel itinerary assistant."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        generated_text = response.choices[0].message.content.strip()

        if return_json:
            try:
                json_data = extract_json_from_text(generated_text)
                return json.dumps(json_data, indent=2)
            except Exception:
                return generated_text

        return generated_text

    except ImportError:
        raise Exception("OpenAI API key is set but 'openai' package is not installed. Run: pip install openai")
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
