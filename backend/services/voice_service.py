"""
Voice AI Service Module for KisanSetu
Supports Multilingual Speech-to-Text (STT), Structured Agronomic Entity Extraction,
Conversational Follow-up Management, and Text-to-Speech (TTS).
"""

import os
import io
import re
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
import speech_recognition as sr
from gtts import gTTS

logger = logging.getLogger("voice_service")

# Language mappings for STT / TTS
LANG_CONFIGS = {
    "en": {"stt_code": "en-IN", "gtts_code": "en", "name": "English"},
    "hi": {"stt_code": "hi-IN", "gtts_code": "hi", "name": "हिंदी (Hindi)"},
    "gu": {"stt_code": "gu-IN", "gtts_code": "gu", "name": "ગુજરાતી (Gujarati)"},
    "mr": {"stt_code": "mr-IN", "gtts_code": "mr", "name": "मराठी (Marathi)"},
    "te": {"stt_code": "te-IN", "gtts_code": "te", "name": "తెలుగు (Telugu)"},
    "ta": {"stt_code": "ta-IN", "gtts_code": "ta", "name": "தமிழ் (Tamil)"},
    "bn": {"stt_code": "bn-IN", "gtts_code": "bn", "name": "বাংলা (Bengali)"},
    "pa": {"stt_code": "pa-IN", "gtts_code": "pa", "name": "ਪੰਜਾਬੀ (Punjabi)"},
    "kn": {"stt_code": "kn-IN", "gtts_code": "kn", "name": "ಕನ್ನಡ (Kannada)"}
}

# Conversational follow-up prompts for missing fields
MISSING_FIELD_PROMPTS = {
    "crop_name": {
        "en": "Which crop are you cultivating this season? (e.g., Tomato, Cotton, Soybean, Wheat, Onion)",
        "hi": "आप इस मौसम में कौन सी फसल उगा रहे हैं? (उदा. टमाटर, कपास, सोयाबीन, गेहूं, प्याज)",
        "gu": "તમે આ સિઝનમાં કયો પાક વાવી રહ્યા છો? (દા.ત. ટામેટા, કપાસ, સોયાબીન, ઘઉં, ડુંગળી)",
        "mr": "तुम्ही या हंगामात कोणते पीक घेत आहात? (उदा. टोमॅटो, कापूस, सोयाबीन, गहू, कांदा)",
        "te": "మీరు ఈ సీజన్‌లో ఏ పంట సాగు చేస్తున్నారు? (ఉదా. టమాటా, పత్తి, సోయాబీన్, గోధుమ, ఉల్లిపాయ)",
        "ta": "இந்த பருவத்தில் நீங்கள் என்ன பயிர் பயிரிடுகிறீர்கள்? (எ.கா. தக்காளி, பருத்தி, சோயாபீன், கோதுமை, வெங்காயம்)",
        "bn": "আপনি এই মরসুমে কোন ফসল চাষ করছেন? (যেমন টমেটো, তুলা, সয়াবিন, গম, পেঁয়াজ)",
        "pa": "ਤੁਸੀਂ ਇਸ ਸੀਜ਼ਨ ਵਿੱਚ ਕਿਹੜੀ ਫ਼ਸਲ ਉਗਾ ਰਹੇ ਹੋ? (ਜਿਵੇਂ ਟਮਾਟਰ, ਕਪਾਹ, ਸੋਇਆਬੀਨ, ਕਣਕ, ਪਿਆਜ਼)",
        "kn": "ನೀವು ಈ ಋತುವಿನಲ್ಲಿ ಯಾವ ಬೆಳೆಯನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? (ಉದಾ. ಟೊಮೆಟೊ, ಹತ್ತಿ, ಸೋಯಾಬೀನ್, ಗೋಧಿ, ಈರುಳ್ಳಿ)"
    },
    "land_acres": {
        "en": "How many acres of land are you cultivating? (e.g., 1.5 acres, 2 acres)",
        "hi": "आपके पास कितने एकड़ कृषि भूमि है? (उदा. 1.5 एकड़, 2 एकड़)",
        "gu": "તમારી પાસે કેટલા એકર ખેતીની જમીન છે? (દા.ત. ૧.૫ એકર, ૨ એકર)",
        "mr": "तुमच्याकडे किती एकर शेती जमीन आहे? (उदा. १.५ एकर, २ एकर)",
        "te": "మీరు ఎన్ని ఎకరాలలో సాగు చేస్తున్నారు? (ఉదా. 1.5 ఎకరాలు, 2 ఎకరాలు)",
        "ta": "நீங்கள் எத்தனை ஏக்கரில் பயிரிடுகிறீர்கள்? (எ.கா. 1.5 ஏக்கர், 2 ஏக்கர்)",
        "bn": "আপনার কত একর জমি চাষের অধীনে আছে? (যেমন ১.৫ একর, ২ একর)",
        "pa": "ਤੁਹਾਡੇ ਕੋਲ ਕਿੰਨੇ ਏਕੜ ਜ਼ਮੀਨ ਹੈ? (ਜਿਵੇਂ 1.5 ਏਕੜ, 2 ਏਕੜ)",
        "kn": "ನೀವು ಎಷ್ಟು ಎಕರೆ ಜಮೀನಿನಲ್ಲಿ ಕೃಷಿ ಮಾಡುತ್ತಿದ್ದೀರಿ? (ಉದಾ. 1.5 ಎಕರೆ, 2 ಎಕರೆ)"
    },
    "district": {
        "en": "In which district is your farm located? (e.g., Nashik, Guntur, Kolar, Agra, Salem)",
        "hi": "आपका खेत किस जिले में स्थित है? (उदा. नासिक, गुंटूर, कोलार, आगरा, सेलम)",
        "gu": "તમારું ખેતર કયા જિલ્લામાં આવેલું છે? (દા.ત. નાસિક, ગુંટૂર, કોલાર, આગ્રા, સેલમ)",
        "mr": "आपले शेत कोणत्या जिल्ह्यात आहे? (उदा. नाशिक, गुंटूर, कोलार, आग्रा, सेलम)",
        "te": "మీ పొలం ఏ జిల్లాలో ఉంది? (ఉదా. నాసిక్, గుంటూరు, కోలార్, ఆగ్రా, సేలం)",
        "ta": "உங்கள் பண்ணை எந்த மாவட்டத்தில் உள்ளது? (எ.கா. நாசிக், குண்டூர், கோலார், ஆக்ரா, சேலம்)",
        "bn": "আপনার খামারটি কোন জেলায় অবস্থিত? (যেমন নাসিক, গুন্টুর, কোলার, আগ্রা, সালেম)",
        "pa": "ਤੁਹਾਡਾ ਖੇਤ ਕਿਸ ਜ਼ਿਲ੍ਹੇ ਵਿੱਚ ਹੈ? (ਜਿਵੇਂ ਨਾਸਿਕ, ਗੁੰਟੂਰ, ਕੋਲਾਰ, ਆਗਰਾ, ਸਲੇਮ)",
        "kn": "ನಿಮ್ಮ ಜಮೀನು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿದೆ? (ಉದಾ. ನಾಸಿಕ್, ಗುಂಟೂರು, ಕೋಲಾರ, ಆಗ್ರಾ, ಸೇಲಂ)"
    },
    "expected_yield_qtl_acre": {
        "en": "What is your expected yield per acre in quintals? (e.g., 18 quintals per acre)",
        "hi": "प्रति एकड़ आपकी अनुमानित पैदावार कितने क्विंटल है? (उदा. 18 क्विंटल प्रति एकड़)",
        "gu": "પ્રતિ એકર તમારી અંદાજિત ઉપજ કેટલા ક્વિન્ટલ છે? (દા.ત. ૧૮ ક્વિન્ટલ પ્રતિ એકર)",
        "mr": "प्रति एकर आपले अंदाजे उत्पादन किती क्विंटल आहे? (उदा. १८ क्विंटल प्रति एकर)",
        "te": "ఎకరాకు మీ అంచనా దిగుబడి ఎన్ని క్వింటాళ్లు? (ఉదా. 18 క్వింటాళ్లు)",
        "ta": "ஒரு ஏக்கருக்கு உங்கள் எதிர்பார்க்கப்படும் விளைச்சல் எத்தனை குவிண்டால்? (எ.கா. 18 குவிண்டால்)",
        "bn": "প্রতি একরে আপনার আনুমানিক ফলন কত কুইন্টাল? (যেমন ১৮ কুইন্টাল)",
        "pa": "ਪ੍ਰਤੀ ਏਕੜ ਤੁਹਾਡੀ ਅਨੁਮਾਨਿਤ ਪੈਦਾਵਾਰ ਕਿੰਨੇ ਕੁਇੰਟਲ ਹੈ? (ਜਿਵੇਂ 18 ਕੁਇੰਟਲ)",
        "kn": "ಪ್ರತಿ ಎಕರೆಗೆ ನಿಮ್ಮ ನಿರೀಕ್ಷಿತ ಇಳುವರಿ ಎಷ್ಟು ಕ್ವಿಂಟಾಲ್‌ಗಳು? (ಉದಾ. 18 ಕ್ವಿಂಟಾಲ್‌ಗಳು)"
    }
}

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.openai_client = None
        if self.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}")

    def transcribe_audio(self, audio_bytes: bytes, lang_code: str = "en", filename: str = "audio.wav") -> Dict[str, Any]:
        """
        Transcribe audio bytes using OpenAI Whisper (if configured) or Google Speech Recognition fallback.
        """
        if not audio_bytes or len(audio_bytes) < 100:
            return {
                "success": False,
                "error": "Empty or corrupted audio recording. Please speak clearly into your microphone.",
                "transcript": "",
                "provider": "none"
            }

        lang_info = LANG_CONFIGS.get(lang_code, LANG_CONFIGS["en"])

        # 1. Try OpenAI Whisper if API key available
        if self.openai_client:
            try:
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = filename
                res = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=lang_code if lang_code != "en" else "en"
                )
                text = res.text.strip()
                if text:
                    return {
                        "success": True,
                        "transcript": text,
                        "provider": "OpenAI Whisper-1",
                        "language": lang_info["name"]
                    }
            except Exception as e:
                logger.warning(f"Whisper transcription failed, falling back to Google Speech: {e}")

        # 2. Try Google Speech Recognition via speech_recognition package
        try:
            audio_file = io.BytesIO(audio_bytes)
            with sr.AudioFile(audio_file) as source:
                # Adjust for ambient noise and record
                audio_data = self.recognizer.record(source)
                stt_lang = lang_info["stt_code"]
                transcript = self.recognizer.recognize_google(audio_data, language=stt_lang)
                if transcript and len(transcript.strip()) > 0:
                    return {
                        "success": True,
                        "transcript": transcript.strip(),
                        "provider": "Google Speech Recognition",
                        "language": lang_info["name"]
                    }
        except sr.UnknownValueError:
            return {
                "success": False,
                "error": "Audio could not be understood. Please speak a bit louder and closer to the microphone.",
                "transcript": "",
                "provider": "Google Speech Recognition"
            }
        except sr.RequestError as e:
            return {
                "success": False,
                "error": f"Speech recognition service request error: {str(e)}",
                "transcript": "",
                "provider": "Google Speech Recognition"
            }
        except Exception as e:
            logger.error(f"STT Error: {e}")
            return {
                "success": False,
                "error": f"Audio processing error: {str(e)}",
                "transcript": "",
                "provider": "local_audio_engine"
            }

        return {
            "success": False,
            "error": "No speech detected in the audio file.",
            "transcript": "",
            "provider": "none"
        }

    def extract_agronomic_entities(self, transcript: str, current_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Converts unstructured multilingual farmer speech transcript into validated structured fields.
        Does NOT compute credit limits or scores; only extracts verified data fields.
        """
        extracted = dict(current_data) if current_data else {
            "farmer_name": "Ramesh Tukaram Patil",
            "district": "",
            "crop_name": "",
            "land_acres": None,
            "expected_yield_qtl_acre": None,
            "selling_price_per_qtl": None,
            "estimated_expenses_inr": None,
            "existing_loan_obligations_inr": None,
            "irrigation": "Drip"
        }

        if not transcript or not transcript.strip():
            return {
                "extracted_fields": extracted,
                "missing_fields": self._get_missing_fields(extracted),
                "confidence": 0.0,
                "raw_transcript": transcript
            }

        text = transcript.strip()
        indic_to_ascii = str.maketrans({
            '\u0966': '0', '\u0967': '1', '\u0968': '2', '\u0969': '3', '\u096A': '4',
            '\u096B': '5', '\u096C': '6', '\u096D': '7', '\u096E': '8', '\u096F': '9',
            '\u0AE6': '0', '\u0AE7': '1', '\u0AE8': '2', '\u0AE9': '3', '\u0AEA': '4',
            '\u0AEB': '5', '\u0AEC': '6', '\u0AED': '7', '\u0AEE': '8', '\u0AEF': '9',
            '\u09E6': '0', '\u09E7': '1', '\u09E8': '2', '\u09E9': '3', '\u09EA': '4',
            '\u09EB': '5', '\u09EC': '6', '\u09ED': '7', '\u09EE': '8', '\u09EF': '9',
            '\u0A66': '0', '\u0A67': '1', '\u0A68': '2', '\u0A69': '3', '\u0A6A': '4',
            '\u0A6B': '5', '\u0A6C': '6', '\u0A6D': '7', '\u0A6E': '8', '\u0A6F': '9',
            '\u0C66': '0', '\u0C67': '1', '\u0C68': '2', '\u0C69': '3', '\u0C6A': '4',
            '\u0C6B': '5', '\u0C6C': '6', '\u0C6D': '7', '\u0C6E': '8', '\u0C6F': '9',
            '\u0CE6': '0', '\u0CE7': '1', '\u0CE8': '2', '\u0CE9': '3', '\u0CEA': '4',
            '\u0CEB': '5', '\u0CEC': '6', '\u0CED': '7', '\u0CEE': '8', '\u0CEF': '9',
            '\u0BE6': '0', '\u0BE7': '1', '\u0BE8': '2', '\u0BE9': '3', '\u0BEA': '4',
            '\u0BEB': '5', '\u0BEC': '6', '\u0BED': '7', '\u0BEE': '8', '\u0BEF': '9',
        })
        text = text.translate(indic_to_ascii)
        lower = text.lower()

        # 1. Crop Detection (Multilingual across 9 languages)
        crop_definitions = [
            ("Tomato", ["tomato", "tamatar", "टमाटर", "ટામેટા", "टोमॅटो", "టమాటా", "தக்காளி", "টমেটো", "ਟਮਾਟਰ", "ಟೊಮೆಟೊ"]),
            ("Cotton", ["cotton", "kapas", "kapaas", "कपास", "કપાસ", "कापूस", "పత్తి", "பருத்தி", "তুলা", "ਕਪਾਹ", "ಹತ್ತಿ"]),
            ("Soybean", ["soybean", "soya", "सोयाबीन", "સોયાબીન", "సోయాబీన్", "சோயாபீன்", "সয়াবিন", "ਸੋਇਆਬੀਨ", "ಸೋಯಾಬೀನ್"]),
            ("Wheat", ["wheat", "gehun", "gehu", "गेहूं", "ઘઉં", "गहू", "గోధుమ", "கோதுமை", "গম", "ਕਣਕ", "ಗೋಧಿ"]),
            ("Onion", ["onion", "pyaz", "kanda", "कांदा", "प्याज", "ડુંગળી", "ఉల్లిపాయ", "வெங்காயம்", "পেঁয়াজ", "ਪਿਆਜ਼", "ಈರುಳ್ಳಿ"]),
            ("Chilli (Dry)", ["chilli", "chili", "mirchi", "मिर्च", "મરચાં", "मिरची", "మిర్చి", "மிளகாய்", "মরিচ", "ਮਿਰਚ", "ಮೆಣಸಿನಕಾಯಿ"]),
            ("Potato", ["potato", "aloo", "alu", "बटाटा", "आलू", "બટાકા", "ఆలూ", "உருளைக்கிழங்கு", "আলু", "ਆਲੂ", "ಆಲೂಗಡ್ಡೆ"]),
            ("Grapes", ["grapes", "angoor", "द्राक्ष", "દ્રાક્ષ", "ద్రాక్ష", "திராட்சை", "আঙুর", "ਅੰਗੂਰ", "ದ್ರಾಕ್ಷಿ"]),
            ("Turmeric", ["turmeric", "haldi", "हळद", "હળદર", "పసుపు", "மஞ்சள்", "হলুদ", "ਹਲਦੀ", "ಅರಿಶಿನ"])
        ]

        for crop_name, keywords in crop_definitions:
            if any(k in lower for k in keywords):
                extracted["crop_name"] = crop_name
                break

        # 2. District Detection
        district_definitions = [
            ("Maharashtra_Nashik", ["nashik", "nasik", "नासिक", "नाशिक", "નાસિક", "నాసిక్", "நாசிக்", "নাসিক", "ਨਾਸਿਕ", "ನಾಸಿಕ್"]),
            ("Andhra Pradesh_Guntur", ["guntur", "गुंटूर", "ગુંટૂર", "గుంటూరు", "குண்டூர்", "গুন্টুর", "ਗੁੰਟੂਰ", "ಗುಂಟೂರು"]),
            ("Karnataka_Kolar", ["kolar", "कोलार", "કોલાર", "కోలార్", "கோலார்", "কোলার", "ਕੋਲਾਰ", "ಕೋಲಾರ"]),
            ("Uttar Pradesh_Agra", ["agra", "आगरा", "આગ્રા", "ఆగ్రా", "ஆக்ரா", "আগ্রা", "ਆਗਰਾ", "ಆಗ್ರಾ"]),
            ("Tamil Nadu_Salem", ["salem", "सेलम", "સેલમ", "సేలం", "சேலம்", "সালেম", "ਸਲੇਮ", "ಸೇಲಂ"])
        ]

        for dist_key, keywords in district_definitions:
            if any(k in lower for k in keywords):
                extracted["district"] = dist_key
                break

        # 3. Acres Detection (Spoken numbers & decimal numbers)
        # Match "1.5 acres", "2 acre", "दोध एकड़", "२ एकर", etc.
        acre_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:acres?|acre|एकड़|એકર|एकर|ఎకరా[లు|ల]?|ஏக்கர்|একর|ਏਕੜ|ಎಕರೆ)', lower)
        if acre_match:
            try:
                extracted["land_acres"] = float(acre_match.group(1))
            except Exception:
                pass
        else:
            # Word numbers in regional speech
            word_numbers = {
                "one": 1.0, "two": 2.0, "three": 3.0, "half": 0.5, "one and half": 1.5, "two and half": 2.5,
                "एक": 1.0, "दो": 2.0, "तीन": 3.0, "डेढ़": 1.5, "ढाई": 2.5,
                "એક": 1.0, "બે": 2.0, "દોઢ": 1.5, "અઢી": 2.5,
                "एक": 1.0, "दोन": 2.0, "दीड": 1.5, "अडीच": 2.5,
                "ఒకటి": 1.0, "రెండు": 2.0, "ఒకటిన్నర": 1.5,
                "ஒன்று": 1.0, "இரண்டு": 2.0, "ஒன்றரை": 1.5,
                "এক": 1.0, "দুই": 2.0, "দেড়": 1.5,
                "ਇੱਕ": 1.0, "ਦੋ": 2.0, "ਡੇਢ": 1.5,
                "ಒಂದು": 1.0, "ಎರಡು": 2.0, "ಒಂದೂವರೆ": 1.5
            }
            for word, val in word_numbers.items():
                if any(k in lower for k in [f"{word} acre", f"{word} एकड़", f"{word} એકર", f"{word} एकर", f"{word} ఎకరా", f"{word} ஏக்கர்"]):
                    extracted["land_acres"] = val
                    break

        # 4. Yield per acre detection (Quintals)
        yield_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:quintals?|qtl|quintal|क्विंटल|ક્વિન્ટલ|క్వింటా[లు|ళ్లు|ల]?|குவிண்டால்|কুইন্টাল|ਕੁਇੰਟਲ|ಕ್ವಿಂಟಾಲ್)', lower)
        if yield_match:
            try:
                extracted["expected_yield_qtl_acre"] = float(yield_match.group(1))
            except Exception:
                pass

        # 5. Selling Price detection
        price_match = re.search(r'(?:price|rate|भाव|दाम|કિંમત|ధర|விலை|দাম|ਰੇਟ|ಬೆಲೆ)\s*(?:is|of|₹|rs\.?|rupees)?\s*([0-9,]+)', lower)
        if price_match:
            try:
                clean_p = price_match.group(1).replace(",", "")
                extracted["selling_price_per_qtl"] = float(clean_p)
            except Exception:
                pass

        # 6. Expenses detection
        exp_match = re.search(r'(?:expense|cost|खर्च|लागत|ખર્ચ|ఖర్చు|செலவு|খরচ|ਖਰਚਾ|ವೆಚ್ಚ)\s*(?:is|of|₹|rs\.?|rupees)?\s*([0-9,]+)', lower)
        if exp_match:
            try:
                clean_e = exp_match.group(1).replace(",", "")
                extracted["estimated_expenses_inr"] = float(clean_e)
            except Exception:
                pass

        # 7. Existing loan obligations detection
        loan_match = re.search(r'(?:loan|debt|कर्ज|उधार|ઋણ|అప్పు|கடன்|ঋণ|ਕਰਜ਼ਾ|ಸಾಲ)\s*(?:is|of|₹|rs\.?|rupees)?\s*([0-9,]+)', lower)
        if loan_match:
            try:
                clean_l = loan_match.group(1).replace(",", "")
                extracted["existing_loan_obligations_inr"] = float(clean_l)
            except Exception:
                pass

        # 8. Irrigation Detection
        if any(w in lower for w in ["drip", "ड्रिप", "ઠિબક", "ठिबक", "డ్రిప్", "சொட்டு நீர்", "ড্রিপ", "ਤੁਪਕਾ", "ಹನಿ"]):
            extracted["irrigation"] = "Drip"
        elif any(w in lower for w in ["rain", "rainfed", "बारिश", "વરસાદ", "पाऊस", "వర్షం", "மழை", "বৃষ্টি", "ਮੀਂਹ", "ಮಳೆ"]):
            extracted["irrigation"] = "Rainfed"
        elif any(w in lower for w in ["canal", "نہر", "नहर", "કહેનાર", "कालवा", "కాలువ", "கால்வாய்", "খাল", "ਨਹਿਰ", "ಕಾಲುವೆ"]):
            extracted["irrigation"] = "Canal"

        # 9. Farmer Name Detection (if self-introduced)
        name_match = re.search(r'(?:my name is|i am|mera naam|naam|नाव|નામ|పేరు|பெயர்|নাম|ਨਾਮ|ಹೆಸರು)\s+([A-Za-z\u0900-\u0D7F\s]{3,25})', lower)
        if name_match:
            candidate = name_match.group(1).strip().title()
            if candidate and len(candidate) > 2 and not any(w in candidate.lower() for w in ["acres", "tomato", "cotton", "farmer", "crop"]):
                extracted["farmer_name"] = candidate

        missing = self._get_missing_fields(extracted)
        return {
            "extracted_fields": extracted,
            "missing_fields": missing,
            "confidence": 0.90 if len(missing) == 0 else (1.0 - len(missing) * 0.2),
            "raw_transcript": transcript
        }

    def _get_missing_fields(self, data: Dict[str, Any]) -> List[str]:
        """Identifies required fields that still need clarification from the farmer."""
        required = ["crop_name", "land_acres", "district", "expected_yield_qtl_acre"]
        missing = []
        for field in required:
            val = data.get(field)
            if val is None or val == "":
                missing.append(field)
        return missing

    def get_followup_question(self, missing_fields: List[str], lang_code: str = "en") -> Optional[str]:
        """Returns the conversational follow-up prompt for the next missing field in the selected language."""
        if not missing_fields:
            return None
        next_field = missing_fields[0]
        prompts = MISSING_FIELD_PROMPTS.get(next_field, {})
        return prompts.get(lang_code, prompts.get("en", f"Please provide information for {next_field}."))

    def synthesize_speech(self, text: str, lang_code: str = "en") -> Tuple[bool, Optional[bytes], str]:
        """
        Generates audio for the credit decision output using OpenAI TTS or gTTS.
        Returns: (success, audio_bytes, mime_type)
        """
        if not text or not text.strip():
            return False, None, "audio/mp3"

        clean_text = text.replace("₹", " rupees ").replace("*", "").replace("#", "").strip()

        # 1. Try OpenAI TTS if configured
        if self.openai_client:
            try:
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=clean_text[:4000]
                )
                audio_bytes = response.read()
                return True, audio_bytes, "audio/mp3"
            except Exception as e:
                logger.warning(f"OpenAI TTS failed, falling back to gTTS: {e}")

        # 2. Try gTTS (Google Text-to-Speech)
        try:
            lang_info = LANG_CONFIGS.get(lang_code, LANG_CONFIGS["en"])
            gtts_lang = lang_info["gtts_code"]
            tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return True, fp.read(), "audio/mp3"
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return False, None, "audio/mp3"


# Global VoiceService instance
voice_service = VoiceService()
