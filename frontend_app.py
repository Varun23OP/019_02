"""
KisanSetu - Dual Streamlit Portal (frontend_app.py)
Marginal Farmer Cashflow Intake with Conversational Voice Assistant & Institutional Rural Bank Underwriting Console
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta

# Inject backend path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.services.agronomic_engine import (
    AgronomicEngine,
    NHB_YIELD_CEILINGS_QTL_ACRE,
    DISTRICT_COORDINATES,
    FPO_ACTIVE_GUARANTOR_ROSTER
)
from backend.services.voice_service import (
    voice_service,
    LANG_CONFIGS,
    MISSING_FIELD_PROMPTS
)

# Page Configuration
st.set_page_config(
    page_title="KisanSetu | Dynamic Agronomic Credit Network",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Engine
@st.cache_resource
def get_engine():
    return AgronomicEngine()

engine = get_engine()

# Custom Styling for Human-Crafted Institutional Look
st.markdown("""
<style>
    /* Clean, Professional Institutional Styling */
    .main {
        background-color: #f8fafc;
        color: #0f172a;
    }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 12px 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .mandi-ticker {
        background: linear-gradient(90deg, #15803d, #166534);
        color: #ffffff;
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.92rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 18px;
    }
    .warning-clamp-badge {
        background-color: #fffbeb;
        color: #b45309;
        border-left: 4px solid #f59e0b;
        padding: 10px 14px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.88rem;
        margin: 10px 0;
    }
    .weather-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 14px;
    }
    .voice-assistant-card {
        background: #ffffff;
        border: 1.5px solid #86efac;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .transcript-box {
        background: #f8fafc;
        border: 1.5px dashed #cbd5e1;
        padding: 12px 16px;
        border-radius: 6px;
        color: #0f172a;
        font-size: 0.92rem;
        font-style: italic;
        margin: 8px 0;
    }
    .followup-box {
        background: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 10px 14px;
        border-radius: 6px;
        color: #1e3a8a;
        font-weight: 600;
        font-size: 0.90rem;
        margin-top: 8px;
    }
    .cap-danger {
        background-color: #fef2f2;
        color: #991b1b;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.78rem;
    }
    .cap-success {
        background-color: #f0fdf4;
        color: #166534;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)

# Multilingual Vocabulary Dictionary
LANGUAGES = {
    "English": "en",
    "हिंदी (Hindi)": "hi",
    "ગુજરાતી (Gujarati)": "gu",
    "मराठी (Marathi)": "mr",
    "తెలుగు (Telugu)": "te",
    "தமிழ் (Tamil)": "ta",
    "বাংলা (Bengali)": "bn",
    "ਪੰਜਾਬੀ (Punjabi)": "pa",
    "ಕನ್ನಡ (Kannada)": "kn"
}

VOCAB = {
    "en": {
        "title": "🌾 KisanSetu: Community-Owned Agri-Credit Network",
        "farmer_tab": "🌾 Marginal Farmer Cashflow Portal",
        "bank_tab": "🏦 Rural Bank Underwriting Console",
        "calculate_btn": "Calculate Agronomic Credit Limit",
        "approved_limit": "Approved Credit Limit",
        "trust_score": "Community Trust Score",
        "interest_rate": "Subsidized Interest Rate",
        "bullet_due": "Harvest Bullet Due Date",
        "savings_note": "You save approximately ₹14,800 vs 48% informal moneylenders.",
        "voice_sim": "🎙️ Voice Intake: 'Ramesh Patil: 1.5 acres Tomato in Nashik with Drip Irrigation'"
    },
    "hi": {
        "title": "🌾 किसानसेतु: समुदाय-स्वामित्व वाला डिजिटल कृषि ऋण नेटवर्क",
        "farmer_tab": "🌾 सीमांत किसान नकदी प्रवाह पोर्टल",
        "bank_tab": "🏦 ग्रामीण बैंक ऋण हामीदारी कंसोल",
        "calculate_btn": "पारदर्शी ऋण सीमा की गणना करें",
        "approved_limit": "स्वीकृत संस्थागत ऋण सीमा",
        "trust_score": "सामुदायिक विश्वास स्कोर",
        "interest_rate": "सब्सिडीयुक्त ब्याज दर",
        "bullet_due": "फसल कटाई उपरांत देय तिथि",
        "savings_note": "साहूकारों के 48% ब्याज की तुलना में आपकी लगभग ₹14,800 की बचत होगी।",
        "voice_sim": "🎙️ वॉइस इनपुट: 'रमेश पाटिल: नासिक में 1.5 एकड़ टमाटर, ड्रिप सिंचाई और 3-साथी गारंटी'"
    },
    "gu": {
        "title": "🌾 કિસાનસેતુ: સમુદાય આધારિત ડિજિટલ કૃષિ ધિરાણ નેટવર્ક",
        "farmer_tab": "🌾 સીમાંત ખેડૂત રોકડ પ્રવાહ પોર્ટલ",
        "bank_tab": "🏦 ગ્રામીણ બેંક અંડરરાઇટિંગ કન્સોલ",
        "calculate_btn": "પારદર્શક ધિરાણ મર્યાદા ગણો",
        "approved_limit": "મંજૂર સંસ્થાકીય ધિરાણ મર્યાદા",
        "trust_score": "સામુદાયિક ટ્રસ્ટ સ્કોર",
        "interest_rate": "સબસિડીવાળો વ્યાજ દર",
        "bullet_due": "પાક લણણી પછીની ચુકવણી તારીખ",
        "savings_note": "સાહુકારી વ્યાજ સામે ખેડૂતને આશરે ₹14,800 ની બચત થશે.",
        "voice_sim": "🎙️ વોઇસ ઇનપુટ: 'રમેશભાઈ પટેલ: 1.5 એકર ટામેટા, ડ્રિપ ઇરિગેશન અને 3-ખેડૂત ગેરંટી'"
    },
    "mr": {
        "title": "🌾 किसानसेतू: समुदाय-मालकीचे डिजिटल कृषी पतपुरवठा नेटवर्क",
        "farmer_tab": "🌾 अल्पभूधारक शेतकरी रोकड प्रवाह पोर्टल",
        "bank_tab": "🏦 ग्रामीण बँक जोखीम मूल्यांकन मंच",
        "calculate_btn": "पारदर्शक कर्ज मर्यादा मोजा",
        "approved_limit": "मंजूर संस्थागत कर्ज मर्यादा",
        "trust_score": "सामुदायिक विश्वास निर्देशांक",
        "interest_rate": "सवलतीचा व्याज दर",
        "bullet_due": "पीक विक्रीपश्चात परतफेड तारीख",
        "savings_note": "खाजगी सावकारांच्या ४८% व्याजाच्या तुलनेत सुमारे ₹१४,८०० ची बचत.",
        "voice_sim": "🎙️ व्हॉईस इनपुट: 'रमेश पाटील: १.५ एकर टोमॅटो, ठिबक सिंचन व ३-शेतकरी हमी गट'"
    },
    "te": {
        "title": "🌾 కిసాన్ సేతు: కమ్యూనిటీ యాజమాన్య డిజిటల్ వ్యవసాయ పరపతి నెట్వర్క్",
        "farmer_tab": "🌾 సన్నకారు రైతు నగదు ప్రవాహ పోర్టల్",
        "bank_tab": "🏦 గ్రామీణ బ్యాంక్ అండర్ రైటింగ్ కన్సోల్",
        "calculate_btn": "రుణ పరిమితిని లెక్కించండి",
        "approved_limit": "మంజూరైన రుణ పరిమితి",
        "trust_score": "ట్రస్ట్ స్కోర్",
        "interest_rate": "రాయితీ వడ్డీ రేటు",
        "bullet_due": "పంట అమ్మకం తర్వాత గడువు",
        "savings_note": "వడ్డీ వ్యాపారుల కంటే మీకు ₹14,800 ఆదా అవుతుంది.",
        "voice_sim": "🎙️ వాయిస్ ఇన్పుట్: 'రమేష్ పాటిల్: 1.5 ఎకరాల టమాటా, డ్రిప్ ఇరిగేషన్'"
    },
    "ta": {
        "title": "🌾 கிசான்சேது: சமூக உரிமையுடைய டிஜிட்டல் விவசாயக் கடன் தளம்",
        "farmer_tab": "🌾 குறு விவசாயி பணப்புழக்க மையம்",
        "bank_tab": "🏦 கிராம வங்கி கடன் மதிப்பீட்டு அரங்கம்",
        "calculate_btn": "கடன் வரம்பைக் கணக்கிடு",
        "approved_limit": "அங்கீகரிக்கப்பட்ட கடன் வரம்பு",
        "trust_score": "நம்பகத்தன்மை மதிப்பீடு",
        "interest_rate": "மானிய வட்டி விகிதம்",
        "bullet_due": "அறுவடைக்குப் பிந்தைய தவணை தேதி",
        "savings_note": "கந்துவட்டிக்காரர்களை விட உங்களுக்கு ₹14,800 மிச்சமாகும்.",
        "voice_sim": "🎙️ குரல் வழி: 'ரமேஷ் பாட்டீல்: 1.5 ஏக்கர் தக்காளி, சொட்டு நீர் பாசனம்'"
    },
    "bn": {
        "title": "🌾 কিষাণসেতু: সম্প্রদায়-মালিকানাধীন ডিজিটাল কৃষি ঋণ নেটওয়ার্ক",
        "farmer_tab": "🌾 প্রান্তিক কৃষক নগদ প্রবাহ পোর্টাল",
        "bank_tab": "🏦 গ্রামীণ ব্যাংক আন্ডাররাইটিং কনসোল",
        "calculate_btn": "স্বচ্ছ ঋণ সীমা হিসাব করুন",
        "approved_limit": "অনুমোদিত ঋণ সীমা",
        "trust_score": "বিশ্বাসযোগ্যতা স্কোর",
        "interest_rate": "ভর্তুকিযুক্ত সুদের হার",
        "bullet_due": "ফসল তোলার পরের পরিশোধের তারিখ",
        "savings_note": "মহাজনদের চড়া সুদের তুলনায় প্রায় ₹১৪,৮০০ সাশ্রয় হবে।",
        "voice_sim": "🎙️ ভয়েস ইনপুট: 'রমেশ পাটিল: ১.৫ একর টমেটো ও ৩-সদস্যের গ্যারান্টি'"
    },
    "pa": {
        "title": "🌾 ਕਿਸਾਨਸੇਤੂ: ਭਾਈਚਾਰਕ ਮਾਲਕੀ ਵਾਲਾ ਖੇਤੀ ਕਰਜ਼ਾ ਨੈੱਟਵਰਕ",
        "farmer_tab": "🌾 ਸੀਮਾਂਤ ਕਿਸਾਨ ਕੈਸ਼ਫਲੋ ਪੋਰਟਲ",
        "bank_tab": "🏦 ਪੇਂਡੂ ਬੈਂਕ ਅੰਡਰਰਾਈਟਿੰਗ ਕੰਸੋਲ",
        "calculate_btn": "ਪਾਰਦਰਸ਼ੀ ਕਰਜ਼ਾ ਸੀਮਾ ਗਿਣੋ",
        "approved_limit": "ਪ੍ਰਵਾਨਿਤ ਕਰਜ਼ਾ ਸੀਮਾ",
        "trust_score": "ਭਰੋਸੇਯੋਗਤਾ ਸਕੋਰ",
        "interest_rate": "ਸਬਸਿਡੀ ਵਾਲੀ ਵਿਆਜ ਦਰ",
        "bullet_due": "ਫ਼ਸਲ ਵੇਚਣ ਤੋਂ ਬਾਅਦ ਅਦਾਇਗੀ ਮਿਤੀ",
        "savings_note": "ਆੜ੍ਹਤੀਆਂ ਦੇ 48% ਵਿਆਜ ਨਾਲੋਂ ਲਗਭਗ ₹14,800 ਦੀ ਬੱਚਤ।",
        "voice_sim": "🎙️ ਆਵਾਜ਼ ਇਨਪੁਟ: 'ਰਮੇਸ਼ ਪਾਟਿਲ: 1.5 ਏਕੜ ਟਮਾਟਰ, ਤੁਪਕਾ ਸਿੰਚਾਈ'"
    },
    "kn": {
        "title": "🌾 ಕಿಸಾನ್‌ಸೇತು: ಸಮುದಾಯ ಸ್ವಾಮ್ಯದ ಕೃಷಿ ಸಾಲ ಜಾಲ",
        "farmer_tab": "🌾 ಸಣ್ಣ ರೈತರ ನಗದು ಹರಿವು ಪೋರ್ಟಲ್",
        "bank_tab": "🏦 ಗ್ರಾಮೀಣ ಬ್ಯಾಂಕ್ ಅಂಡರ್‌ರೈಟಿಂಗ್ ಕನ್ಸೋಲ್",
        "calculate_btn": "ಸಾಲದ ಮಿತಿಯನ್ನು ಲೆಕ್ಕಹಾಕಿ",
        "approved_limit": "ಅನುಮೋದಿತ ಸಾಲದ ಮಿತಿ",
        "trust_score": "ಸಮುದಾಯ ಟ್ರಸ್ಟ್ ಸ್ಕೋರ್",
        "interest_rate": "ರಿಯಾಯಿತಿ ಬಡ್ಡಿ ದರ",
        "bullet_due": "ಬೆಳೆ ಕಟಾವಿನ ನಂತರದ ಮರುಪಾವತಿ ದಿನಾಂಕ",
        "savings_note": "ಲವಾದೇವಿದಾರರಿಗಿಂತ ಸುಮಾರು ₹14,800 ಉಳಿತಾಯವಾಗಲಿದೆ.",
        "voice_sim": "🎙️ ಧ್ವನಿ ಇನ್‌ಪುಟ್: 'ರಮೇಶ್ ಪಾಟೀಲ್: 1.5 ಎಕರೆ ಟೊಮೆಟೊ, ಹನಿ ನೀರಾವರಿ'"
    }
}

# Initialize Session State Variables
if "farmer_name" not in st.session_state:
    st.session_state.farmer_name = "Ramesh Tukaram Patil"
if "district_choice" not in st.session_state:
    st.session_state.district_choice = "Maharashtra_Nashik"
if "crop_choice" not in st.session_state:
    st.session_state.crop_choice = "Tomato"
if "acres_val" not in st.session_state:
    st.session_state.acres_val = 1.5
if "user_yield" not in st.session_state:
    st.session_state.user_yield = 22.0
if "irrigation_choice" not in st.session_state:
    st.session_state.irrigation_choice = "Drip"
if "selected_peers" not in st.session_state:
    st.session_state.selected_peers = ["MEM-442", "MEM-443"]
if "audio_transcript" not in st.session_state:
    st.session_state.audio_transcript = ""
if "followup_question" not in st.session_state:
    st.session_state.followup_question = None
if "last_processed_audio_len" not in st.session_state:
    st.session_state.last_processed_audio_len = 0
if "stt_provider_used" not in st.session_state:
    st.session_state.stt_provider_used = "Google Speech Recognition"

# Sidebar: Language & Configuration
with st.sidebar:
    st.image("https://img.icons8.com/color/96/wheat.png", width=64)
    st.title("KisanSetu Hub")
    st.caption("Public Digital Credit Infrastructure")
    
    selected_lang_label = st.selectbox("🌐 Select Interface Language", list(LANGUAGES.keys()), index=0)
    lang_code = LANGUAGES[selected_lang_label]
    t = VOCAB.get(lang_code, VOCAB["en"])
    
    st.divider()
    st.subheader("🎙️ Voice AI Assistant Status")
    whisper_active = bool(voice_service.openai_client)
    if whisper_active:
        st.success("🟢 OpenAI Whisper STT (Active)")
        st.success("🟢 OpenAI TTS-1 Engine (Active)")
    else:
        st.success("🟢 Google Speech Recognition (Active)")
        st.success("🟢 gTTS Multilingual Audio (Active)")
        st.caption("💡 Set `OPENAI_API_KEY` in `.env` for Whisper-1 cloud acceleration.")
    
    st.divider()
    st.subheader("🏛️ Live Datasets Status")
    st.success("🟢 AGMARKNET 2.0 (Live Modal Feeds)")
    st.success("🟢 NHB 90th-Percentile Yield Norms")
    st.success("🟢 Open-Meteo Weather Telemetry")
    st.success("🟢 PM-KISAN OGD Registry")
    st.success("🟢 WDRA e-NWR Trade Settlements")
    
    st.divider()
    st.info("💡 **Explainable Sizing Formula:**\n`Credit Limit = 0.45 × Net Farm-Gate Profit × Weather Factor × FPO Factor`")

# Main Portal Title
st.title(t["title"])
st.caption("Replacing physical land mortgages with real-time agronomic data, climate telemetry, and 3-peer social collateral.")

# Main Navigation Tabs
tab_farmer, tab_bank = st.tabs([t["farmer_tab"], t["bank_tab"]])

# ==============================================================================
# TAB 1: MARGINAL FARMER CASHFLOW INTAKE & WORKING VOICE ASSISTANT
# ==============================================================================
with tab_farmer:
    st.subheader("🎙️ Kisan Vani Multilingual Conversational Voice Assistant")
    st.markdown(f"Speak your crop, land area, district, and yield naturally in **{selected_lang_label}**. The voice assistant transcribes your speech, extracts the agronomic fields into the form below, and clarifies any missing details.")

    # Working Voice Input Component
    col_v1, col_v2 = st.columns([1.2, 1.0])
    
    with col_v1:
        st.markdown("##### 🎤 Live Microphone Audio Input")
        audio_val = st.audio_input(
            f"Click mic to record spoken agronomic details in {selected_lang_label}",
            key="farmer_audio_recorder"
        )
        
        # When user records audio
        if audio_val is not None:
            audio_bytes = audio_val.getvalue()
            if len(audio_bytes) != st.session_state.last_processed_audio_len:
                st.session_state.last_processed_audio_len = len(audio_bytes)
                with st.spinner(f"Transcribing spoken audio in {selected_lang_label}..."):
                    stt_res = voice_service.transcribe_audio(audio_bytes, lang_code=lang_code)
                    if stt_res["success"]:
                        transcript_text = stt_res["transcript"]
                        st.session_state.audio_transcript = transcript_text
                        st.session_state.stt_provider_used = stt_res["provider"]
                        
                        # Extract structured entities
                        current_dict = {
                            "farmer_name": st.session_state.farmer_name,
                            "district": st.session_state.district_choice,
                            "crop_name": st.session_state.crop_choice,
                            "land_acres": st.session_state.acres_val,
                            "expected_yield_qtl_acre": st.session_state.user_yield,
                            "irrigation": st.session_state.irrigation_choice
                        }
                        extraction = voice_service.extract_agronomic_entities(transcript_text, current_dict)
                        ext_fields = extraction["extracted_fields"]
                        
                        # Populate session state fields
                        if ext_fields.get("crop_name"):
                            st.session_state.crop_choice = ext_fields["crop_name"]
                        if ext_fields.get("land_acres") is not None:
                            st.session_state.acres_val = float(ext_fields["land_acres"])
                        if ext_fields.get("district"):
                            st.session_state.district_choice = ext_fields["district"]
                        if ext_fields.get("expected_yield_qtl_acre") is not None:
                            st.session_state.user_yield = float(ext_fields["expected_yield_qtl_acre"])
                        if ext_fields.get("irrigation"):
                            st.session_state.irrigation_choice = ext_fields["irrigation"]
                        if ext_fields.get("farmer_name"):
                            st.session_state.farmer_name = ext_fields["farmer_name"]
                        
                        # Check for conversational follow-up
                        st.session_state.followup_question = voice_service.get_followup_question(
                            extraction["missing_fields"], lang_code=lang_code
                        )
                        st.rerun()
                    else:
                        st.error(stt_res.get("error", "Could not transcribe audio. Please try speaking closer to the mic."))

    with col_v2:
        st.markdown("##### 📝 Real-Time Recognized Transcript")
        if st.session_state.audio_transcript:
            st.markdown(f"""
            <div class="transcript-box">
                "{st.session_state.audio_transcript}"
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"✅ Transcribed via **{st.session_state.stt_provider_used}** ({selected_lang_label})")
        else:
            st.info(f"🎙️ No audio recorded yet. Click the microphone control on the left and speak: *\"1.5 acres of Tomato in Nashik with drip irrigation\"* (or in {selected_lang_label}).")
        
        # Conversational Follow-up Prompt
        if st.session_state.followup_question:
            st.markdown(f"""
            <div class="followup-box">
                🗣️ <strong>Assistant Follow-up Question:</strong><br>
                {st.session_state.followup_question}
            </div>
            """, unsafe_allow_html=True)
            
            # Optional typed response for follow-up
            col_fq1, col_fq2 = st.columns([3, 1])
            with col_fq1:
                typed_answer = st.text_input("Answer by typing (or speak via microphone):", key="txt_followup_answer", placeholder="e.g., 20 quintals per acre")
            with col_fq2:
                st.write("")
                st.write("")
                if st.button("Submit Answer"):
                    if typed_answer.strip():
                        current_dict = {
                            "farmer_name": st.session_state.farmer_name,
                            "district": st.session_state.district_choice,
                            "crop_name": st.session_state.crop_choice,
                            "land_acres": st.session_state.acres_val,
                            "expected_yield_qtl_acre": st.session_state.user_yield,
                            "irrigation": st.session_state.irrigation_choice
                        }
                        extraction = voice_service.extract_agronomic_entities(typed_answer, current_dict)
                        ext_fields = extraction["extracted_fields"]
                        if ext_fields.get("expected_yield_qtl_acre") is not None:
                            st.session_state.user_yield = float(ext_fields["expected_yield_qtl_acre"])
                        if ext_fields.get("land_acres") is not None:
                            st.session_state.acres_val = float(ext_fields["land_acres"])
                        if ext_fields.get("crop_name"):
                            st.session_state.crop_choice = ext_fields["crop_name"]
                        if ext_fields.get("district"):
                            st.session_state.district_choice = ext_fields["district"]
                        st.session_state.followup_question = voice_service.get_followup_question(
                            extraction["missing_fields"], lang_code=lang_code
                        )
                        st.rerun()

    st.divider()

    # Form parameters (Pre-populated from voice extraction and freely editable)
    col_t1, col_t2 = st.columns([1.3, 1.0])
    
    with col_t1:
        st.subheader("🌾 Farm & Crop Parameters (Review & Edit)")
        st.caption("Verify and modify the extracted agronomic parameters before submitting for underwriting assessment.")
        
        # Farmer Details
        f_name = st.text_input("Farmer Full Name", value=st.session_state.farmer_name, key="input_farmer_name")
        st.session_state.farmer_name = f_name
        
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            dist_keys = list(DISTRICT_COORDINATES.keys())
            dist_idx = dist_keys.index(st.session_state.district_choice) if st.session_state.district_choice in dist_keys else 0
            district_choice = st.selectbox(
                "District & State",
                dist_keys,
                index=dist_idx,
                format_func=lambda d: f"{d.title()} ({DISTRICT_COORDINATES[d]['state']}) - {DISTRICT_COORDINATES[d]['apmc']}",
                key="select_district"
            )
            st.session_state.district_choice = district_choice

        with col_loc2:
            crop_keys = list(NHB_YIELD_CEILINGS_QTL_ACRE.keys())
            crop_idx = crop_keys.index(st.session_state.crop_choice) if st.session_state.crop_choice in crop_keys else 0
            crop_choice = st.selectbox(
                "Cultivated Crop",
                crop_keys,
                index=crop_idx,
                format_func=lambda c: c.title(),
                key="select_crop"
            )
            st.session_state.crop_choice = crop_choice

        col_land1, col_land2 = st.columns(2)
        with col_land1:
            acres_val = st.slider(
                "Land Cultivation Area (Acres)",
                min_value=0.5,
                max_value=2.5,
                value=float(min(max(st.session_state.acres_val, 0.5), 2.5)),
                step=0.1,
                key="slider_acres"
            )
            st.session_state.acres_val = acres_val

        with col_land2:
            nhb_cap = NHB_YIELD_CEILINGS_QTL_ACRE[crop_choice]["ceiling"]
            user_yield = st.number_input(
                f"Expected Yield (Qtl/Acre) [NHB Ceiling: {nhb_cap} Qtl]",
                min_value=5.0,
                max_value=40.0,
                value=float(min(max(st.session_state.user_yield, 5.0), 40.0)),
                step=0.5,
                key="num_yield"
            )
            st.session_state.user_yield = user_yield

        col_ir1, col_ir2 = st.columns(2)
        with col_ir1:
            irrigation_options = ["Drip", "Canal", "Rainfed"]
            ir_idx = irrigation_options.index(st.session_state.irrigation_choice) if st.session_state.irrigation_choice in irrigation_options else 0
            irrigation_choice = st.selectbox("Irrigation Method", irrigation_options, index=ir_idx, key="select_irrigation")
            st.session_state.irrigation_choice = irrigation_choice
            
        with col_ir2:
            guarantor_options = list(FPO_ACTIVE_GUARANTOR_ROSTER.keys())
            selected_peers = st.multiselect(
                "Select 2 Peer Guarantors (FPO Roster)",
                guarantor_options,
                default=st.session_state.selected_peers,
                format_func=lambda g: f"{FPO_ACTIVE_GUARANTOR_ROSTER[g]['name']} [{FPO_ACTIVE_GUARANTOR_ROSTER[g]['status']}]",
                key="multiselect_peers"
            )
            st.session_state.selected_peers = selected_peers

        # Explicit Submission & Confirmation Button
        st.markdown("---")
        btn_calc = st.button("✅ Confirm Parameters & Calculate Agronomic Credit Limit", type="primary", use_container_width=True)

    with col_t2:
        # Real-Time Mandi Ticker Ribbon
        mandi_info = engine.discover_agmarknet_price_and_volatility(crop_choice, district_choice)
        st.markdown(f"""
        <div class="mandi-ticker">
            <div><strong>🛒 {district_choice.title()} APMC:</strong> ₹{mandi_info['mandi_modal_price_qtl']:,.0f}/Qtl (Modal)</div>
            <div>Arrivals: {mandi_info['arrivals_tonnes']} MT {mandi_info['price_trend_30d']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Live Weather Telemetry Box
        weather_info = engine.fetch_realtime_weather_telemetry(district_choice)
        st.markdown(f"""
        <div class="weather-card">
            <strong>🌦️ Live Weather Telemetry ({weather_info['source']}):</strong><br>
            • 7-Day Rainfall: <strong>{weather_info['rainfall_7d_mm']} mm</strong> ({weather_info['rainfall_status']})<br>
            • Drought Risk Multiplier: <strong>{weather_info['drought_risk_multiplier']}x</strong><br>
            • Dynamic Maturity Adjustment: <strong>+{weather_info['weather_maturity_delay_days']} Days</strong>
        </div>
        """, unsafe_allow_html=True)

        # Run Underwriting Calculation
        calc_payload = {
            "farmer_name": f_name,
            "district": district_choice,
            "crop_name": crop_choice,
            "land_acres": acres_val,
            "expected_yield_qtl_acre": user_yield,
            "peer_member_ids": selected_peers
        }
        res = engine.compute_complete_underwriting(calc_payload)
        fin = res["financial_sizing"]
        guards = res["agronomic_guards"]

        # Check and Display Yield Clamping Alert
        if guards["yield_capping"]["yield_clamped"]:
            st.markdown(f"""
            <div class="warning-clamp-badge">
                ⚠️ <strong>Input Clamped to NHB 90th-Percentile Benchmark:</strong><br>
                Reported {user_yield} Qtl/Ac was capped to safe district ceiling of <strong>{guards['yield_capping']['effective_yield_qtl_acre']} Qtl/Ac</strong> to prevent overleveraging.
            </div>
            """, unsafe_allow_html=True)

        if not guards["fpo_peer_roster"]["all_peers_within_cap"]:
            st.error("⚠️ One or more peer guarantors have reached their active guarantee cap (2/2). Multiplier reduced.")

        st.subheader("📊 Transparent Sizing Decision")

        amt_str = f"₹ {fin['final_sanctioned_credit_limit_inr']:,.0f}"
        score_str = f"{fin['composite_trust_score']}"
        rate_str = f"{fin['interest_rate_pct']}%"
        due_str = f"{res['trade_settlement_and_bullet_due']['bullet_due_date']}"
        crop_disp = crop_choice.title()
        dist_disp = district_choice.title()

        # Decision speech script templates
        voice_readout_native = {
            "en": f"Namaste {f_name}! Based on your {acres_val} acres of {crop_disp} in {dist_disp} and 3-peer FPO guarantee, your approved credit limit is {amt_str} with {score_str} trust score. Subsidized interest rate is {rate_str} per annum with harvest bullet repayment due on {due_str}.",
            "hi": f"नमस्ते {f_name} जी! {dist_disp} में आपकी {acres_val} एकड़ {crop_disp} की फसल और 3-साथी FPO गारंटी के आधार पर, आपकी स्वीकृत ऋण सीमा {amt_str} तय की गई है। ब्याज दर केवल {rate_str} है और फसल बिक्री उपरांत देय तिथि {due_str} है।",
            "gu": f"નમસ્તે {f_name}ભાઈ! {dist_disp} માં તમારી {acres_val} એકર {crop_disp} ની ખેતી અને FPO ગેરંટી આધારે, તમારી મંજૂર થયેલ ધિરાણ મર્યાદા {amt_str} છે. વ્યાજ દર માત્ર {rate_str} છે અને પાક લણણી પછીની ચુકવણી તારીખ {due_str} છે.",
            "mr": f"नमस्कार {f_name}जी! {dist_disp} मध्ये आपली {acres_val} एकर {crop_disp} लागवड आणि ३-शेतकरी हमीच्या आधारे, आपली मंजूर कर्ज मर्यादा {amt_str} असून {rate_str} सवलतीचा व्याज दर आहे. परतफेड देय तारीख {due_str} आहे.",
            "te": f"నమస్కారం {f_name} గారు! {dist_disp} లో మీ {acres_val} ఎకరాల {crop_disp} పంట మరియు ఎఫ్‌పీఓ గ్యారెంటీ ఆధారంగా, మీ ఆమోదిత రుణ పరిమితి {amt_str}, {rate_str} వడ్డీ రేటుతో. గడువు తేదీ {due_str}.",
            "ta": f"வணக்கம் {f_name} அவர்களே! {dist_disp} இல் உங்கள் {acres_val} ஏக்கர் {crop_disp} பயிர் அடிப்படையில், உங்கள் அங்கீகரிக்கப்பட்ட கடன் வரம்பு {amt_str}, {rate_str} வட்டி விகிதத்தில். திருப்பிச் செலுத்தும் தேதி {due_str}.",
            "bn": f"নমস্কার {f_name} বাবু! {dist_disp} এ আপনার {acres_val} একর {crop_disp} এবং FPO গ্যারান্টির ভিত্তিতে অনুমোদিত ঋণ সীমা {amt_str}, {rate_str} সুদে। পরিশোধের তারিখ {due_str}।",
            "pa": f"ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ {f_name} ਜੀ! {dist_disp} ਵਿੱਚ ਤੁਹਾਡੀ {acres_val} ਏਕੜ {crop_disp} ਫ਼ਸਲ ਲਈ ਪ੍ਰਵਾਨਿਤ ਕਰਜ਼ਾ ਸੀਮਾ {amt_str} ਹੈ, {rate_str} ਵਿਆਜ ਦਰ 'ਤੇ। ਅਦਾਇਗੀ ਮਿਤੀ {due_str} ਹੈ।",
            "kn": f"ನಮಸ್ಕಾರ {f_name} ಅವರೇ! {dist_disp} ನಲ್ಲಿ ನಿಮ್ಮ {acres_val} ಎಕರೆ {crop_disp} ಬೆಳೆಗೆ ಅನುಮೋದಿತ ಸಾಲದ ಮಿತಿ {amt_str} ಆಗಿದೆ, {rate_str} ಬಡ್ಡಿದರದಲ್ಲಿ. ಮರುಪಾವತಿ ದಿನಾಂಕ {due_str}."
        }

        spoken_native_text = voice_readout_native.get(lang_code, voice_readout_native["en"])

        # Display Text Metrics
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(t["approved_limit"], f"₹ {fin['final_sanctioned_credit_limit_inr']:,.0f}", delta=f"{fin['dscr_ratio']}x DSCR")
        with col_m2:
            st.metric(t["trust_score"], f"{fin['composite_trust_score']} / 100", delta="Grade AAA Prime")

        col_m3, col_m4 = st.columns(2)
        with col_m3:
            st.metric(t["interest_rate"], f"{fin['interest_rate_pct']}% p.a.", delta="Subsidized")
        with col_m4:
            st.metric(t["bullet_due"], res["trade_settlement_and_bullet_due"]["bullet_due_date"], delta=f"{res['trade_settlement_and_bullet_due']['bullet_maturity_days']} Days")

        st.success(t["savings_note"])

        # "🔊 Speak Result" Feature
        st.markdown("##### 🔊 Audio Decision Synthesizer")
        st.caption(f"Click below to generate and listen to this credit assessment in **{selected_lang_label}**.")
        
        col_spk1, col_spk2 = st.columns([1, 1])
        with col_spk1:
            if st.button("🔊 Speak Result", key="btn_speak_assessment_result", use_container_width=True):
                with st.spinner("Synthesizing credit decision audio..."):
                    success, audio_data, mime = voice_service.synthesize_speech(spoken_native_text, lang_code=lang_code)
                    if success and audio_data:
                        st.session_state["decision_audio"] = audio_data
                        st.success("🔊 Audio ready! Playing below:")
                    else:
                        st.error("Audio synthesis failed. Please check network connection.")

        if "decision_audio" in st.session_state and st.session_state["decision_audio"]:
            st.audio(st.session_state["decision_audio"], format="audio/mp3", autoplay=True)

        # Mathematical Sizing Breakdown
        with st.expander("🔍 Step-by-Step Mathematical Transparency Breakdown"):
            st.write(f"1. **Capped Harvest Production:** {acres_val} Ac × {guards['yield_capping']['effective_yield_qtl_acre']} Qtl = **{guards['yield_capping']['total_effective_yield_qtl']} Quintals**")
            st.write(f"2. **Net Farm-Gate Price:** ₹{guards['mandi_price_discovery']['mandi_modal_price_qtl']:,.0f} - ₹80 (APMC Freight) = **₹{guards['mandi_price_discovery']['net_farmgate_price_inr_qtl']:,.0f}/Qtl**")
            st.write(f"3. **Gross Farm Revenue:** {guards['yield_capping']['total_effective_yield_qtl']} Qtl × ₹{guards['mandi_price_discovery']['net_farmgate_price_inr_qtl']:,.0f} = **₹{fin['gross_farmgate_revenue_inr']:,.0f}**")
            st.write(f"4. **CACP Cultivation Cost:** {acres_val} Ac × ₹{guards['yield_capping']['cacp_cost_per_acre_inr']:,.0f} = **₹{fin['total_cultivation_cost_inr']:,.0f}**")
            st.write(f"5. **Net Farm-Gate Profit:** ₹{fin['gross_farmgate_revenue_inr']:,.0f} - ₹{fin['total_cultivation_cost_inr']:,.0f} = **₹{fin['net_farmgate_profit_inr']:,.0f}**")
            st.write(f"6. **Base Limit (45% Net Profit):** 0.45 × ₹{fin['net_farmgate_profit_inr']:,.0f} = **₹{fin['base_credit_limit_inr']:,.0f}**")
            st.write(f"7. **Weather & FPO Factors:** × {fin['weather_multiplier']} (Climate) × {fin['fpo_multiplier']} (FPO Multiplier)")
            st.markdown(f"**Final Approved Limit:** `₹ {fin['final_sanctioned_credit_limit_inr']:,.0f}`")

# ==============================================================================
# TAB 2: INSTITUTIONAL RURAL BANK UNDERWRITING CONSOLE
# ==============================================================================
with tab_bank:
    st.subheader("🏦 Rural Bank & NABARD Priority Sector Lending Underwriting Console")
    
    # Portfolio Top Metrics
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    with col_b1:
        st.metric("Total PSL Pool Allocated", "₹ 25.0 Crore", delta="NABARD RRB")
    with col_b2:
        st.metric("Active Guarantee Pools", "148 FPO Circles", delta="444 Farmers")
    with col_b3:
        st.metric("Historical Repayment Rate", "94.8%", delta="Zero Defaults")
    with col_b4:
        st.metric("e-RUPI Programmable Disbursal", "100% Lock", delta="Fertilizer/Seeds")

    st.markdown("---")

    col_audit1, col_audit2 = st.columns([1.2, 1.0])
    
    with col_audit1:
        st.markdown("#### 📋 Farmer Underwriting Queue & Risk Triangulation")
        
        # Live Application Audit Card
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #0f172a;">{f_name}</h4>
                <span class="cap-success">Grade AAA Prime</span>
            </div>
            <p style="margin: 4px 0; color: #475569; font-size: 0.88rem;">
                📍 {district_choice.title()} APMC • 🌾 {crop_choice.title()} ({acres_val} Acres) • 💧 Drip Irrigation
            </p>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 12px; background: #f8fafc; padding: 10px; border-radius: 6px;">
                <div><span style="font-size: 0.78rem; color: #64748b;">Sanctioned Limit:</span><br><strong>₹{fin['final_sanctioned_credit_limit_inr']:,.0f}</strong></div>
                <div><span style="font-size: 0.78rem; color: #64748b;">DSCR Ratio:</span><br><strong>{fin['dscr_ratio']}x</strong></div>
                <div><span style="font-size: 0.78rem; color: #64748b;">Subsidized Rate:</span><br><strong>{fin['interest_rate_pct']}% p.a.</strong></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Action Buttons
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            if st.button("⚡ Instant e-RUPI Disbursal", type="primary", use_container_width=True):
                st.success(f"✅ e-RUPI Voucher of ₹{fin['final_sanctioned_credit_limit_inr']:,.0f} issued to {f_name} (Restricted to Agri Inputs).")
        with col_act2:
            st.button("📄 Generate Sanction Letter", use_container_width=True)
        with col_act3:
            st.button("🚩 Flag for Field Audit", use_container_width=True)

    with col_audit2:
        st.markdown("#### 🛡️ FPO Guarantor Saturation Matrix")
        
        roster_data = []
        for mem_id, g in FPO_ACTIVE_GUARANTOR_ROSTER.items():
            roster_data.append({
                "Member ID": mem_id,
                "Guarantor Name": g["name"],
                "Land (Ac)": g["land_acres"],
                "Active Exposure": f"{g['active_guarantees_given']}/2",
                "Status": "⚠️ Capped (2/2)" if g["active_guarantees_given"] >= 2 else "✅ Available"
            })
        
        df_roster = pd.DataFrame(roster_data)
        st.dataframe(df_roster, use_container_width=True, hide_index=True)
        st.caption("🔒 Strict Policy Rule: Max 2 joint-liability guarantees per member to eliminate contagion default risks.")
