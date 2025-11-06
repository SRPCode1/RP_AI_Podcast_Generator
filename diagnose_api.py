import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

print("="*60)
print("GEMINI API DIAGNOSE")
print("="*60)

# 1. Load API Key
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("✗ GEMINI_API_KEY nicht gefunden in .env")
    exit(1)
else:
    print(f"✓ API Key gefunden (erste 10 Zeichen): {api_key[:10]}...")

# 2. Initialize Client
try:
    client = genai.Client(api_key=api_key)
    print("✓ Client initialisiert")
except Exception as e:
    print(f"✗ Client-Initialisierung fehlgeschlagen: {e}")
    exit(1)

# 3. List available models
print("\n" + "-"*60)
print("VERFÜGBARE MODELLE:")
print("-"*60)
try:
    models = client.models.list()
    tts_models = [m for m in models if 'tts' in m.name.lower()]
    print(f"✓ Gefunden: {len(list(models))} Modelle insgesamt")
    print(f"✓ Davon TTS-Modelle: {len(tts_models)}")
    for m in tts_models[:5]:
        print(f"  - {m.name}")
except Exception as e:
    print(f"✗ Fehler beim Abrufen der Modelle: {e}")

# 4. Test a simple text generation (no TTS)
print("\n" + "-"*60)
print("TEST 1: Einfache Text-Generierung")
print("-"*60)
try:
    response = client.models.generate_content(
        model="models/gemini-2.0-flash-exp",
        contents="Say hello in one word"
    )
    print(f"✓ Text-Generierung erfolgreich: {response.text}")
except Exception as e:
    print(f"✗ Text-Generierung fehlgeschlagen: {e}")
    print(f"   Fehlertyp: {type(e).__name__}")

# 5. Test TTS with minimal request
print("\n" + "-"*60)
print("TEST 2: Mini TTS-Request (10 Wörter)")
print("-"*60)

test_models = [
    "models/gemini-2.5-pro-preview-tts",
    "models/gemini-2.5-flash-preview-tts"
]

for model_name in test_models:
    print(f"\nTeste Modell: {model_name}")
    try:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Speaker 1: Hello, this is a test.")],
            ),
        ]
        
        config = types.GenerateContentConfig(
            temperature=1,
            response_modalities=["audio"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker="Speaker 1",
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Sulafat"
                                )
                            ),
                        ),
                    ]
                ),
            ),
        )
        
        # Try non-streaming first
        print("  Versuche non-streaming...")
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config
        )
        
        if hasattr(response, 'candidates') and response.candidates:
            print(f"  ✓ Non-streaming TTS erfolgreich mit {model_name}")
            print(f"    Response hat candidates: {len(response.candidates)}")
            break
        else:
            print(f"  ⚠ Response ohne audio data")
            
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        print(f"     Fehlertyp: {type(e).__name__}")
        if hasattr(e, 'status_code'):
            print(f"     Status Code: {e.status_code}")
        if hasattr(e, 'message'):
            print(f"     Message: {e.message}")

print("\n" + "="*60)
print("DIAGNOSE ABGESCHLOSSEN")
print("="*60)