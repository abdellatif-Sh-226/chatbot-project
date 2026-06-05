import google.generativeai as genai

API_KEY = "YOUR_GEMINI_API_KEY_HERE"
MODEL = "gemini-2.0-flash"

try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content("Say hello in one word")
    print(f"SUCCESS: {response.text.strip()}")
except Exception as e:
    print(f"ERROR: {e}")
