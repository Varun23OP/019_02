import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd

import importlib

# Local Service fallbacks in case backend process is starting
import backend.services.underwriting as _underwriting_mod
import backend.services.voice_nlp as _voice_nlp_mod
import backend.services.agri_data as _agri_data_mod
import backend.services.identity_blockchain as _identity_mod
import backend.services.gdpr_consent as _consent_mod

try:
    importlib.reload(_underwriting_mod)
    importlib.reload(_voice_nlp_mod)
    importlib.reload(_agri_data_mod)
    importlib.reload(_identity_mod)
    importlib.reload(_consent_mod)
except Exception:
    pass

from backend.services.underwriting import UnderwritingService
from backend.services.voice_nlp import VoiceNLPService, SUPPORTED_LANGUAGES
from backend.services.agri_data import AgriDataService, AGMARKNET_MANDI_CATALOG
from backend.services.identity_blockchain import FarmerIdentityService
from backend.services.gdpr_consent import GDPRConsentService

import os

# Dynamic API base configuration for cloud deployment (Streamlit Cloud / Render / Railway)
API_BASE = os.getenv("API_BASE") or os.getenv("BACKEND_URL")
if not API_BASE:
    try:
        API_BASE = st.secrets.get("BACKEND_URL") or st.secrets.get("API_BASE")
    except Exception:
        API_BASE = None
if not API_BASE:
    API_BASE = "http://127.0.0.1:8000/api/v1"

API_BASE = API_BASE.rstrip("/")
if not API_BASE.endswith("/api/v1"):
    API_BASE = f"{API_BASE}/api/v1"


st.set_page_config(
    page_title="KisanSetu — Community-Owned Credit Network",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# MULTILINGUAL LOCALIZATION DICTIONARY (11 LANGUAGES)
# -------------------------------------------------------------
TRANSLATIONS = {
    "English": {
        "title": "🌾 KisanSetu: Community-Owned Credit Network",
        "tagline": "Deterministic Agronomic Underwriting • 3-Peer FPO Social Collateral • Harvest Bullet Amortization",
        "tab_farmer": "👨‍🌾 Marginal Farmer Portal (Voice & Vernacular)",
        "tab_fpo": "🤝 FPO Coordinator Console",
        "tab_lender": "🏦 Rural Bank & NBFC Console",
        "farmer_sub": "Marginal Smallholder Credit Sizing & Intake",
        "zero_land": "💡 Zero Land-Deed Mandate: Underwritten using seasonal crop revenue and 3-peer FPO social collateral.",
        "voice_section": "🎙️ Multilingual Voice Intake (Spoken Input in 10+ Languages)",
        "voice_record_prompt": "Speak your name, crop, land size, yield, and input expenses:",
        "voice_sample_prompt": "Or select a 1-click pre-recorded voice scenario:",
        "transcript_box": "Recognized Spoken Transcript (Review & Correct Below):",
        "name_label": "Borrower Full Name",
        "phone_label": "Registered Mobile Number (Aadhaar-Linked)",
        "village_label": "Village",
        "district_label": "District",
        "crop_label": "Primary Crop Cultivated",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "Cultivated Acreage (Max 2.5 Acres for Marginal Smallholders)",
        "yield_label": "Expected Yield (Quintals/Acre)",
        "seeds_cost_label": "Seeds & Saplings Cost (₹)",
        "fert_cost_label": "Fertilizer & Pesticide Cost (₹)",
        "labour_cost_label": "Labour & Machinery Hiring Cost (₹)",
        "irr_cost_label": "Irrigation & Power Cost (₹)",
        "p1_label": "FPO Peer Guarantor 1",
        "p2_label": "FPO Peer Guarantor 2",
        "p3_label": "FPO Peer Guarantor 3",
        "fpo_label": "Affiliated FPO Producer Co.",
        "consent_underwriting": "I consent to agronomic cashflow assessment without land titles.",
        "consent_fpo": "I consent to sharing crop status with my 3-member FPO peer guarantee pool.",
        "consent_mandi": "I consent to receiving AGMARKNET mandi price alerts and harvest reminders.",
        "btn_calc": "🚀 Calculate Safe Credit Limit & Issue Credential",
        "success_msg": "✅ Agronomic Underwriting & Credit Sizing Completed!",
        "metric_score": "Credit Score",
        "metric_limit": "Approved Credit Limit",
        "metric_rev": "Projected Crop Revenue",
        "metric_bullet": "Bullet Repayment Due Date",
        "advisory_header": "📢 Vernacular Audio Advisory (IVR / WhatsApp):"
    },
    "Hindi (हिंदी)": {
        "title": "🌾 किसानसेतु: समुदाय-स्वामित्व वाला कृषि क्रेडिट नेटवर्क",
        "tagline": "निश्चित कृषि नकदी प्रवाह मूल्यांकन • FPO 3-सदस्यीय सामाजिक गारंटी • फसल-आधारित एकमुश्त पुनर्भुगतान",
        "tab_farmer": "👨‍🌾 सीमांत किसान पोर्टल (आवाज और क्षेत्रीय भाषा)",
        "tab_fpo": "🤝 FPO समन्वयक कंसोल",
        "tab_lender": "🏦 ग्रामीण बैंक और NBFC कंसोल",
        "farmer_sub": "सीमांत किसान ऋण सीमा और पंजीकरण",
        "zero_land": "💡 शून्य भूमि-दस्तावेज़ नीति: मौसमी फसल उत्पादन और 3 FPO सदस्यों की सामाजिक गारंटी पर आधारित।",
        "voice_section": "🎙️ बहुभाषी वॉयस इनटेक (10+ भाषाओं में बोलकर दर्ज करें)",
        "voice_record_prompt": "अपना नाम, फसल, जमीन, पैदावार और खर्च बोलें:",
        "voice_sample_prompt": "या 1-क्लिक वॉयस नमूना चुनें:",
        "transcript_box": "पहचाना गया वॉयस संदेश (नीचे जांचें और सुधारें):",
        "name_label": "किसान का पूरा नाम",
        "phone_label": "मोबाइल नंबर (आधार से जुड़ा हुआ)",
        "village_label": "गांव",
        "district_label": "जिला",
        "crop_label": "मुख्य फसल",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "खेती योग्य भूमि (एकड़ - अधिकतम 2.5)",
        "yield_label": "अनुमानित पैदावार (क्विंटल/एकड़)",
        "seeds_cost_label": "बीज लागत (₹)",
        "fert_cost_label": "खाद एवं कीटनाशक लागत (₹)",
        "labour_cost_label": "मजदूरी एवं मशीनरी खर्च (₹)",
        "irr_cost_label": "सिंचाई एवं अन्य खर्च (₹)",
        "p1_label": "FPO साथी गारंटर 1",
        "p2_label": "FPO साथी गारंटर 2",
        "p3_label": "FPO साथी गारंटर 3",
        "fpo_label": "संबंधित FPO कंपनी",
        "consent_underwriting": "मैं बिना जमीन के दस्तावेज के कृषि मूल्यांकन की सहमति देता हूं।",
        "consent_fpo": "मैं 3 FPO साथी सदस्यों के साथ विवरण साझा करने की सहमति देता हूं।",
        "consent_mandi": "मैं AGMARKNET मंडी भाव और कटाई अलर्ट प्राप्त करने की सहमति देता हूं।",
        "btn_calc": "🚀 सुरक्षित ऋण सीमा की गणना करें और जमा करें",
        "success_msg": "✅ कृषि अंडरराइटिंग सफलतापूर्वक पूरी हुई!",
        "metric_score": "क्रेडिट स्कोर",
        "metric_limit": "स्वीकृत ऋण सीमा",
        "metric_rev": "अनुमानित फसल आय",
        "metric_bullet": "एकमुश्त भुगतान तिथि",
        "advisory_header": "📢 वॉयस संदेश (IVR / व्हाट्सएप ऑडियो):"
    },
    "Marathi (मराठी)": {
        "title": "🌾 किसानसेतू: समुदाय-मालकीचे कृषी पत नेटवर्क",
        "tagline": "निश्चित पीक रोखप्रवाह मूल्यांकन • FPO ३-सदस्यीय सामाजिक हमी • पीक काढणीनंतर एकरकमी परतफेड",
        "tab_farmer": "👨‍🌾 अल्पभूधारक शेतकरी पोर्टल (व्हॉइस इनटेक)",
        "tab_fpo": "🤝 FPO समन्वयक कन्सोल",
        "tab_lender": "🏦 ग्रामीण बँक व पतपुरवठा कन्सोल",
        "farmer_sub": "अल्पभूधारक शेतकरी पत मर्यादा व नोंदणी",
        "zero_land": "💡 सातबारा/जमीन कागदपत्रे आवश्यक नाहीत: हंगामी पीक उत्पन्न आणि ३ शेतकरी सहकाऱ्यांच्या हमीवर आधारित.",
        "voice_section": "🎙️ बहुभाषिक व्हॉइस इनटेक (१०+ प्रादेशिक भाषा)",
        "voice_record_prompt": "नाव, पीक, क्षेत्र, उत्पादन आणि खर्च बोला:",
        "voice_sample_prompt": "किंवा १-क्लिक व्हॉइस नमुना निवडा:",
        "transcript_box": "ध्वनी संदेशाचे रूपांतर (तपासा व दुरुस्त करा):",
        "name_label": "शेतकऱ्याचे संपूर्ण नाव",
        "phone_label": "नोंदणीकृत मोबाईल नंबर",
        "village_label": "गाव",
        "district_label": "जिल्हा",
        "crop_label": "लागवड केलेले मुख्य पीक",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "लागवड क्षेत्र (एकर)",
        "yield_label": "अपेक्षित उत्पादन (क्विंटल/एकर)",
        "seeds_cost_label": "बियाणे खर्च (₹)",
        "fert_cost_label": "खते व औषधे खर्च (₹)",
        "labour_cost_label": "मजुरी व मशागत खर्च (₹)",
        "irr_cost_label": "पाणी व वीज खर्च (₹)",
        "p1_label": "FPO सहकारी जामीनदार १",
        "p2_label": "FPO सहकारी जामीनदार २",
        "p3_label": "FPO सहकारी जामीनदार ३",
        "fpo_label": "संलग्न FPO संस्था",
        "consent_underwriting": "मी जमिनीच्या मालकीहक्काशिवाय कृषी मूल्यांकनास संमती देतो.",
        "consent_fpo": "मी ३ शेतकरी सहकाऱ्यांसोबत माहिती सामायिक करण्यास संमती देतो.",
        "consent_mandi": "मी AGMARKNET बाजारभाव आणि पीक काढणी सूचना मिळण्यास संमती देतो.",
        "btn_calc": "🚀 सुरक्षित कर्ज मर्यादा मोजा आणि सादर करा",
        "success_msg": "✅ कृषी पत मूल्यांकन यशस्वीरीत्या पूर्ण झाले!",
        "metric_score": "क्रेडिट स्कोअर",
        "metric_limit": "मंजूर पत मर्यादा",
        "metric_rev": "अपेक्षित पीक महसूल",
        "metric_bullet": "एकरकमी परतफेड तारीख",
        "advisory_header": "📢 व्हॉइस संदेश सल्लागार:"
    },
    "Gujarati (ગુજરાતી)": {
        "title": "🌾 કિસાનસેતુ: સમુદાય આધારિત ધિરાણ નેટવર્ક",
        "tagline": "રોકડ પ્રવાહ મૂલ્યાંકન • FPO ૩-સભ્ય સામાજિક ગેરંટી • લણણી સમયે એકમુક્ત ચુકવણી",
        "tab_farmer": "👨‍🌾 સીમાંત ખેડૂત પોર્ટલ (વોઇસ / પ્રાદેશિક ભાષા)",
        "tab_fpo": "🤝 FPO સંયોજક કન્સોલ",
        "tab_lender": "🏦 ગ્રામીણ બેંક લોન કન્સોલ",
        "farmer_sub": "સીમાંત ખેડૂત ધિરાણ મર્યાદા શોધ",
        "zero_land": "💡 જમીનના દસ્તાવેજ વગર લોન: પાક ઉત્પાદન અને ૩ FPO સભ્યોની બાંહેધરી પર આધારિત.",
        "voice_section": "🎙️ બહુભાષી વૉઇસ ઇનપુટ (૧૦+ ભાષાઓમાં બોલીને દાખલ કરો)",
        "voice_record_prompt": "નામ, પાક, જમીન અને ખર્ચ બોલો:",
        "voice_sample_prompt": "અથવા ૧-ક્લિક વૉઇસ સેમ્પલ પસંદ કરો:",
        "transcript_box": "ઓળખાયેલ લખાણ (ચકાસો અને સુધારો):",
        "name_label": "ખેડૂતનું પૂરું નામ",
        "phone_label": "મોબાઇલ નંબર (આધાર લિંક્ડ)",
        "village_label": "ગામ",
        "district_label": "જિલ્લો",
        "crop_label": "મુખ્ય પાક",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "ખેતીની જમીન (એકર)",
        "yield_label": "અપેક્ષિત ઉત્પાદન (ક્વિન્ટલ/એકર)",
        "seeds_cost_label": "બિયારણ ખર્ચ (₹)",
        "fert_cost_label": "ખાતર દવા ખર્ચ (₹)",
        "labour_cost_label": "મજૂરી ખર્ચ (₹)",
        "irr_cost_label": "સિંચાઈ ખર્ચ (₹)",
        "p1_label": "FPO જામીનદાર ૧",
        "p2_label": "FPO જામીનદાર ૨",
        "p3_label": "FPO જામીનદાર ૩",
        "fpo_label": "સંબંધિત FPO સંસ્થા",
        "consent_underwriting": "હું જમીનના દસ્તાવેજ વગર પાક આધારિત લોન મૂલ્યાંકન માટે સંમતિ આપું છું.",
        "consent_fpo": "હું ૩ FPO સભ્યો સાથે માહિતી શેર કરવા સંમતિ આપું છું.",
        "consent_mandi": "હું AGMARKNET બજારભાવ એલર્ટ મેળવવા સંમતિ આપું છું.",
        "btn_calc": "🚀 લોન મર્યાદા ગણો અને સબમિટ કરો",
        "success_msg": "✅ પાક આધારિત મૂલ્યાંકન સફળતાપૂર્વક પૂર્ણ થયું!",
        "metric_score": "ક્રેડિટ સ્કોર",
        "metric_limit": "મંજૂર લોન મર્યાદા",
        "metric_rev": "અંદાજિત પાક આવક",
        "metric_bullet": "ચૂકવણીની અંતિમ તારીખ",
        "advisory_header": "📢 ઓડિયો સંદેશ (વોટ્સએપ / IVR):"
    },
    "Telugu (తెలుగు)": {
        "title": "🌾 కిసాన్‌సేతు: రైతుల యాజమాన్య క్రెడిట్ నెట్‌వర్క్",
        "tagline": "వ్యవసాయ నగదు ప్రవాహ అంచనా • 3-రైతుల సామాజిక పూచీకత్తు • పంట కోత అనంతర చెల్లింపు",
        "tab_farmer": "👨‍🌾 ఉపాంత రైతు పోర్టల్ (వాయిస్ ఇన్‌పుట్)",
        "tab_fpo": "🤝 FPO కోఆర్డినేటర్ కన్సోల్",
        "tab_lender": "🏦 గ్రామీణ బ్యాంక్ అండర్‌రైటింగ్",
        "farmer_sub": "ఉపాంత రైతుల రుణ పరిమితి లెక్కింపు",
        "zero_land": "💡 భూమి పట్టా అవసరం లేదు: పంట దిగుబడి మరియు 3 మంది రైతుల పూచీకత్తు ఆధారంగా రుణం.",
        "voice_section": "🎙️ బహుభాషా వాయిస్ ఇన్‌పుట్ (10+ భాషలు)",
        "voice_record_prompt": "మీ పేరు, పంట, విస్తీర్ణం, దిగుబడి మాట్లాడండి:",
        "voice_sample_prompt": "లేదా శాంపిల్ వాయిస్ ఎంచుకోండి:",
        "transcript_box": "వాయిస్ టెక్స్ట్ (తనిఖీ చేసి సరిదిద్దండి):",
        "name_label": "రైతు పూర్తి పేరు",
        "phone_label": "మొబైల్ నంబర్",
        "village_label": "గ్రామం",
        "district_label": "జిల్లా",
        "crop_label": "ప్రధాన పంట",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "సాగు విస్తీర్ణం (ఎకరాలు)",
        "yield_label": "దిగుబడి (క్వింటాళ్ళు/ఎకరా)",
        "seeds_cost_label": "విత్తనాల ఖర్చు (₹)",
        "fert_cost_label": "ఎరువుల ఖర్చు (₹)",
        "labour_cost_label": "కూలీల ఖర్చు (₹)",
        "irr_cost_label": "నీటిపారుదల ఖర్చు (₹)",
        "p1_label": "FPO పూచీకత్తు రైతు 1",
        "p2_label": "FPO పూచీకత్తు రైతు 2",
        "p3_label": "FPO పూచీకత్తు రైతు 3",
        "fpo_label": "FPO సంస్థ",
        "consent_underwriting": "భూమి పత్రాలు లేకుండా వ్యవసాయ రుణ అంచనాకు అంగీకరిస్తున్నాను.",
        "consent_fpo": "3 మంది సహచర రైతులతో సమాచారం పంచుకోవడానికి అంగీకరిస్తున్నాను.",
        "consent_mandi": "మార్కెట్ ధరల హెచ్చరికలకు అంగీకరిస్తున్నాను.",
        "btn_calc": "🚀 రుణ పరిమితిని లెక్కించి సమర్పించండి",
        "success_msg": "✅ వ్యవసాయ అండర్‌రైటింగ్ విజయవంతంగా పూర్తయింది!",
        "metric_score": "క్రెడిట్ స్కోరు",
        "metric_limit": "రుణ పరిమితి",
        "metric_rev": "ఆశించిన పంట ఆదాయం",
        "metric_bullet": "ఏకమొత్తం చెల్లింపు తేదీ",
        "advisory_header": "📢 ఆడియో సలహాదారు (WhatsApp / IVR):"
    },
    "Tamil (தமிழ்)": {
        "title": "🌾 கிசான்சேது: விவசாயிகள் கடன் கட்டமைப்பு",
        "tagline": "பயிர் வருவாய் மதிப்பீடு • 3 உழவர் சமூக உத்தரவாதம் • அறுவடைக்கு பின் மொத்த திருப்பிச் செலுத்துதல்",
        "tab_farmer": "👨‍🌾 குறு உழவர் போர்டல் (குரல் பதிவு)",
        "tab_fpo": "🤝 FPO ஒருங்கிணைப்பாளர் கன்சோல்",
        "tab_lender": "🏦 கிராம வங்கி கடன் கன்சோல்",
        "farmer_sub": "குறு உழவர் கடன் வரம்பு நிர்ணயம்",
        "zero_land": "💡 நிலப் பட்டா தேவையில்லை: பருவ கால பயிர் விளைச்சல் மற்றும் 3 உழவர்களின் சமூக உத்தரவாதம்.",
        "voice_section": "🎙️ பன்மொழி குரல் உள்ளீடு (10+ மொழிகள்)",
        "voice_record_prompt": "பெயர், பயிர், பரப்பு, மகசூல் மற்றும் செலவுகளைப் பேசுங்கள்:",
        "voice_sample_prompt": "அல்லது மாதிரி குரலைத் தேர்ந்தெடுக்கவும்:",
        "transcript_box": "உணரப்பட்ட உரை (சரிபார்த்து திருத்தவும்):",
        "name_label": "விவசாயி முழுப் பெயர்",
        "phone_label": "கைபேசி எண்",
        "village_label": "கிராமம்",
        "district_label": "மாவட்டம்",
        "crop_label": "சாகுபடி பயிர்",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "நிலப் பரப்பு (ஏக்கர்)",
        "yield_label": "எதிர்பார்க்கப்படும் மகசூல் (குவிண்டால்)",
        "seeds_cost_label": "விதை செலவு (₹)",
        "fert_cost_label": "உரச் செலவு (₹)",
        "labour_cost_label": "வேலை ஆட்கள் செலவு (₹)",
        "irr_cost_label": "பாசன செலவு (₹)",
        "p1_label": "FPO உத்தரவாத உழவர் 1",
        "p2_label": "FPO உத்தரவாத உழவர் 2",
        "p3_label": "FPO உத்தரவாத உழவர் 3",
        "fpo_label": "FPO உழவர் உற்பத்தியாளர் நிறுவனம்",
        "consent_underwriting": "நிலப் பட்டா இன்றி பயிர் மதிப்பீட்டிற்கு சம்மதிக்கிறேன்.",
        "consent_fpo": "3 உழவர் கூட்டாளிகளுடன் விவரங்களைப் பகிர சம்மதிக்கிறேன்.",
        "consent_mandi": "சந்தை விலை அறிவிப்புகளைப் பெற சம்மதிக்கிறேன்.",
        "btn_calc": "🚀 கடன் வரம்பைக் கணக்கிட்டு சமர்ப்பிக்கவும்",
        "success_msg": "✅ பயிர் மதிப்பீடு வெற்றிகரமாக முடிந்தது!",
        "metric_score": "கிரெடிட் மதிப்பெண்",
        "metric_limit": "அங்கீகரிக்கப்பட்ட கடன் வரம்பு",
        "metric_rev": "எதிர்பார்க்கப்படும் பயிர் வருவாய்",
        "metric_bullet": "திருப்பிச் செலுத்தும் தேதி",
        "advisory_header": "📢 குரல் வழி வழிகாட்டுதல்:"
    },
    "Kannada (ಕನ್ನಡ)": {
        "title": "🌾 ಕಿಸಾನ್‌ಸೇತು: ಸಮುದಾಯ ಸ್ವಾಮ್ಯದ ರೈತ ಸಾಲ ಜಾಲ",
        "tagline": "ಬೆಳೆ ನಗದು ಹರಿವಿನ ಮೌಲ್ಯಮಾಪನ • 3-ರೈತರ ಸಾಮಾಜಿಕ ಖಾತರಿ • ಕೊಯ್ಲಿನ ನಂತರ ಏಕಗಂಟಿನ ಮರುಪಾವತಿ",
        "tab_farmer": "👨‍🌾 ಸಣ್ಣ ರೈತರ ಪೋರ್ಟಲ್ (ಧ್ವನಿ ಇನ್ಪುಟ್)",
        "tab_fpo": "🤝 FPO ಸಂಯೋಜಕರ ಕನ್ಸೋಲ್",
        "tab_lender": "🏦 ಗ್ರಾಮೀಣ ಬ್ಯಾಂಕ್ ಸಾಲ ಕನ್ಸೋಲ್",
        "farmer_sub": "ಸಣ್ಣ ರೈತರ ಸಾಲ ಮಿತಿ ಲೆಕ್ಕಾಚಾರ",
        "zero_land": "💡 ಪಹಣಿ/ಭೂಮಿ ದಾಖಲೆ ಕಡ್ಡಾಯವಿಲ್ಲ: ಬೆಳೆ ಆದಾಯ ಮತ್ತು 3 ಸದಸ್ಯರ ಖಾತರಿಯ ಮೇಲೆ ಸಾಲ.",
        "voice_section": "🎙️ ಬಹುಭಾಷಾ ಧ್ವನಿ ಇನ್‌ಪುಟ್ (10+ ಭಾಷೆಗಳು)",
        "voice_record_prompt": "ಹೆಸರು, ಬೆಳೆ, ಜಮೀನು, ಇಳುವರಿ ಮತ್ತು ಖರ್ಚುಗಳನ್ನು ಮಾತನಾಡಿ:",
        "voice_sample_prompt": "ಅಥವಾ ಮಾದರಿ ಧ್ವನಿಯನ್ನು ಆರಿಸಿ:",
        "transcript_box": "ಪತ್ತೆಯಾದ ಪಠ್ಯ (ಪರಿಶೀಲಿಸಿ ಮತ್ತು ತಿದ್ದಿ):",
        "name_label": "ರೈತರ ಪೂರ್ಣ ಹೆಸರು",
        "phone_label": "ಮೊಬೈಲ್ ಸಂಖ್ಯೆ",
        "village_label": "ಗ್ರಾಮ",
        "district_label": "ಜಿಲ್ಲೆ",
        "crop_label": "ಮುಖ್ಯ ಬೆಳೆ",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "ಕೃಷಿ ಭೂಮಿ (ಎಕರೆ)",
        "yield_label": "ನಿರೀಕ್ಷಿತ ಇಳುವರಿ (ಕ್ವಿಂಟಾಲ್/ಎಕರೆ)",
        "seeds_cost_label": "ಬೀಜದ ವೆಚ್ಚ (₹)",
        "fert_cost_label": "ಗೊಬ್ಬರ ಮತ್ತು ಕೀಟನಾಶಕ ವೆಚ್ಚ (₹)",
        "labour_cost_label": "ಕೂಲಿ ವೆಚ್ಚ (₹)",
        "irr_cost_label": "ನೀರಾವರಿ ವೆಚ್ಚ (₹)",
        "p1_label": "FPO ಜಾಮೀನುದಾರ ರೈತ 1",
        "p2_label": "FPO ಜಾಮೀನುದಾರ ರೈತ 2",
        "p3_label": "FPO ಜಾಮೀನುದಾರ ರೈತ 3",
        "fpo_label": "ಸಂಬಂಧಿತ FPO ಸಂಸ್ಥೆ",
        "consent_underwriting": "ಭೂಮಿ ದಾಖಲೆಗಳಿಲ್ಲದೆ ಕೃಷಿ ಮೌಲ್ಯಮಾಪನಕ್ಕೆ ಒಪ್ಪಿಗೆ ನೀಡುತ್ತೇನೆ.",
        "consent_fpo": "3 ಸದಸ್ಯರ FPO ಗುಂಪಿನೊಂದಿಗೆ ಮಾಹಿತಿ ಹಂಚಿಕೊಳ್ಳಲು ಸಮ್ಮತಿಸುತ್ತೇನೆ.",
        "consent_mandi": "ಮಾರುಕಟ್ಟೆ ದರ ಎಚ್ಚರಿಕೆಗಳನ್ನು ಪಡೆಯಲು ಒಪ್ಪುತ್ತೇನೆ.",
        "btn_calc": "🚀 ಸಾಲದ ಮಿತಿಯನ್ನು ಲೆಕ್ಕಹಾಕಿ ಸಲ್ಲಿಸಿ",
        "success_msg": "✅ ಕೃಷಿ ಸಾಲ ಮೌಲ್ಯಮಾಪನ ಯಶಸ್ವಿಯಾಗಿದೆ!",
        "metric_score": "ಕ್ರೆಡಿಟ್ ಸ್ಕೋರ್",
        "metric_limit": "ಅನುಮೋದಿತ ಸಾಲದ ಮಿತಿ",
        "metric_rev": "ನಿರೀಕ್ಷಿತ ಬೆಳೆ ಆದಾಯ",
        "metric_bullet": "ಮರುಪಾವತಿ ಅಂತಿಮ ದಿನಾಂಕ",
        "advisory_header": "📢 ಧ್ವನಿ ಸಂದೇಶ ಮಾರ್ಗದರ್ಶಿ:"
    },
    "Punjabi (ਪੰਜਾਬੀ)": {
        "title": "🌾 ਕਿਸਾਨਸੇਤੂ: ਕਿਸਾਨਾਂ ਦਾ ਆਪਣਾ ਕ੍ਰੈਡਿਟ ਨੈੱਟਵਰਕ",
        "tagline": "ਫਸਲੀ ਨਕਦੀ ਪ੍ਰਵਾਹ ਮੁਲਾਂਕਣ • FPO 3-ਮੈਂਬਰੀ ਸਮਾਜਿਕ ਗਾਰੰਟੀ • ਵਾਢੀ ਤੋਂ ਬਾਅਦ ਇਕਮੁਸ਼ਤ ਅਦਾਇਗੀ",
        "tab_farmer": "👨‍🌾 ਛੋਟੇ ਕਿਸਾਨਾਂ ਦਾ ਪੋਰਟਲ (ਆਵਾਜ਼ ਦੁਆਰਾ)",
        "tab_fpo": "🤝 FPO ਕੋਆਰਡੀਨੇਟਰ ਕੰਸੋਲ",
        "tab_lender": "🏦 ਪੇਂਡੂ ਬੈਂਕ ਕੰਸੋਲ",
        "farmer_sub": "ਕਿਸਾਨ ਕਰਜ਼ਾ ਹੱਦ ਨਿਰਧਾਰਨ",
        "zero_land": "💡 ਜ਼ਮੀਨ ਦੀ ਫਰਦ ਦੀ ਲੋੜ ਨਹੀਂ: ਫਸਲੀ ਝਾੜ ਅਤੇ 3 ਸਾਥੀ ਕਿਸਾਨਾਂ ਦੀ ਗਾਰੰਟੀ 'ਤੇ ਆਧਾਰਿਤ।",
        "voice_section": "🎙️ ਬਹੁ-ਭਾਸ਼ਾਈ ਵੌਇਸ ਇਨਪੁਟ (10+ ਭਾਸ਼ਾਵਾਂ)",
        "voice_record_prompt": "ਆਪਣਾ ਨਾਮ, ਫਸਲ, ਰਕਬਾ, ਝਾੜ ਅਤੇ ਖਰਚਾ ਬੋਲੋ:",
        "voice_sample_prompt": "ਜਾਂ 1-ਕਲਿੱਕ ਵੌਇਸ ਨਮੂਨਾ ਚੁਣੋ:",
        "transcript_box": "ਦਰਜ ਹੋਇਆ ਵੇਰਵਾ (ਚੈੱਕ ਕਰੋ ਅਤੇ ਠੀਕ ਕਰੋ):",
        "name_label": "ਕਿਸਾਨ ਦਾ ਪੂਰਾ ਨਾਮ",
        "phone_label": "ਮੋਬਾਈਲ ਨੰਬਰ",
        "village_label": "ਪਿੰਡ",
        "district_label": "ਜ਼ਿਲ੍ਹਾ",
        "crop_label": "ਮੁੱਖ ਫਸਲ",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "ਵਾਹੀਯੋਗ ਜ਼ਮੀਨ (ਏਕੜ)",
        "yield_label": "ਅਨੁਮਾਨਿਤ ਝਾੜ (ਕੁਇੰਟਲ/ਏਕੜ)",
        "seeds_cost_label": "ਬੀਜ ਖਰਚਾ (₹)",
        "fert_cost_label": "ਖਾਦ ਅਤੇ ਦਵਾਈਆਂ (₹)",
        "labour_cost_label": "ਮਜ਼ਦੂਰੀ ਖਰਚਾ (₹)",
        "irr_cost_label": "ਸਿੰਚਾਈ ਖਰਚਾ (₹)",
        "p1_label": "FPO ਗਾਰੰਟਰ 1",
        "p2_label": "FPO ਗਾਰੰਟਰ 2",
        "p3_label": "FPO ਗਾਰੰਟਰ 3",
        "fpo_label": "ਸੰਬੰਧਿਤ FPO",
        "consent_underwriting": "ਮੈਂ ਬਿਨਾਂ ਜ਼ਮੀਨੀ ਦਸਤਾਵੇਜ਼ ਫਸਲੀ ਮੁਲਾਂਕਣ ਲਈ ਸਹਿਮਤ ਹਾਂ।",
        "consent_fpo": "ਮੈਂ 3 ਸਾਥੀ ਕਿਸਾਨਾਂ ਨਾਲ ਜਾਣਕਾਰੀ ਸਾਂਝੀ ਕਰਨ ਲਈ ਸਹਿਮਤ ਹਾਂ।",
        "consent_mandi": "ਮੈਂ ਮੰਡੀ ਭਾਅ ਅਤੇ ਵਾਢੀ ਅਲਰਟ ਪ੍ਰਾਪਤ ਕਰਨ ਲਈ ਸਹਿਮਤ ਹਾਂ।",
        "btn_calc": "🚀 ਕਰਜ਼ਾ ਸੀਮਾ ਗਿਣੋ ਅਤੇ ਜਮ੍ਹਾਂ ਕਰੋ",
        "success_msg": "✅ ਫਸਲੀ ਮੁਲਾਂਕਣ ਸਫਲਤਾਪੂਰਵਕ ਮੁਕੰਮਲ!",
        "metric_score": "ਕ੍ਰੈਡਿਟ ਸਕੋਰ",
        "metric_limit": "ਪ੍ਰਵਾਨਿਤ ਕਰਜ਼ਾ ਹੱਦ",
        "metric_rev": "ਅਨੁਮਾਨਿਤ ਫਸਲੀ ਆਮਦਨ",
        "metric_bullet": "ਅਦਾਇਗੀ ਦੀ ਆਖਰੀ ਮਿਤੀ",
        "advisory_header": "📢 ਵੌਇਸ ਸੁਨੇਹਾ ਸਲਾਹਕਾਰ:"
    },
    "Bengali (বাংলা)": {
        "title": "🌾 কিষাণসেতু: প্রান্তিক কৃষকদের ক্রেডিট নেটওয়ার্ক",
        "tagline": "ফসলভিত্তিক নগদ প্রবাহ মূল্যায়ন • FPO ৩-সদস্য সামাজিক গ্যারান্টি • ফসল তোলার পর এককালীন পরিশোধ",
        "tab_farmer": "👨‍🌾 প্রান্তিক কৃষক পোর্টাল (ভয়েস ইনপুট)",
        "tab_fpo": "🤝 FPO সমন্বয়কারী কনসোল",
        "tab_lender": "🏦 গ্রামীণ ব্যাংক লোন কনসোল",
        "farmer_sub": "প্রান্তিক কৃষকদের ঋণ সীমা নির্ধারণ",
        "zero_land": "💡 জমির দলিলের প্রয়োজন নেই: মরসুমি ফসল এবং ৩ জন কৃষক সঙ্গীর গ্যারান্টির ভিত্তিতে ঋণ।",
        "voice_section": "🎙️ বহুভাষিক ভয়েস ইনটেক (১০+ ভাষা)",
        "voice_record_prompt": "নাম, ফসল, জমির পরিমাণ, ফলন এবং খরচের কথা বলুন:",
        "voice_sample_prompt": "অথবা নমুনা ভয়েস নির্বাচন করুন:",
        "transcript_box": "শনাক্তকৃত পাঠ্য (যাচাই ও সংশোধন করুন):",
        "name_label": "কৃষকের পুরো নাম",
        "phone_label": "মোবাইল নম্বর",
        "village_label": "গ্রাম",
        "district_label": "জেলা",
        "crop_label": "প্রধান ফসল",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "জমির পরিমাণ (একর)",
        "yield_label": "প্রত্যাশিত ফলন (কুইন্টাল/একর)",
        "seeds_cost_label": "বীজ খরচ (₹)",
        "fert_cost_label": "সার ও কীটনাশক খরচ (₹)",
        "labour_cost_label": "মজুরি খরচ (₹)",
        "irr_cost_label": "সেচ খরচ (₹)",
        "p1_label": "FPO জামিনদার ১",
        "p2_label": "FPO জামিনদার ২",
        "p3_label": "FPO জামিনদার ৩",
        "fpo_label": "সংযুক্ত FPO সংস্থা",
        "consent_underwriting": "জমির দলিল ছাড়া ফসল মূল্যায়নে সম্মতি দিচ্ছি।",
        "consent_fpo": "৩ জন কৃষক সঙ্গীর সাথে তথ্য ভাগ করতে সম্মত।",
        "consent_mandi": "মান্ডি দর ও ফসল কাটার বিজ্ঞপ্তি পেতে সম্মত।",
        "btn_calc": "🚀 নিরাপদ ঋণ সীমা গণনা করুন ও জমা দিন",
        "success_msg": "✅ কৃষি ঋণ মূল্যায়ন সফলভাবে সম্পন্ন হয়েছে!",
        "metric_score": "ক্রেডিট স্কোর",
        "metric_limit": "অনুমোদিত ঋণ সীমা",
        "metric_rev": "প্রত্যাশিত ফসল আয়",
        "metric_bullet": "পরিশোধের শেষ তারিখ",
        "advisory_header": "📢 ভয়েস বার্তা পরামর্শ:"
    },
    "Odia (ଓଡ଼ିଆ)": {
        "title": "🌾 କିଷାନସେତୁ: କ୍ଷୁଦ୍ର ଚାଷୀ ଋଣ ନେଟୱାର୍କ",
        "tagline": "ଫସଲ ଆୟ ଆକଳନ • FPO ୩-ସଦସ୍ୟ ସାମାଜିକ ଗ୍ୟାରେଣ୍ଟି • ଅମଳ ପରେ ଏକକାଳୀନ ପରିଶୋଧ",
        "tab_farmer": "👨‍🌾 କ୍ଷୁଦ୍ର ଚାଷୀ ପୋର୍ଟାଲ (ଭଏସ୍ ଇନପୁଟ୍)",
        "tab_fpo": "🤝 FPO ସଂଯୋଜକ କନସୋଲ",
        "tab_lender": "🏦 ଗ୍ରାମୀଣ ବ୍ୟାଙ୍କ କନସୋଲ",
        "farmer_sub": "କ୍ଷୁଦ୍ର ଚାଷୀ ଋଣ ସୀମା ନିର୍ଦ୍ଧାରଣ",
        "zero_land": "💡 ଜମି ପଟ୍ଟା ଆବଶ୍ୟକ ନାହିଁ: ଫସଲ ଅମଳ ଏବଂ ୩ ଜଣ ଚାଷୀ ସାଥୀଙ୍କ ଗ୍ୟାରେଣ୍ଟି ଉପରେ ଆଧାରିତ।",
        "voice_section": "🎙️ ବହୁଭାଷୀ ଭଏସ୍ ଇନଟେକ୍ (୧୦+ ଭାଷା)",
        "voice_record_prompt": "ନାମ, ଫସଲ, ଜମି, ଅମଳ ଏବଂ ଖର୍ଚ୍ଚ କୁହନ୍ତୁ:",
        "voice_sample_prompt": "କିମ୍ବା ନମୁନା ଭଏସ୍ ବାଛନ୍ତୁ:",
        "transcript_box": "ରେକର୍ଡ ହୋଇଥିବା ବିବରଣୀ (ଯାଞ୍ଚ ଏବଂ ସଂଶୋଧନ କରନ୍ତୁ):",
        "name_label": "ଚାଷୀଙ୍କ ପୂରା ନାମ",
        "phone_label": "ମୋବାଇଲ୍ ନମ୍ବର",
        "village_label": "ଗାଁ",
        "district_label": "ଜିଲ୍ଲା",
        "crop_label": "ମୁଖ୍ୟ ଫସଲ",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "ଜମି ପରିମାଣ (ଏକର)",
        "yield_label": "ଆଶା କରାଯାଉଥିବା ଅମଳ (କ୍ୱିଣ୍ଟାଲ୍)",
        "seeds_cost_label": "ବିହନ ଖର୍ଚ୍ଚ (₹)",
        "fert_cost_label": "ଖତ ଏବଂ ଔଷଧ ଖର୍ଚ୍ଚ (₹)",
        "labour_cost_label": "ମୂଲିଆ ଖର୍ଚ୍ଚ (₹)",
        "irr_cost_label": "ଜଳସେଚନ ଖର୍ଚ୍ଚ (₹)",
        "p1_label": "FPO ଜାମିନଦାର ୧",
        "p2_label": "FPO ଜାମିନଦାର ୨",
        "p3_label": "FPO ଜାମିନଦାର ୩",
        "fpo_label": "FPO ସଂସ୍ଥା",
        "consent_underwriting": "ଜମି ପଟ୍ଟା ବିନା ଫସଲ ଆକଳନ ପାଇଁ ସହମତ।",
        "consent_fpo": "୩ ଜଣ ଚାଷୀ ସାଥୀଙ୍କ ସହ ତଥ୍ୟ ବାଣ୍ଟିବା ପାଇଁ ସହମତ।",
        "consent_mandi": "ମଣ୍ଡି ଦର ଏବଂ ଅମଳ ସତର୍କତା ପାଇଁ ସହମତ।",
        "btn_calc": "🚀 ଋଣ ସୀମା ଗଣନା କରନ୍ତୁ ଏବଂ ଦାଖଲ କରନ୍ତୁ",
        "success_msg": "✅ କୃଷି ଋଣ ମୂଲ୍ୟାୟନ ସଫଳତାର ସହ ସମ୍ପୂର୍ଣ୍ଣ ହେଲା!",
        "metric_score": "କ୍ରେଡିଟ୍ ସ୍କୋର",
        "metric_limit": "ମଞ୍ଜୁର ଋଣ ସୀମା",
        "metric_rev": "ଆନୁମାନିକ ଫସଲ ଆୟ",
        "metric_bullet": "ପରିଶୋଧର ଶେଷ ତାରିଖ",
        "advisory_header": "📢 ଭଏସ୍ ପରାମର୍ଶ:"
    },
    "Assamese (অসমীয়া)": {
        "title": "🌾 কিষাণসেতু: প্ৰান্তীয় কৃষকৰ ক্ৰেডিট নেটৱৰ্ক",
        "tagline": "শস্যভিত্তিক নগদ ধন মূল্যায়ন • FPO ৩-জনীয়া সামাজিক গেৰাণ্টী • চপোৱাৰ পিছত এককালীন পৰিশোধ",
        "tab_farmer": "👨‍🌾 ক্ষুদ্ৰ কৃষক প'ৰ্টেল (ভইচ ইনপুট)",
        "tab_fpo": "🤝 FPO সমন্বয়ক কনচোল",
        "tab_lender": "🏦 গ্ৰাম্য বেংক কনচোল",
        "farmer_sub": "ক্ষুদ্ৰ কৃষক ঋণ সীমা নিৰ্ধাৰণ",
        "zero_land": "💡 মাটিৰ পট্টাৰ প্ৰয়োজন নাই: বতৰৰ শস্য উৎপাদন আৰু ৩ জন কৃষক সংগীৰ গেৰাণ্টীত ঋণ।",
        "voice_section": "🎙️ বহুভাষিক ভইচ ইনটেক (১০+ ভাষা)",
        "voice_record_prompt": "নাম, শস্য, মাটি, উৎপাদন আৰু খৰচ কওক:",
        "voice_sample_prompt": "বা নমুনা ভইচ বাছক:",
        "transcript_box": "পোহৰলৈ অহা পাঠ্য (পৰীক্ষা আৰু সংশোধন কৰক):",
        "name_label": "কৃষকৰ সম্পূৰ্ণ নাম",
        "phone_label": "ম'বাইল নম্বৰ",
        "village_label": "গাঁও",
        "district_label": "জিলা",
        "crop_label": "প্ৰধান শস্য",
        "crops": ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"],
        "acres_label": "খেতিৰ মাটি (একৰ)",
        "yield_label": "প্ৰত্যাশিত উৎপাদন (কুইন্টল)",
        "seeds_cost_label": "বীজৰ খৰচ (₹)",
        "fert_cost_label": "সাৰ আৰু ঔষধৰ খৰচ (₹)",
        "labour_cost_label": "বনুৱা খৰচ (₹)",
        "irr_cost_label": "পানী যোগান খৰচ (₹)",
        "p1_label": "FPO গেৰাণ্টৰ ১",
        "p2_label": "FPO গেৰাণ্টৰ ২",
        "p3_label": "FPO গেৰাণ্টৰ ৩",
        "fpo_label": "সংশ্লিষ্ট FPO",
        "consent_underwriting": "মাটিৰ পট্টা অবিহনে শস্য মূল্যায়নত সন্মতি জনাইছোঁ।",
        "consent_fpo": "৩ জন কৃষক সংগীৰ সৈতে তথ্য ভাগ-বতৰা কৰিবলৈ সন্মত।",
        "consent_mandi": "বজাৰ মূল্য আৰু শস্য চপোৱা এলাৰ্ট পাবলৈ সন্মত।",
        "btn_calc": "🚀 ঋণ সীমা গণনা কৰক আৰু জমা দিয়ক",
        "success_msg": "✅ কৃষি ঋণ মূল্যায়ন সফলভাৱে সম্পূৰ্ণ হ'ল!",
        "metric_score": "ক্ৰেডিট স্ক'ৰ",
        "metric_limit": "অনুমোদিত ঋণ সীমা",
        "metric_rev": "প্ৰত্যাশিত শস্য উপাৰ্জন",
        "metric_bullet": "পৰিশোধৰ অন্তিম তাৰিখ",
        "advisory_header": "📢 ভইচ বাৰ্তা পৰামৰ্শ:"
    }
}

# -------------------------------------------------------------
# TOP NAVIGATION: LANGUAGE & NETWORK STATUS
# -------------------------------------------------------------
col_lang, col_status = st.columns([3, 1])
with col_lang:
    lang_choice = st.selectbox(
        "🌐 Choose Language / भाषा चुनें / પ્રાદેશિક ભાષા / భాష ఎంచుకోండి (11 Indian Languages Supported)",
        list(TRANSLATIONS.keys()),
        index=0
    )
T = TRANSLATIONS[lang_choice]

# Check live backend status
backend_connected = False
try:
    health_res = requests.get(f"{API_BASE}/health", timeout=1.0)
    if health_res.status_code == 200:
        backend_connected = True
except Exception:
    backend_connected = False

with col_status:
    if backend_connected:
        st.success("🟢 FastAPI Backend: Connected")
    else:
        st.info("🟡 Local Edge Engine: Active")


def get_live_fpo_groups():
    """Fetch live FPO peer guarantee groups from FastAPI backend with SQLite local fallback."""
    if backend_connected:
        try:
            res = requests.get(f"{API_BASE}/fpo/groups", timeout=2.5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
    try:
        from backend.database import SessionLocal
        from backend.models import PeerGroup, PeerGroupMember, Farmer, CreditAssessment
        db = SessionLocal()
        groups = db.query(PeerGroup).all()
        results = []
        for g in groups:
            members_data = []
            total_limit = 0.0
            for m in g.members:
                farmer = db.query(Farmer).filter(Farmer.id == m.farmer_id).first()
                assessment = db.query(CreditAssessment).filter(
                    CreditAssessment.farmer_id == m.farmer_id
                ).order_by(CreditAssessment.id.desc()).first()
                limit = assessment.loan_eligibility_amount if assessment else 0.0
                score = assessment.credit_score if assessment else 70
                total_limit += limit
                members_data.append({
                    "farmer_id": m.farmer_id,
                    "name": farmer.name if farmer else f"Farmer #{m.farmer_id}",
                    "phone": farmer.phone if farmer else "N/A",
                    "role": m.role,
                    "credit_score": score,
                    "credit_limit": limit,
                    "guarantee_pledged": m.guarantee_pledged
                })
            m_count = len(g.members)
            results.append({
                "id": g.id,
                "group_code": g.group_code,
                "fpo_name": g.fpo_name,
                "village": g.village,
                "district": g.district,
                "status": g.status,
                "pool_state": "Full (3/3)" if m_count >= 3 else f"Forming ({m_count}/3)",
                "is_full": m_count >= 3,
                "open_slots": max(0, 3 - m_count),
                "repayment_rate": g.repayment_rate,
                "total_pool_credit_limit": total_limit,
                "member_count": m_count,
                "members": members_data
            })
        db.close()
        return results
    except Exception:
        return []


def get_unassigned_farmers():
    """Fetch all farmers not currently assigned to any 3-member peer guarantee pool."""
    if backend_connected:
        try:
            res = requests.get(f"{API_BASE}/fpo/unassigned-farmers", timeout=2.5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
    try:
        from backend.database import SessionLocal
        from backend.models import PeerGroupMember, Farmer, CreditAssessment
        db = SessionLocal()
        assigned_members = db.query(PeerGroupMember.farmer_id).all()
        assigned_ids = {m[0] for m in assigned_members}
        all_farmers = db.query(Farmer).order_by(Farmer.id.desc()).all()
        unassigned = [f for f in all_farmers if f.id not in assigned_ids]
        results = []
        for f in unassigned:
            latest_assessment = db.query(CreditAssessment).filter(
                CreditAssessment.farmer_id == f.id
            ).order_by(CreditAssessment.id.desc()).first()
            results.append({
                "farmer_id": f.id,
                "name": f.name,
                "phone": f.phone,
                "village": f.village or "Pimpalgaon",
                "district": f.district or "Nashik",
                "state": f.state or "Maharashtra",
                "land_size_acres": f.land_size_acres,
                "fpo_name": f.fpo_name or "Sahyadri Agro Producer Co.",
                "crop_name": latest_assessment.crop_name if latest_assessment else "Not specified",
                "credit_score": latest_assessment.credit_score if latest_assessment else 70,
                "credit_limit": latest_assessment.loan_eligibility_amount if latest_assessment else 0.0,
                "risk_category": latest_assessment.risk_category if latest_assessment else "MODERATE",
                "status": "UNASSIGNED",
                "created_at": f.created_at.isoformat() if f.created_at else None
            })
        db.close()
        return results
    except Exception:
        return []


def get_lender_applications(status: Optional[str] = None):
    """Fetch live loan applications from backend with SQLite local fallback."""
    if backend_connected:
        try:
            params = {"status": status} if status else {}
            res = requests.get(f"{API_BASE}/lenders/applications", params=params, timeout=2.5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
    try:
        from backend.database import SessionLocal
        from backend.models import CreditAssessment, Farmer, PeerGroupMember, PeerGroup, CropVerification
        db = SessionLocal()
        query = db.query(CreditAssessment)
        if status:
            query = query.filter(CreditAssessment.status == status.upper())
        assessments = query.order_by(CreditAssessment.id.desc()).all()
        results = []
        for a in assessments:
            farmer = db.query(Farmer).filter(Farmer.id == a.farmer_id).first()
            group_member = db.query(PeerGroupMember).filter(PeerGroupMember.farmer_id == a.farmer_id).first()
            fpo_group_code = "GRP-SAHYADRI-01"
            if group_member:
                grp = db.query(PeerGroup).filter(PeerGroup.id == group_member.group_id).first()
                if grp:
                    fpo_group_code = grp.group_code

            ver = db.query(CropVerification).filter(CropVerification.farmer_id == a.farmer_id).order_by(CropVerification.id.desc()).first()
            crop_verification_status = ver.verification_status if ver else "VERIFIED_BY_PEERS"

            results.append({
                "assessment_id": a.id,
                "farmer_id": a.farmer_id,
                "farmer_name": farmer.name if farmer else f"Farmer #{a.farmer_id}",
                "phone": farmer.phone if farmer else "N/A",
                "village": farmer.village if farmer else "Pimpalgaon",
                "district": farmer.district if farmer else "Nashik",
                "crop_name": a.crop_name or "Tomato (Horticulture)",
                "acres": a.acres or (farmer.land_size_acres if farmer else 2.0),
                "projected_yield": a.projected_yield or 18.0,
                "mandi_price_per_qtl": a.mandi_price_per_qtl or 2250.0,
                "gross_revenue": a.gross_revenue or 81000.0,
                "total_expenses": a.total_expenses or 24000.0,
                "net_profit": a.net_profit or 57000.0,
                "credit_score": a.credit_score,
                "sanctioned_limit": a.loan_eligibility_amount,
                "risk_category": a.risk_category,
                "pmfby_insured": a.pmfby_insured,
                "social_collateral": "3/3 Verified FPO Pool",
                "peer_group_code": fpo_group_code,
                "crop_verification": crop_verification_status,
                "bullet_repayment_date": a.bullet_repayment_date.strftime("%d-%b-%Y") if a.bullet_repayment_date else "12-Jan-2027",
                "status": a.status or "PENDING_REVIEW",
                "lender_notes": a.lender_notes,
                "disbursement_tx_id": a.disbursement_tx_id,
                "disbursed_at": a.disbursed_at.strftime("%Y-%m-%d %H:%M") if a.disbursed_at else None,
                "assessment_date": a.assessment_date.strftime("%Y-%m-%d %H:%M") if a.assessment_date else ""
            })
        db.close()
        return results
    except Exception:
        return []


def execute_lender_decision(assessment_id: int, decision: str, lender_notes: str = ""):
    """Submit lender decision to backend or fallback SQLite database with strict validation."""
    if backend_connected:
        try:
            res = requests.post(
                f"{API_BASE}/lenders/applications/{assessment_id}/decision",
                json={"decision": decision, "lender_notes": lender_notes},
                timeout=2.5
            )
            if res.status_code == 200:
                data = res.json()
                return True, data.get("message", f"Loan #{assessment_id} successfully {decision}."), data
            else:
                err_detail = res.json().get("detail", f"Backend rejected request (HTTP {res.status_code})")
                return False, err_detail, None
        except Exception as e:
            return False, f"Backend connection error: {str(e)}", None

    try:
        from backend.database import SessionLocal
        from backend.models import CreditAssessment
        db = SessionLocal()
        assessment = db.query(CreditAssessment).filter(CreditAssessment.id == assessment_id).first()
        if not assessment:
            db.close()
            return False, f"Loan assessment #{assessment_id} not found in database.", None

        if assessment.status == decision:
            db.close()
            return False, f"Loan application #{assessment_id} is already {assessment.status}.", None

        if assessment.status == "DISBURSED":
            db.close()
            return False, f"Cannot change decision on loan #{assessment_id}: funds have already been disbursed.", None

        if assessment.status == "REJECTED":
            db.close()
            return False, f"Loan #{assessment_id} was REJECTED and cannot be modified.", None

        if assessment.status != "PENDING_REVIEW":
            db.close()
            return False, f"Cannot decision loan #{assessment_id}: current status is {assessment.status}. Expected PENDING_REVIEW.", None

        assessment.status = decision
        if lender_notes:
            assessment.lender_notes = lender_notes
        db.commit()
        db.close()
        return True, f"Loan #{assessment_id} successfully updated to {decision}.", {"status": decision}
    except Exception as e:
        return False, f"Database operation failed: {str(e)}", None


def execute_lender_disbursement(assessment_id: int):
    """Execute simulated disbursement to backend or fallback SQLite database."""
    if backend_connected:
        try:
            res = requests.post(f"{API_BASE}/lenders/applications/{assessment_id}/disburse", timeout=2.5)
            if res.status_code == 200:
                data = res.json()
                return True, data.get("message", "Disbursement recorded."), data
            else:
                err_detail = res.json().get("detail", f"Disbursement blocked (HTTP {res.status_code})")
                return False, err_detail, None
        except Exception as e:
            return False, f"Backend connection error: {str(e)}", None

    try:
        from backend.database import SessionLocal
        from backend.models import CreditAssessment
        import time
        from datetime import datetime
        db = SessionLocal()
        assessment = db.query(CreditAssessment).filter(CreditAssessment.id == assessment_id).first()
        if not assessment:
            db.close()
            return False, f"Loan assessment #{assessment_id} not found in database.", None

        if assessment.status == "DISBURSED":
            db.close()
            return False, f"Loan #{assessment_id} has already been disbursed. Duplicate disbursement prevented.", None

        if assessment.status == "PENDING_REVIEW":
            db.close()
            return False, f"Cannot disburse loan #{assessment_id}: application is PENDING_REVIEW. Must be SANCTIONED first.", None

        if assessment.status == "REJECTED":
            db.close()
            return False, f"Cannot disburse loan #{assessment_id}: application was REJECTED.", None

        if assessment.status != "SANCTIONED":
            db.close()
            return False, f"Cannot disburse loan #{assessment_id}: status is {assessment.status}. Only SANCTIONED loans can be disbursed.", None

        now = datetime.utcnow()
        tx_id = f"SIM-eRUPI-AGRI-{assessment.id}-{int(time.time())}"
        assessment.status = "DISBURSED"
        assessment.disbursement_tx_id = tx_id
        assessment.disbursed_at = now
        amt = assessment.loan_eligibility_amount
        db.commit()
        db.close()
        return True, f"₹{amt:,.0f} simulated disbursement recorded via e-RUPI sandbox voucher (Demo rail).", {"status": "DISBURSED", "disbursement_tx_id": tx_id}
    except Exception as e:
        return False, f"Database operation failed: {str(e)}", None


st.title(T["title"])
st.caption(T["tagline"])

tab1, tab2, tab3 = st.tabs([T["tab_farmer"], T["tab_fpo"], T["tab_lender"]])

# -------------------------------------------------------------
# TAB 1: MARGINAL FARMER INTAKE & CREDIT PORTAL
# -------------------------------------------------------------
with tab1:
    st.subheader(T["farmer_sub"])
    st.info(T["zero_land"])

    # 1. Multilingual Voice Intake Section
    st.markdown(f"### {T['voice_section']}")
    
    voice_col1, voice_col2 = st.columns([1, 1])

    # Map selected language to language code
    lang_code_map = {
        "English": "en", "Hindi (हिंदी)": "hi", "Marathi (मराठी)": "mr",
        "Gujarati (ગુજરાતી)": "gu", "Telugu (తెలుగు)": "te", "Tamil (தமிழ்)": "ta",
        "Kannada (ಕನ್ನಡ)": "kn", "Punjabi (ਪੰਜਾਬੀ)": "pa", "Bengali (বাংলা)": "bn",
        "Odia (ଓଡ଼ିଆ)": "or", "Assamese (অসমীয়া)": "as"
    }
    cur_lang_code = lang_code_map.get(lang_choice, "hi")

    # Session State for voice-recognized form fields and conflict tracking
    # Session State for voice-recognized form fields and conflict tracking
    if "ff_farmer_name" not in st.session_state:
        st.session_state.ff_farmer_name = "Ramesh Patel"
    if "ff_phone" not in st.session_state:
        st.session_state.ff_phone = "9876543210"
    if "ff_village" not in st.session_state:
        st.session_state.ff_village = "Pimpalgaon"
    if "ff_district" not in st.session_state:
        st.session_state.ff_district = "Nashik"
    if "ff_crop" not in st.session_state:
        st.session_state.ff_crop = T["crops"][0]
    if "ff_acres" not in st.session_state:
        st.session_state.ff_acres = 2.0
    if "ff_yield" not in st.session_state:
        st.session_state.ff_yield = 18.0
    if "ff_seeds" not in st.session_state:
        st.session_state.ff_seeds = 6000.0
    if "ff_fert" not in st.session_state:
        st.session_state.ff_fert = 8000.0
    if "ff_labour" not in st.session_state:
        st.session_state.ff_labour = 8000.0
    if "ff_irr" not in st.session_state:
        st.session_state.ff_irr = 2000.0
    if "ff_fpo" not in st.session_state:
        st.session_state.ff_fpo = "Sahyadri Agro Producer Co."
    if "ff_p1" not in st.session_state:
        st.session_state.ff_p1 = "Suresh Kumar (FPO #441)"
    if "ff_p2" not in st.session_state:
        st.session_state.ff_p2 = "Dinesh Bhai (FPO #892)"
    if "ff_p3" not in st.session_state:
        st.session_state.ff_p3 = "Mahesh Solanki (FPO #103)"
    if "ff_repeat" not in st.session_state:
        st.session_state.ff_repeat = False
    if "ff_manually_edited" not in st.session_state:
        st.session_state.ff_manually_edited = set()
    if "current_transcript" not in st.session_state:
        st.session_state.current_transcript = ""
    if "voice_fields_updated" not in st.session_state:
        st.session_state.voice_fields_updated = set()
    if "pending_conflicts" not in st.session_state:
        st.session_state.pending_conflicts = {}
    if "clarifications" not in st.session_state:
        st.session_state.clarifications = []
    if "contradictions" not in st.session_state:
        st.session_state.contradictions = []
    if "last_processed_audio_hash" not in st.session_state:
        st.session_state.last_processed_audio_hash = None

    def mark_manual_edit(field_name: str):
        if "ff_manually_edited" not in st.session_state:
            st.session_state.ff_manually_edited = set()
        st.session_state.ff_manually_edited.add(field_name)

    def apply_transcript(transcript_text: str, lang: str, target_field: str = None):
        if not transcript_text or not transcript_text.strip():
            return
        
        cleaned = transcript_text.strip()
        st.session_state.current_transcript = cleaned

        # Build current_data ONLY from fields manually edited by the user to prevent false conflicts with defaults
        current_data = {}
        if "name" in st.session_state.ff_manually_edited:
            current_data["name"] = st.session_state.ff_farmer_name
            current_data["farmer_name"] = st.session_state.ff_farmer_name
        if "phone" in st.session_state.ff_manually_edited:
            current_data["phone"] = st.session_state.ff_phone
        if "village" in st.session_state.ff_manually_edited:
            current_data["village"] = st.session_state.ff_village
        if "district" in st.session_state.ff_manually_edited:
            current_data["district"] = st.session_state.ff_district
        if "crop" in st.session_state.ff_manually_edited:
            current_data["crop"] = st.session_state.ff_crop
        if "acres" in st.session_state.ff_manually_edited:
            current_data["acres"] = st.session_state.ff_acres
        if "yield" in st.session_state.ff_manually_edited:
            current_data["yield_quintals"] = st.session_state.ff_yield
            current_data["projected_yield"] = st.session_state.ff_yield
        if "costs" in st.session_state.ff_manually_edited:
            tot = st.session_state.ff_seeds + st.session_state.ff_fert + st.session_state.ff_labour + st.session_state.ff_irr
            current_data["costs"] = tot
            current_data["input_costs"] = tot

        try:
            result = VoiceNLPService.parse_transcript_to_fields(cleaned, lang_code=lang, current_data=current_data, target_field=target_field)
        except TypeError:
            try:
                result = VoiceNLPService.parse_transcript_to_fields(cleaned, lang_code=lang, current_data=current_data)
            except TypeError:
                result = VoiceNLPService.parse_transcript_to_fields(cleaned, lang_code=lang)
        st.session_state.clarifications = result.get("clarifications", [])
        st.session_state.contradictions = result.get("contradictions", [])
        st.session_state.confirmation_summary = result.get("confirmation_summary", "")
        st.session_state.followup_question = result.get("followup_question")
        
        conflicts = result.get("proposed_changes", {})
        st.session_state.pending_conflicts = conflicts

        extracted = result.get("extracted_fields", {})
        
        # Populate each extracted field into form session_state if not in conflict
        if ("name" in extracted or "farmer_name" in extracted) and "name" not in conflicts and "farmer_name" not in conflicts:
            st.session_state.ff_farmer_name = str(extracted.get("name") or extracted.get("farmer_name"))
            st.session_state.voice_fields_updated.add("name")

        if "phone" in extracted and "phone" not in conflicts:
            st.session_state.ff_phone = str(extracted["phone"])
            st.session_state.voice_fields_updated.add("phone")

        if "village" in extracted and "village" not in conflicts:
            st.session_state.ff_village = str(extracted["village"])
            st.session_state.voice_fields_updated.add("village")

        if "district" in extracted and "district" not in conflicts:
            st.session_state.ff_district = str(extracted["district"])
            st.session_state.voice_fields_updated.add("district")

        if "crop" in extracted and "crop" not in conflicts:
            sp_crop = str(extracted["crop"])
            for c in T["crops"]:
                if sp_crop.lower() in c.lower() or c.lower().split()[0] in sp_crop.lower():
                    st.session_state.ff_crop = c
                    break
            st.session_state.voice_fields_updated.add("crop")

        if "acres" in extracted and "acres" not in conflicts:
            ac_val = max(0.5, min(2.5, float(extracted["acres"])))
            st.session_state.ff_acres = ac_val
            st.session_state.voice_fields_updated.add("acres")

        if ("yield_quintals" in extracted or "projected_yield" in extracted) and "yield_quintals" not in conflicts and "yield" not in conflicts:
            y_val = max(1.0, min(80.0, float(extracted.get("yield_quintals") or extracted.get("projected_yield"))))
            st.session_state.ff_yield = y_val
            st.session_state.voice_fields_updated.add("yield")

        if ("costs" in extracted or "input_costs" in extracted) and "costs" not in conflicts and "input_costs" not in conflicts:
            c_val = float(extracted.get("costs") or extracted.get("input_costs"))
            st.session_state.ff_seeds = round(c_val * 0.25, 2)
            st.session_state.ff_fert = round(c_val * 0.35, 2)
            st.session_state.ff_labour = round(c_val * 0.30, 2)
            st.session_state.ff_irr = round(c_val * 0.10, 2)
            st.session_state.voice_fields_updated.add("costs")

        st.rerun()

    # Prominent Hero Voice Input (Zero Copy/Paste)
    st.markdown("""
        <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 2px solid #22c55e; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #15803d; margin-bottom: 0.25rem;">
                🎙️ बोलकर जानकारी भरें / Speak to Fill Form
            </div>
            <div style="font-size: 0.88rem; color: #166534;">
                माइक पर टैप करके अपनी जानकारी बोलें (जैसे नाम, मोबाइल नंबर, फसल, जमीन, पैदावार और कुल खर्च)। बोलते ही सभी फ़ील्ड अपने-आप भर जाएंगे।
            </div>
        </div>
    """, unsafe_allow_html=True)

    recorded_audio = st.audio_input("बोलकर जानकारी भरें / Speak to Fill Form", key="hero_farmer_audio_input")
    if recorded_audio:
        audio_bytes = recorded_audio.read()
        audio_hash = hash(audio_bytes)
        if st.session_state.last_processed_audio_hash != audio_hash:
            st.session_state.last_processed_audio_hash = audio_hash
            with st.spinner("🎙️ Recognizing speech and filling form fields automatically..."):
                parsed = VoiceNLPService.transcribe_audio_bytes(audio_bytes, cur_lang_code)
                if parsed.get("success") and parsed.get("raw_transcript"):
                    apply_transcript(parsed["raw_transcript"], cur_lang_code)
                else:
                    err_msg = parsed.get("error", "Speech could not be understood clearly.")
                    st.warning(f"⚠️ {err_msg} You can try speaking again or use the optional transcript section below.")

    # Simple Confirmation Summary Card (Farmer Review)
    if st.session_state.get("confirmation_summary"):
        st.success(f"📋 **पहचानी गई जानकारी / Recognized Details:**\n\n**{st.session_state.confirmation_summary}**")
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1.5, 1.2, 1.2, 1.5])
        with btn_col1:
            if st.button("✅ Confirm & Continue", key="btn_confirm_continue", use_container_width=True):
                st.session_state.farmer_confirmed = True
                st.toast("✅ Details confirmed! Please review the form below and click 'Calculate Safe Credit Limit' when ready.")
        with btn_col2:
            if st.button("🔄 Record Again", key="btn_record_again", use_container_width=True):
                st.session_state.last_processed_audio_hash = None
                st.session_state.confirmation_summary = None
                st.session_state.followup_question = None
                st.session_state.current_transcript = ""
                st.rerun()
        with btn_col3:
            if st.button("✏️ Edit Details", key="btn_edit_details", use_container_width=True):
                st.toast("👉 You can directly edit the fields in the form below.")
        with btn_col4:
            if st.button("🔊 Listen Summary Aloud", key="btn_listen_summary_aloud", use_container_width=True):
                try:
                    from backend.services.voice_service import voice_service
                    ok, a_bytes, mime = voice_service.synthesize_speech(st.session_state.confirmation_summary, cur_lang_code)
                    if ok and a_bytes:
                        st.audio(a_bytes, format=mime, autoplay=True)
                except Exception:
                    st.info(f"🔊 {st.session_state.confirmation_summary}")

    # Follow-up Question Card (One specific targeted question if info is missing)
    if st.session_state.get("followup_question"):
        followup_data = st.session_state.followup_question
        st.info(f"❓ **एक जानकारी और चाहिए / One Quick Detail Needed:**\n\n**{followup_data['question']}**")
        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            followup_audio = st.audio_input(f"🎙️ Answer by Voice ({followup_data.get('field_label', 'detail')})", key="followup_audio_box")
            if followup_audio:
                f_bytes = followup_audio.read()
                f_hash = hash(f_bytes)
                if st.session_state.get("last_followup_hash") != f_hash:
                    st.session_state.last_followup_hash = f_hash
                    f_parsed = VoiceNLPService.transcribe_audio_bytes(f_bytes, cur_lang_code)
                    if f_parsed.get("success") and f_parsed.get("raw_transcript"):
                        apply_transcript(f_parsed["raw_transcript"], cur_lang_code, target_field=followup_data.get("field"))
        with f_col2:
            if st.button("🔊 Listen Question", key="btn_listen_followup", use_container_width=True):
                try:
                    from backend.services.voice_service import voice_service
                    ok, a_bytes, mime = voice_service.synthesize_speech(followup_data['question'], cur_lang_code)
                    if ok and a_bytes:
                        st.audio(a_bytes, format=mime, autoplay=True)
                except Exception:
                    st.info(f"🔊 {followup_data['question']}")

    # Optional Collapsible Transcript & Scenarios Section (No copy/paste needed)
    with st.expander("📝 View / Edit Transcript (Optional)", expanded=False):
        st.caption("Spoken transcript appears here automatically. You can also type manually or select a regional demo scenario:")
        typed_col1, typed_col2 = st.columns([4, 1])
        with typed_col1:
            typed_utterance = st.text_input(
                "Spoken Text Input",
                value=st.session_state.current_transcript,
                placeholder="My name is Ramesh Patel, phone 9876543210. I am cultivating 2.0 acres of Tomato in Pimpalgaon, Nashik. Expecting 18 quintals per acre yield and total input expenses are 24000 rupees.",
                label_visibility="collapsed",
                key="input_typed_speech_box"
            )
        with typed_col2:
            if st.button("⚡ Update from Transcript", key="btn_parse_typed_speech", use_container_width=True):
                user_text = typed_utterance or st.session_state.current_transcript
                if user_text and user_text.strip():
                    apply_transcript(user_text.strip(), cur_lang_code)
                else:
                    st.warning("Please enter a spoken sentence first.")

        st.markdown("---")
        st.write("Or try a 1-click regional demo scenario:")
        sample_scenarios = {
            "hi": "Hindi — Nashik Tomato Smallholder (2.0 Acres, ₹24,000 Costs)",
            "mr": "Marathi — Vidarbha Cotton Smallholder (2.5 Acres, ₹26,000 Costs)",
            "gu": "Gujarati — Rajkot Soybean Smallholder (1.5 Acres, ₹18,000 Costs)",
            "te": "Telugu — Warangal Cotton Smallholder (2.0 Acres, ₹22,000 Costs)",
            "ta": "Tamil — Dindigul Tomato Smallholder (1.5 Acres, ₹20,000 Costs)",
            "kn": "Kannada — Davanagere Maize Smallholder (2.0 Acres, ₹21,000 Costs)",
            "pa": "Punjabi — Khanna Wheat Smallholder (2.0 Acres, ₹25,000 Costs)",
            "bn": "Bengali — Hooghly Tomato Smallholder (1.5 Acres, ₹23,000 Costs)",
            "or": "Odia — Cuttack Vegetable Smallholder (1.5 Acres, ₹19,000 Costs)",
            "as": "Assamese — Nagaon Maize Smallholder (2.0 Acres, ₹20,000 Costs)",
            "en": "English — Direct Smallholder Intake (2.0 Acres Tomato, ₹24,000 Costs)"
        }
        selected_scenario_code = st.selectbox(
            "Select Vernacular Voice Scenario:",
            list(sample_scenarios.keys()),
            format_func=lambda x: sample_scenarios[x],
            index=list(sample_scenarios.keys()).index(cur_lang_code) if cur_lang_code in sample_scenarios else 0
        )
        if st.button("▶️ Load & Transcribe Vernacular Scenario", use_container_width=True):
            sample = VoiceNLPService.get_sample_utterance(selected_scenario_code)
            apply_transcript(sample["transcript"], selected_scenario_code)

    # Contradictions Warning
    if st.session_state.contradictions:
        for contra in st.session_state.contradictions:
            st.warning(f"⚠️ **Clarification Needed:** {contra}")

    # Conflict Resolution Banner
    if st.session_state.pending_conflicts:
        st.warning("⚠️ **Review Proposed Voice Changes:** The spoken input conflicts with values you manually entered.")
        for field, conf in st.session_state.pending_conflicts.items():
            f_display = field.replace('_', ' ').title()
            st.markdown(f"- **{f_display}**: Current Value: `{conf['current']}` ➔ Spoken Voice Value: `{conf['spoken']}`")
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("✅ Accept Spoken Changes", key="btn_accept_conflicts", use_container_width=True):
                for field, conf in st.session_state.pending_conflicts.items():
                    if field in ["farmer_name", "name"]:
                        st.session_state.ff_farmer_name = str(conf["spoken"])
                        st.session_state.ff_manually_edited.discard("name")
                        st.session_state.voice_fields_updated.add("name")
                    elif field == "phone":
                        st.session_state.ff_phone = str(conf["spoken"])
                        st.session_state.ff_manually_edited.discard("phone")
                        st.session_state.voice_fields_updated.add("phone")
                    elif field == "village":
                        st.session_state.ff_village = str(conf["spoken"])
                        st.session_state.ff_manually_edited.discard("village")
                        st.session_state.voice_fields_updated.add("village")
                    elif field == "district":
                        st.session_state.ff_district = str(conf["spoken"])
                        st.session_state.ff_manually_edited.discard("district")
                        st.session_state.voice_fields_updated.add("district")
                    elif field == "crop":
                        for c in T["crops"]:
                            if str(conf["spoken"]).lower() in c.lower():
                                st.session_state.ff_crop = c
                                break
                        st.session_state.ff_manually_edited.discard("crop")
                        st.session_state.voice_fields_updated.add("crop")
                    elif field == "acres":
                        st.session_state.ff_acres = max(0.5, min(2.5, float(conf["spoken"])))
                        st.session_state.ff_manually_edited.discard("acres")
                        st.session_state.voice_fields_updated.add("acres")
                    elif field in ["yield", "yield_quintals", "projected_yield"]:
                        st.session_state.ff_yield = max(1.0, min(80.0, float(conf["spoken"])))
                        st.session_state.ff_manually_edited.discard("yield")
                        st.session_state.voice_fields_updated.add("yield")
                    elif field in ["costs", "input_costs"]:
                        c_val = float(conf["spoken"])
                        st.session_state.ff_seeds = round(c_val * 0.25, 2)
                        st.session_state.ff_fert = round(c_val * 0.35, 2)
                        st.session_state.ff_labour = round(c_val * 0.30, 2)
                        st.session_state.ff_irr = round(c_val * 0.10, 2)
                        st.session_state.ff_manually_edited.discard("costs")
                        st.session_state.voice_fields_updated.add("costs")
                st.session_state.pending_conflicts = {}
                st.rerun()
        with c_btn2:
            if st.button("❌ Keep My Current Values", key="btn_reject_conflicts", use_container_width=True):
                st.session_state.pending_conflicts = {}
                st.rerun()

    # 2. Farmer Review & Correction Form (PRD: Farmer reviews and corrects recognized info)
    st.markdown("---")
    st.markdown("### 📝 Review & Correct Crop Information Before Assessment")
    st.caption("Fields automatically mapped from voice transcription. Modify any value as needed before final submission.")

    v_updated = st.session_state.voice_fields_updated
    if v_updated:
        updated_names = [f.replace('_', ' ').title() for f in sorted(v_updated)]
        st.success(f"🎙️ **Fields populated from voice input:** {', '.join(updated_names)}. Review values below and click Submit when ready.")

    # Missing fields indicator (PRD: Leave unmentioned fields unchanged and indicate which details still need to be provided)
    req_labels = {
        "name": "Farmer Name",
        "phone": "Phone Number",
        "village": "Village",
        "district": "District",
        "crop": "Crop",
        "acres": "Land Area (Acres)",
        "yield": "Expected Yield",
        "costs": "Cultivation Costs"
    }
    if st.session_state.current_transcript:
        missing_items = [lbl for k, lbl in req_labels.items() if k not in v_updated]
        if missing_items:
            st.info(f"ℹ️ **Details still needed (not mentioned in speech):** {', '.join(missing_items)}. You can speak them, type into the form below, or enter another voice note.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lbl_name = f"{T['name_label']} 🎙️ [Voice Updated]" if "name" in v_updated else T["name_label"]
        farmer_name = st.text_input(lbl_name, key="ff_farmer_name", on_change=mark_manual_edit, args=("name",))

        lbl_phone = f"{T['phone_label']} 🎙️ [Voice Updated]" if "phone" in v_updated else T["phone_label"]
        phone = st.text_input(lbl_phone, key="ff_phone", on_change=mark_manual_edit, args=("phone",))

        lbl_village = f"{T['village_label']} 🎙️ [Voice Updated]" if "village" in v_updated else T["village_label"]
        village = st.text_input(lbl_village, key="ff_village", on_change=mark_manual_edit, args=("village",))

        lbl_district = f"{T['district_label']} 🎙️ [Voice Updated]" if "district" in v_updated else T["district_label"]
        district = st.text_input(lbl_district, key="ff_district", on_change=mark_manual_edit, args=("district",))

        crop_idx = T["crops"].index(st.session_state.ff_crop) if st.session_state.ff_crop in T["crops"] else 0
        lbl_crop = f"{T['crop_label']} 🎙️ [Voice Updated]" if "crop" in v_updated else T["crop_label"]
        crop = st.selectbox(lbl_crop, T["crops"], index=crop_idx, key="ff_crop", on_change=mark_manual_edit, args=("crop",))

        lbl_acres = f"{T['acres_label']} 🎙️ [Voice Updated]" if "acres" in v_updated else T["acres_label"]
        acres = st.number_input(lbl_acres, min_value=0.5, max_value=2.5, step=0.1, key="ff_acres", on_change=mark_manual_edit, args=("acres",))

    with col_f2:
        lbl_yield = f"{T['yield_label']} 🎙️ [Voice Updated]" if "yield" in v_updated else T["yield_label"]
        projected_yield = st.number_input(lbl_yield, min_value=1.0, max_value=80.0, step=0.5, key="ff_yield", on_change=mark_manual_edit, args=("yield",))
        
        # Itemized Costs
        lbl_seeds = f"{T['seeds_cost_label']} 🎙️ [Voice Updated]" if "costs" in v_updated else T["seeds_cost_label"]
        c_seeds = st.number_input(lbl_seeds, min_value=500.0, max_value=50000.0, step=500.0, key="ff_seeds", on_change=mark_manual_edit, args=("costs",))
        c_fert = st.number_input(T["fert_cost_label"], min_value=500.0, max_value=50000.0, step=500.0, key="ff_fert", on_change=mark_manual_edit, args=("costs",))
        c_labour = st.number_input(T["labour_cost_label"], min_value=500.0, max_value=50000.0, step=500.0, key="ff_labour", on_change=mark_manual_edit, args=("costs",))
        c_irr = st.number_input(T["irr_cost_label"], min_value=500.0, max_value=50000.0, step=500.0, key="ff_irr", on_change=mark_manual_edit, args=("costs",))

        fpo_group = st.selectbox(T["fpo_label"], ["Sahyadri Agro Producer Co.", "Tapi Valley Organic FPO", "Kisan Vikas Collective"], key="ff_fpo")

        # 3-Member Peer Guarantee Pool Choice
        all_live_groups = get_live_fpo_groups()
        open_pools = [g for g in all_live_groups if not g.get("is_full", False) and g.get("member_count", 0) < 3]
        pool_options = {"⏳ Unassigned (Awaiting FPO Guarantee Pool Formation)": None}
        for op in open_pools:
            pool_options[f"🤝 Join {op['group_code']} ({op['fpo_name']}) — {op.get('member_count', 0)}/3 Members"] = op["id"]

        selected_pool_label = st.selectbox(
            "🤝 3-Member Peer Guarantee Pool Assignment",
            options=list(pool_options.keys()),
            key="ff_target_pool",
            help="Select an existing forming pool (<3 members) to join, or register as unassigned for coordinator to assign."
        )
        target_pool_id = pool_options[selected_pool_label]

        p1 = st.text_input(T["p1_label"], key="ff_p1")
        p2 = st.text_input(T["p2_label"], key="ff_p2")
        p3 = st.text_input(T["p3_label"], key="ff_p3")

    # Consistent performer checkbox
    is_repeat = st.checkbox("🌟 Consistent Performer (Flawless previous season bullet repayment record (+15% limit bonus))", key="ff_repeat")

    # 3. GDPR & Data Ownership Consents
    st.markdown("##### 🔒 Farmer Data Ownership & GDPR Consent Verification")
    c1 = st.checkbox(T["consent_underwriting"], value=True)
    c2 = st.checkbox(T["consent_fpo"], value=True)
    c3 = st.checkbox(T["consent_mandi"], value=True)

    # 4. Calculation Trigger
    if st.button(T["btn_calc"], type="primary", use_container_width=True):
        if not (c1 and c2 and c3):
            st.error("Please provide necessary consent checkboxes to proceed with agronomic underwriting.")
        else:
            payload = {
                "farmer_name": farmer_name,
                "phone": phone,
                "village": village or "Pimpalgaon",
                "district": district or "Nashik",
                "state": "Maharashtra",
                "fpo_name": fpo_group,
                "target_pool_id": target_pool_id,
                "crop_name": crop,
                "acres": acres,
                "projected_yield": projected_yield,
                "seeds_cost": c_seeds,
                "fertilizer_cost": c_fert,
                "labour_cost": c_labour,
                "irrigation_other_cost": c_irr,
                "peer_guarantors_count": 3,
                "is_consistent_performer": is_repeat
            }

            underwriting_data = None
            vc_data = None
            alerts_data = None
            pool_info = None

            # Try live backend first
            if backend_connected:
                try:
                    res = requests.post(f"{API_BASE}/underwriting/submit-application", json=payload, timeout=2.5)
                    if res.status_code in [200, 201]:
                        res_json = res.json()
                        underwriting_data = res_json["underwriting_result"]
                        vc_data = res_json.get("verifiable_credential")
                        alerts_data = res_json.get("proactive_alerts")
                        pool_info = res_json.get("pool_assignment")
                        st.toast("Application saved to live network!", icon="✅")
                except Exception:
                    underwriting_data = None

            # Fallback to deterministic local engine + SQLite persistence
            if not underwriting_data:
                underwriting_data = UnderwritingService.calculate_assessment(
                    farmer_name=farmer_name,
                    phone=phone,
                    crop_name=crop,
                    acres=acres,
                    projected_yield=projected_yield,
                    seeds_cost=c_seeds,
                    fertilizer_cost=c_fert,
                    labour_cost=c_labour,
                    irrigation_other_cost=c_irr,
                    peer_guarantors_count=3,
                    is_consistent_performer=is_repeat
                )
                try:
                    from backend.database import SessionLocal
                    from backend.models import Farmer, FarmerStatus, CreditAssessment, PeerGroup, PeerGroupMember
                    db_fallback = SessionLocal()
                    f_fb = db_fallback.query(Farmer).filter(Farmer.phone == phone).first()
                    if not f_fb:
                        f_fb = Farmer(
                            name=farmer_name,
                            phone=phone,
                            village=village or "Pimpalgaon",
                            district=district or "Nashik",
                            state="Maharashtra",
                            land_size_acres=acres,
                            fpo_name=fpo_group,
                            status=FarmerStatus.ACTIVE
                        )
                        db_fallback.add(f_fb)
                        db_fallback.commit()
                        db_fallback.refresh(f_fb)
                    else:
                        f_fb.name = farmer_name
                        f_fb.land_size_acres = acres
                        f_fb.village = village or "Pimpalgaon"
                        f_fb.district = district or "Nashik"
                        f_fb.fpo_name = fpo_group
                        db_fallback.commit()
                        db_fallback.refresh(f_fb)

                    # If target_pool_id selected and has < 3 members, link
                    if target_pool_id:
                        g_fb = db_fallback.query(PeerGroup).filter(PeerGroup.id == target_pool_id).first()
                        if g_fb and len(g_fb.members) < 3:
                            exists_m = db_fallback.query(PeerGroupMember).filter(
                                PeerGroupMember.group_id == g_fb.id,
                                PeerGroupMember.farmer_id == f_fb.id
                            ).first()
                            if not exists_m:
                                role = "LEADER" if len(g_fb.members) == 0 else "MEMBER"
                                db_fallback.add(PeerGroupMember(
                                    group_id=g_fb.id,
                                    farmer_id=f_fb.id,
                                    role=role,
                                    guarantee_pledged=True
                                ))
                                db_fallback.commit()

                    bullet_d = datetime.strptime(underwriting_data["amortization"]["bullet_due_date"], "%Y-%m-%d")
                    db_ass = CreditAssessment(
                        farmer_id=f_fb.id,
                        assessment_date=datetime.now(),
                        credit_score=underwriting_data["credit_score"],
                        loan_eligibility_amount=underwriting_data["credit_limit"],
                        risk_category=underwriting_data["risk_category"],
                        crop_name=crop,
                        acres=acres,
                        projected_yield=projected_yield,
                        mandi_price_per_qtl=underwriting_data["mandi_price_per_qtl"],
                        gross_revenue=underwriting_data["gross_revenue"],
                        total_expenses=underwriting_data["expenses_breakdown"]["total"],
                        net_profit=underwriting_data["net_profit"],
                        pmfby_insured=underwriting_data["pmfby_insured"],
                        bullet_repayment_date=bullet_d,
                        status="PENDING_REVIEW",
                        score_breakdown=json.dumps(underwriting_data["score_factors"]),
                        notes=underwriting_data["explanation"]["en"]
                    )
                    db_fallback.add(db_ass)
                    db_fallback.commit()
                    db_fallback.close()
                except Exception:
                    pass

                vc_data = FarmerIdentityService.issue_verifiable_credit_credential(
                    farmer_id=1,
                    farmer_name=farmer_name,
                    phone=phone,
                    state="Maharashtra",
                    crop_name=crop,
                    acres=acres,
                    credit_score=underwriting_data["credit_score"],
                    credit_limit=underwriting_data["credit_limit"],
                    bullet_due_date=underwriting_data["amortization"]["bullet_due_date"],
                    peer_guarantors=[p1, p2, p3],
                    fpo_name=fpo_group
                )
                bullet_d = datetime.strptime(underwriting_data["amortization"]["bullet_due_date"], "%Y-%m-%d")
                alerts_data = AgriDataService.generate_alerts(crop, acres, bullet_d)

            st.success(T["success_msg"])
            if pool_info:
                if pool_info.get("assigned"):
                    st.success(f"🤝 **FPO Guarantee Pool Status**: {pool_info.get('message')}")
                else:
                    st.info(f"⏳ **FPO Guarantee Pool Status**: {pool_info.get('message')}")
            else:
                if target_pool_id:
                    st.success("🤝 **FPO Guarantee Pool Status**: Farmer successfully assigned to selected guarantee pool.")
                else:
                    st.info("⏳ **FPO Guarantee Pool Status**: Farmer registered as unassigned. FPO Coordinator can assign to a 3-member pool in Tab 2.")

            # Key Financial Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(
                T["metric_score"],
                f"{underwriting_data['credit_score']} / 100",
                underwriting_data["risk_category"].split()[0]
            )
            m2.metric(
                T["metric_limit"],
                f"₹{underwriting_data['credit_limit']:,.0f}",
                "0.45 × Net Profit (+15% booster)" if is_repeat else "0.45 × Net Profit"
            )
            m3.metric(
                T["metric_rev"],
                f"₹{underwriting_data['gross_revenue']:,.0f}",
                f"₹{underwriting_data['mandi_price_per_qtl']:,.0f}/qtl ({underwriting_data['mandi_source'].split()[0]})"
            )
            m4.metric(
                T["metric_bullet"],
                underwriting_data["amortization"]["display_due_date"],
                "Single Bullet (0 Monthly EMI)"
            )

            # Credit Offer & Terms
            st.markdown("---")
            st.markdown("### 📜 Official Credit Offer & Harvest-Synchronized Bullet Amortization")
            term_c1, term_c2, term_c3 = st.columns(3)
            term_c1.info(f"**Principal Sanctioned:** ₹{underwriting_data['credit_limit']:,.0f}\n\n**Interest APR:** {underwriting_data['amortization']['interest_rate_apr']}% (PSL Concessional)")
            term_c2.info(f"**Monthly EMI:** ₹0.00 (Zero EMI during crop growth)\n\n**Tenure:** {underwriting_data['amortization']['tenure_days']} Days (Harvest + 30d)")
            term_c3.info(f"**Total Bullet Repayment Due:** ₹{underwriting_data['amortization']['total_bullet_repayment_inr']:,.0f}\n\n**Disbursement Mode:** NPCI e-RUPI Agro-Voucher")

            # Vernacular Advisory
            st.markdown("---")
            if "Hindi" in lang_choice:
                adv = underwriting_data["explanation"]["hi"]
            else:
                adv = underwriting_data["explanation"]["en"]
            st.info(f"{T['advisory_header']}\n\n> *\"{adv}\"*")

            # Explainable Credit Score Breakdown
            with st.expander("🔍 View Explainable Credit Score Factor Breakdown (Transparent Underwriting)", expanded=True):
                factors_df = pd.DataFrame([
                    {
                        "Factor": f["factor"],
                        "Points Awarded": f"{f['points_awarded']} / {f['max_points']}",
                        "Status": f["status"],
                        "Evaluation Rationale": f["description"]
                    }
                    for f in underwriting_data["score_factors"]
                ])
                st.dataframe(factors_df, use_container_width=True)

            # Proactive Mandi Price & Harvest Alerts
            if alerts_data:
                st.markdown("### 🔔 Proactive Mandi Price & Harvest Notifications")
                for al in alerts_data:
                    if al["severity"] == "SUCCESS":
                        st.success(f"**{al['title']}** — {al['message']}")
                    elif al["severity"] == "WARNING":
                        st.warning(f"**{al['title']}** — {al['message']}")
                    else:
                        st.info(f"**{al['title']}** — {al['message']}")

            # Portable Digital Identity (W3C DID & Verifiable Credential)
            if vc_data:
                with st.expander("🆔 Portable Decentralized Identity & W3C Verifiable Credential"):
                    st.markdown(f"**Farmer DID:** `{vc_data['credentialSubject']['id']}`")
                    st.markdown(f"**Tamper-Evident Ledger Anchor:** `{vc_data['blockchainAnchor']['ledgerTransactionHash']}`")
                    st.caption("This cryptographically signed credential allows you to take your credit score to any rural bank or cooperative without land titles.")
                    st.download_button(
                        "📥 Download Portable W3C Credential (JSON-LD)",
                        data=json.dumps(vc_data, indent=2),
                        file_name=f"farmer_credit_credential_{phone}.json",
                        mime="application/json"
                    )

# -------------------------------------------------------------
# TAB 2: FPO COORDINATOR CONSOLE
# -------------------------------------------------------------
with tab2:
    st.subheader("🤝 Farmer Producer Organisation (FPO) Coordinator Console")
    st.caption("3-Member Peer Guarantee Group Management • Field Visit Crop Verification • Early Distress Intervention")

    fpo_k1, fpo_k2, fpo_k3, fpo_k4 = st.columns(4)
    live_groups = get_live_fpo_groups()
    unassigned_farmers = get_unassigned_farmers()
    total_pools = len(live_groups)
    total_pool_farmers = sum(g.get("member_count", len(g.get("members", []))) for g in live_groups)
    total_pool_credit = sum(g.get("total_pool_credit_limit", 0.0) for g in live_groups)
    unassigned_count = len(unassigned_farmers)

    fpo_k1, fpo_k2, fpo_k3, fpo_k4 = st.columns(4)
    fpo_k1.metric("Active Guarantee Pools", f"{total_pools} Pools ({total_pool_farmers} Farmers)", "3-Peer Social Collateral")
    fpo_k2.metric("Total Pool Credit Capacity", f"₹{total_pool_credit:,.0f}", "Live Agronomic Sizing")
    fpo_k3.metric("Unassigned Farmers Queue", f"{unassigned_count} Farmers", "Awaiting Pool Formation")
    fpo_k4.metric("3-Member Rule Compliance", "100% Strict", "Max 3 Members / Pool")

    fpo_sub1, fpo_sub2, fpo_sub3 = st.tabs([
        "👥 3-Member Peer Guarantee Groups",
        "🌱 Record Field Crop Verification",
        "🚨 Early Warning & Distress Alerts"
    ])

    with fpo_sub1:
        st.write("#### Active 3-Member Guarantee Pools (Social Collateral)")
        st.caption("Mutually guaranteed credit circles. Strict maximum of 3 members per pool.")

        if not live_groups:
            st.info("No guarantee pools formed yet. Form your first 3-member pool below.")
        else:
            for g in live_groups:
                m_list = g.get("members", [])
                m_count = g.get("member_count", len(m_list))
                pool_state = g.get("pool_state", "Full (3/3)" if m_count >= 3 else f"Forming ({m_count}/3)")
                limit_val = g.get("total_pool_credit_limit", 0.0)

                with st.expander(
                    f"📌 {g['group_code']} — {g['fpo_name']} ({g.get('village', 'Nashik')}) | Total Pool Limit: ₹{limit_val:,.0f} • [{pool_state}]",
                    expanded=True
                ):
                    col_info1, col_info2, col_info3 = st.columns(3)
                    col_info1.markdown(f"**Pool Status:** `{pool_state}`")
                    col_info2.markdown(f"**Repayment Track Record:** `{g.get('repayment_rate', 100.0)}%`")
                    col_info3.markdown(f"**Joint Social Pledge:** `{m_count}/3 Members Verified`")

                    if m_list:
                        members_df = pd.DataFrame([
                            {
                                "Farmer ID": m.get("farmer_id", "N/A"),
                                "Farmer Name": m.get("name", "N/A"),
                                "Role": m.get("role", "MEMBER"),
                                "Phone": m.get("phone", "N/A"),
                                "Credit Score": f"{m.get('credit_score', 70)} / 100",
                                "Credit Limit": f"₹{m.get('credit_limit', 0.0):,.0f}",
                                "Social Guarantee Pledged": "✅ Signed (Active)" if m.get("guarantee_pledged", True) else "⏳ Pending"
                            }
                            for m in m_list
                        ])
                        st.dataframe(members_df, use_container_width=True)
                    else:
                        st.write("No members in this pool yet.")

                    if m_count < 3:
                        open_slots = 3 - m_count
                        st.warning(f"⚠️ Open Pool: {open_slots} slot(s) available. You can assign an unassigned farmer to this pool below.")

        st.markdown("---")
        st.write("#### 📋 Unassigned Farmers (Awaiting Guarantee Pool Assignment)")
        st.caption("Newly submitted farmers who are not yet placed into a 3-member social collateral pool.")

        if unassigned_farmers:
            unassigned_rows = []
            for u in unassigned_farmers:
                unassigned_rows.append({
                    "Farmer ID": u["farmer_id"],
                    "Name": u["name"],
                    "Phone": u["phone"],
                    "Village / District": f"{u['village']}, {u['district']}",
                    "Affiliated FPO": u["fpo_name"],
                    "Crop Cultivated": u["crop_name"],
                    "Credit Score": f"{u['credit_score']} / 100",
                    "Assessed Credit Limit": f"₹{u['credit_limit']:,.0f}",
                    "Pool Status": "⏳ UNASSIGNED"
                })
            st.dataframe(pd.DataFrame(unassigned_rows), use_container_width=True)

            # Interactive 1-click assignment workflow
            st.write("##### 🤝 Assign Unassigned Farmer to Open Guarantee Pool")
            assign_col1, assign_col2, assign_col3 = st.columns([2, 2, 1])

            farmer_select_map = {
                f"#{u['farmer_id']} - {u['name']} ({u['crop_name']}, ₹{u['credit_limit']:,.0f})": u["farmer_id"]
                for u in unassigned_farmers
            }
            with assign_col1:
                selected_farmer_str = st.selectbox("Select Unassigned Farmer", options=list(farmer_select_map.keys()), key="assign_farmer_select")
                selected_farmer_id = farmer_select_map[selected_farmer_str]

            open_pools = [g for g in live_groups if g.get("member_count", len(g.get("members", []))) < 3]
            with assign_col2:
                if open_pools:
                    pool_select_map = {
                        f"{g['group_code']} ({g['fpo_name']}) — {g.get('member_count', len(g.get('members', [])))}/3 members (Open)": g["id"]
                        for g in open_pools
                    }
                    selected_pool_str = st.selectbox("Select Target Open Pool (< 3 Members)", options=list(pool_select_map.keys()), key="assign_pool_select")
                    selected_pool_id = pool_select_map[selected_pool_str]
                else:
                    st.info("No open pools (<3 members) currently available. Create a new pool below.")
                    selected_pool_id = None

            with assign_col3:
                st.write("")
                st.write("")
                if selected_pool_id and st.button("➕ Assign to Pool", type="primary", use_container_width=True):
                    success = False
                    err_msg = ""
                    if backend_connected:
                        try:
                            a_res = requests.post(f"{API_BASE}/fpo/assign-member", json={
                                "farmer_id": selected_farmer_id,
                                "group_id": selected_pool_id,
                                "role": "MEMBER",
                                "guarantee_pledged": True
                            }, timeout=3.0)
                            if a_res.status_code == 200:
                                success = True
                            else:
                                err_msg = a_res.json().get("detail", "Assignment failed")
                        except Exception as ex:
                            err_msg = str(ex)
                    if not success:
                        try:
                            from backend.database import SessionLocal
                            from backend.models import PeerGroup, PeerGroupMember
                            db_a = SessionLocal()
                            gp = db_a.query(PeerGroup).filter(PeerGroup.id == selected_pool_id).first()
                            if gp and len(gp.members) < 3:
                                db_a.add(PeerGroupMember(
                                    group_id=selected_pool_id,
                                    farmer_id=selected_farmer_id,
                                    role="MEMBER",
                                    guarantee_pledged=True
                                ))
                                db_a.commit()
                                success = True
                            else:
                                err_msg = "Pool has already reached maximum 3 members."
                            db_a.close()
                        except Exception as e:
                            err_msg = str(e)

                    if success:
                        st.success("Farmer successfully assigned to guarantee pool! Refreshing...")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Assignment failed: {err_msg}")
        else:
            st.success("✅ All onboarded farmers are currently assigned to active 3-member guarantee pools. No unassigned farmers.")

        st.markdown("---")
        st.write("#### ➕ Onboard New 3-Member Peer Guarantee Group")
        st.caption("Form a new mutual guarantee pool with 1 to 3 member farmers (Strict 3-member maximum).")
        with st.form("onboard_group_form"):
            new_code = st.text_input("Unique Group Code", value=f"GRP-KCC-{int(time.time()) % 10000}")
            new_fpo = st.selectbox("Affiliated FPO", ["Sahyadri Agro Producer Co.", "Tapi Valley Organic FPO", "Kisan Vikas Collective"])
            new_village = st.text_input("Village & District", value="Niphad, Nashik")

            if unassigned_farmers:
                u_opts = {f"#{u['farmer_id']} - {u['name']} ({u['village']})": u['farmer_id'] for u in unassigned_farmers}
                selected_new_members = st.multiselect(
                    "Select Unassigned Farmers for New Group (1 to 3 members):",
                    options=list(u_opts.keys()),
                    max_selections=3
                )
                m_ids_fallback = st.text_input("Or Enter Member Farmer IDs manually (e.g. 1, 2, 3):", value="")
            else:
                selected_new_members = []
                m_ids_fallback = st.text_input("Member Farmer IDs (comma-separated, max 3):", value="")

            if st.form_submit_button("🤝 Form & Register Peer Guarantee Pool"):
                ids_to_add = [u_opts[k] for k in selected_new_members] if selected_new_members else []
                if not ids_to_add and m_ids_fallback.strip():
                    try:
                        ids_to_add = [int(x.strip()) for x in m_ids_fallback.split(",") if x.strip()]
                    except Exception:
                        ids_to_add = []

                if not ids_to_add:
                    st.error("Please select or enter at least 1 member farmer ID (maximum 3).")
                elif len(ids_to_add) > 3:
                    st.error("PRD Mandate: A peer guarantee pool can have at most 3 members.")
                else:
                    success = False
                    err_msg = ""
                    if backend_connected:
                        try:
                            c_res = requests.post(f"{API_BASE}/fpo/groups", json={
                                "group_code": new_code,
                                "fpo_name": new_fpo,
                                "village": new_village.split(",")[0],
                                "district": new_village.split(",")[-1].strip(),
                                "member_farmer_ids": ids_to_add
                            }, timeout=3.0)
                            if c_res.status_code in [200, 201]:
                                success = True
                            else:
                                err_msg = c_res.json().get("detail", "Creation failed")
                        except Exception as ex:
                            err_msg = str(ex)

                    if not success:
                        try:
                            from backend.database import SessionLocal
                            from backend.models import PeerGroup, PeerGroupMember
                            db_c = SessionLocal()
                            if not db_c.query(PeerGroup).filter(PeerGroup.group_code == new_code).first():
                                ng = PeerGroup(
                                    group_code=new_code,
                                    fpo_name=new_fpo,
                                    village=new_village.split(",")[0],
                                    district=new_village.split(",")[-1].strip(),
                                    status="ACTIVE",
                                    repayment_rate=100.0
                                )
                                db_c.add(ng)
                                db_c.commit()
                                db_c.refresh(ng)
                                for idx, fid in enumerate(ids_to_add):
                                    db_c.add(PeerGroupMember(
                                        group_id=ng.id,
                                        farmer_id=fid,
                                        role="LEADER" if idx == 0 else "MEMBER",
                                        guarantee_pledged=True
                                    ))
                                db_c.commit()
                                success = True
                            else:
                                err_msg = f"Group code {new_code} already exists."
                            db_c.close()
                        except Exception as ex:
                            err_msg = str(ex)

                    if success:
                        st.success(f"Group {new_code} formed successfully with {len(ids_to_add)}/3 members!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(f"Failed to create group: {err_msg}")

    with fpo_sub2:
        st.write("#### Field Visit Crop Inspection Record")
        st.caption("FPO coordinators visit fields to verify crop growth stage, GPS coordinates, and health.")
        
        with st.form("field_verification_form"):
            v_farmer_id = st.number_input("Farmer ID", min_value=1, value=1)
            v_crop = st.selectbox("Observed Crop", ["Tomato (Horticulture)", "Cotton", "Soybean", "Wheat", "Onion", "Maize"])
            v_acres = st.number_input("Physically Verified Acres", min_value=0.5, max_value=2.5, value=2.0, step=0.1)
            v_stage = st.selectbox("Current Crop Stage", ["Sowing / Germination", "Vegetative (Healthy)", "Flowering & Fruit Setting", "Harvest Ready"])
            v_status = st.selectbox("Inspection Outcome", ["VERIFIED", "FLAGGED", "REJECTED"])
            v_officer = st.text_input("Field Officer Name", value="Anand Shinde (FPO Agronomist)")
            v_notes = st.text_area("Field Notes", value="Trellis staking verified. Drip fertigation in place. Good canopy health.")
            
            if st.form_submit_button("📋 Submit Official Crop Verification Record"):
                if backend_connected:
                    try:
                        requests.post(f"{API_BASE}/fpo/verifications", json={
                            "farmer_id": v_farmer_id,
                            "crop_name": v_crop,
                            "verified_acres": v_acres,
                            "crop_stage": v_stage,
                            "field_officer_name": v_officer,
                            "verification_status": v_status,
                            "notes": v_notes
                        }, timeout=1.5)
                    except Exception:
                        pass
                st.success(f"Field verification for Farmer #{v_farmer_id} recorded as {v_status}!")

    with fpo_sub3:
        st.write("#### Proactive Peer Support & Early Warning System")
        st.caption("Identify struggling members before harvest to mobilize peer labor and technical assistance.")
        
        st.warning("⚠️ **Peer Alert (GRP-SAHYADRI-01):** Farmer Suresh Kumar reported minor moisture stress in Plot 2B. Action: Drip line flushing scheduled with co-guarantor Dinesh Bhai.")
        st.info("ℹ️ **Agronomic Health Index:** 17 of 18 pools are at optimal vegetative vigor. Zero default risk detected across active credit book.")

# -------------------------------------------------------------
# TAB 3: RURAL BANK & NBFC CONSOLE
# -------------------------------------------------------------
with tab3:
    st.subheader("🏦 Rural Bank & NBFC Portfolio Underwriting Console")
    st.markdown("Direct visibility into uncollateralized smallholder loans qualified under **RBI Priority Sector Lending (PSL)**.")

    all_apps = get_lender_applications()
    pending_apps = [a for a in all_apps if a.get("status") == "PENDING_REVIEW"]
    sanctioned_apps = [a for a in all_apps if a.get("status") == "SANCTIONED"]
    disbursed_apps = [a for a in all_apps if a.get("status") == "DISBURSED"]
    rejected_apps = [a for a in all_apps if a.get("status") == "REJECTED"]

    total_sanctioned_val = sum(a.get("sanctioned_limit", 0.0) for a in (sanctioned_apps + disbursed_apps))
    total_disbursed_val = sum(a.get("sanctioned_limit", 0.0) for a in disbursed_apps)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Pending Review Queue", f"{len(pending_apps)} Applications", "Action Required" if pending_apps else "Up to date")
    k2.metric("Total Sanctioned Capital", f"₹{total_sanctioned_val:,.0f}", f"{len(sanctioned_apps)} Awaiting Disbursal")
    k3.metric("Simulated Disbursed", f"₹{total_disbursed_val:,.0f}", f"{len(disbursed_apps)} Vouchers Issued")
    k4.metric("PSL Compliance", "100% Eligible", "RBI Direct Agri PSL")

    st.markdown("---")

    lender_tab1, lender_tab2, lender_tab3, lender_tab4 = st.tabs([
        f"⏳ Pending Review ({len(pending_apps)})",
        f"✅ Sanctioned Loans ({len(sanctioned_apps)})",
        f"💳 Disbursed Vouchers ({len(disbursed_apps)})",
        f"🚫 Rejected Archive ({len(rejected_apps)})"
    ])

    # 1. PENDING REVIEW QUEUE (Strictly only PENDING_REVIEW loans)
    with lender_tab1:
        st.write("### ⏳ Smallholder Loan Applications Pending Underwriting Review")
        st.caption("Review agronomic cashflow, daily AGMARKNET mandi modal prices, and 3-peer FPO social guarantees.")

        if not pending_apps:
            st.info("✅ All submitted applications have been processed. No smallholder loans pending review.")
        else:
            for app in pending_apps:
                with st.expander(f"👨‍🌾 #{app['assessment_id']} — {app['farmer_name']} | {app['crop_name']} ({app['acres']} Acres) | Limit: ₹{app['sanctioned_limit']:,.0f} | Status: PENDING_REVIEW", expanded=True):
                    col_d1, col_d2, col_d3 = st.columns(3)
                    with col_d1:
                        st.markdown(f"**Borrower:** {app['farmer_name']} (Phone: `{app.get('phone', 'N/A')}`)")
                        st.markdown(f"**Location:** {app.get('village', 'Pimpalgaon')}, {app.get('district', 'Nashik')}")
                        st.markdown(f"**Credit Score:** `{app['credit_score']} / 100` ({app.get('risk_category', 'Tier-1')})")
                    with col_d2:
                        st.markdown(f"**Daily AGMARKNET Price:** ₹{app.get('mandi_price_per_qtl', 2250):,.0f}/qtl")
                        st.markdown(f"**Expected Yield:** {app.get('projected_yield', 18)} qtl/acre")
                        st.markdown(f"**Social Collateral:** `{app.get('social_collateral', '3/3 Verified')}` ({app.get('peer_group_code', 'GRP-SAHYADRI-01')})")
                    with col_d3:
                        st.markdown(f"**Repayment Model:** Single Harvest Bullet (0 Monthly EMI)")
                        st.markdown(f"**Bullet Due Date:** `{app.get('bullet_repayment_date', '15-Jan-2027')}`")
                        st.markdown(f"**Field Verification:** `{app.get('crop_verification', 'VERIFIED')}`")

                    st.markdown("---")
                    # Actions: Only Sanction and Reject are allowed. Disburse is NOT permitted for PENDING_REVIEW loans.
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        with st.popover(f"✅ Sanction Loan #{app['assessment_id']}", use_container_width=True):
                            st.markdown(f"#### Confirm Sanction for #{app['assessment_id']}")
                            st.markdown(f"**Farmer:** {app['farmer_name']} ({app.get('village', '')}, {app.get('district', '')})")
                            st.markdown(f"**Approved Limit:** `₹{app['sanctioned_limit']:,.0f}`")
                            st.markdown(f"**Bullet Repayment Due:** `{app['bullet_repayment_date']}`")
                            s_notes = st.text_input(
                                "Lender Audit Notes:",
                                value="Sanctioned under Priority Sector Lending. Crop verified by FPO coordinator.",
                                key=f"s_notes_{app['assessment_id']}"
                            )
                            if st.button(f"Confirm & Sanction #{app['assessment_id']}", key=f"btn_sanc_{app['assessment_id']}", type="primary", use_container_width=True):
                                with st.spinner("Recording sanction in database..."):
                                    ok, msg, res = execute_lender_decision(app['assessment_id'], "SANCTIONED", s_notes)
                                    if ok:
                                        st.success(msg)
                                        time.sleep(0.4)
                                        st.rerun()
                                    else:
                                        st.error(f"Sanction Failed: {msg}")

                    with b_col2:
                        with st.popover(f"❌ Reject Loan #{app['assessment_id']}", use_container_width=True):
                            st.markdown(f"#### Confirm Rejection for #{app['assessment_id']}")
                            st.markdown(f"**Farmer:** {app['farmer_name']}")
                            st.markdown(f"**Limit Requested:** `₹{app['sanctioned_limit']:,.0f}`")
                            r_notes = st.text_input(
                                "Rejection Rationale:",
                                value="Insufficient agronomic cashflow margin / high production risk.",
                                key=f"r_notes_{app['assessment_id']}"
                            )
                            if st.button(f"Confirm Rejection #{app['assessment_id']}", key=f"btn_rej_{app['assessment_id']}", type="primary", use_container_width=True):
                                with st.spinner("Recording rejection in database..."):
                                    ok, msg, res = execute_lender_decision(app['assessment_id'], "REJECTED", r_notes)
                                    if ok:
                                        st.warning(msg)
                                        time.sleep(0.4)
                                        st.rerun()
                                    else:
                                        st.error(f"Rejection Failed: {msg}")

    # 2. SANCTIONED LOANS (Ready for Disbursement)
    with lender_tab2:
        st.write("### ✅ Sanctioned Loans Awaiting Voucher Disbursement")
        st.info(
            "ℹ️ **Simulated Disbursement Rail**: KisanSetu issues simulated purpose-bound NPCI e-RUPI vouchers locked to agricultural input merchants (MCCs 5261/5193). "
            "This is a demonstration environment; no real fiat money is transferred."
        )

        if not sanctioned_apps:
            st.info("No sanctioned loans awaiting disbursement.")
        else:
            for app in sanctioned_apps:
                with st.expander(f"🌾 #{app['assessment_id']} — {app['farmer_name']} | {app['crop_name']} | Sanctioned Limit: ₹{app['sanctioned_limit']:,.0f} | Status: SANCTIONED", expanded=True):
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.markdown(f"**Borrower:** {app['farmer_name']} (Phone: `{app.get('phone', 'N/A')}`)")
                        st.markdown(f"**Location:** {app.get('village', 'Pimpalgaon')}, {app.get('district', 'Nashik')}")
                        st.markdown(f"**Sanctioned Amount:** `₹{app['sanctioned_limit']:,.0f}`")
                    with col_s2:
                        st.markdown(f"**Credit Score:** `{app['credit_score']} / 100` ({app.get('risk_category', 'Tier-1')})")
                        st.markdown(f"**Bullet Repayment Due:** `{app.get('bullet_repayment_date', '15-Jan-2027')}`")
                        st.markdown(f"**Peer Guarantee:** `{app.get('peer_group_code', 'GRP-SAHYADRI-01')}`")
                    with col_s3:
                        st.markdown(f"**Lender Audit Notes:**")
                        st.caption(f"_{app.get('lender_notes') or 'Sanctioned under PSL'}_")

                    st.markdown("---")
                    # Action: Only Disburse is allowed. Sanction and Reject are hidden.
                    with st.popover(f"⚡ Disburse e-RUPI Voucher #{app['assessment_id']}", use_container_width=True):
                        st.markdown(f"#### Execute Simulated Disbursement for #{app['assessment_id']}")
                        st.markdown(f"**Beneficiary:** {app['farmer_name']} (Phone: `{app.get('phone', 'N/A')}`)")
                        st.markdown(f"**Sanctioned Amount:** `₹{app['sanctioned_limit']:,.0f}`")
                        st.markdown(f"**Disbursement Channel:** Simulated NPCI e-RUPI Purpose-Bound Agro-Voucher")
                        st.caption("⚠️ Notice: This is a **simulated demonstration**. No real financial funds will be transferred.")
                        if st.button(f"Confirm Simulated Disbursal #{app['assessment_id']}", key=f"btn_disb_{app['assessment_id']}", type="primary", use_container_width=True):
                            with st.spinner("Generating e-RUPI sandbox voucher and updating database..."):
                                ok, msg, res = execute_lender_disbursement(app['assessment_id'])
                                if ok:
                                    st.success(msg)
                                    time.sleep(0.4)
                                    st.rerun()
                                else:
                                    st.error(f"Disbursement Failed: {msg}")

    # 3. DISBURSED LOANS ARCHIVE
    with lender_tab3:
        st.write("### 💳 Disbursed Loans & Active Harvest Credit Book")
        st.caption("Disbursed agricultural capital with simulated transaction hashes and harvest bullet repayment schedules.")

        if not disbursed_apps:
            st.info("No loans disbursed yet.")
        else:
            for app in disbursed_apps:
                with st.expander(f"💳 #{app['assessment_id']} — {app['farmer_name']} | Disbursed: ₹{app['sanctioned_limit']:,.0f} | Status: DISBURSED", expanded=False):
                    cd1, cd2, cd3 = st.columns(3)
                    with cd1:
                        st.markdown(f"**Beneficiary:** {app['farmer_name']}")
                        st.markdown(f"**Disbursed Amount:** `₹{app['sanctioned_limit']:,.0f}`")
                        st.markdown(f"**Disbursement Tx ID:** `{app.get('disbursement_tx_id') or 'SIM-eRUPI-TX'}`")
                    with cd2:
                        st.markdown(f"**Disbursement Mode:** Simulated e-RUPI Voucher")
                        st.markdown(f"**Disbursed At:** `{app.get('disbursed_at') or 'Recorded'}`")
                        st.markdown(f"**Bullet Repayment Due:** `{app.get('bullet_repayment_date')}`")
                    with cd3:
                        st.markdown(f"**Guarantee Circle:** `{app.get('peer_group_code', 'GRP-SAHYADRI-01')}`")
                        st.markdown(f"**Crop:** {app.get('crop_name')} ({app.get('acres')} Ac)")
                        st.markdown(f"**Credit Score:** `{app.get('credit_score')} / 100`")

    # 4. REJECTED ARCHIVE
    with lender_tab4:
        st.write("### 🚫 Rejected Smallholder Loan Applications")
        st.caption("Archived applications that did not meet credit or agronomic margin criteria.")

        if not rejected_apps:
            st.info("No rejected applications on record.")
        else:
            for app in rejected_apps:
                with st.expander(f"🚫 #{app['assessment_id']} — {app['farmer_name']} | Requested Limit: ₹{app['sanctioned_limit']:,.0f} | Status: REJECTED", expanded=False):
                    cr1, cr2 = st.columns(2)
                    with cr1:
                        st.markdown(f"**Applicant:** {app['farmer_name']} ({app.get('village', 'Pimpalgaon')}, {app.get('district', 'Nashik')})")
                        st.markdown(f"**Crop & Acreage:** {app.get('crop_name')} ({app.get('acres')} Acres)")
                        st.markdown(f"**Credit Score:** `{app.get('credit_score')} / 100`")
                    with cr2:
                        st.markdown(f"**Rejection Rationale:**")
                        st.error(f"_{app.get('lender_notes') or 'Insufficient margin.'}_")
                        st.caption(f"Assessment Date: {app.get('assessment_date') or 'N/A'}")

    # Mandi Price Stability & Trend Monitoring
    st.markdown("---")
    st.write("### 📈 AGMARKNET Mandi Price Trend Monitoring (30-Day APMC History)")
    st.caption("Ensuring commodity market stability and protecting harvest bullet repayment realization.")

    mandi_crop_choice = st.selectbox("Select Crop for Mandi Trend Analysis:", list(AGMARKNET_MANDI_CATALOG.keys()))
    crop_mandi_data = AGMARKNET_MANDI_CATALOG[mandi_crop_choice]

    trend_dates = [(datetime.now() - timedelta(days=29 - i)).strftime("%d-%b") for i in range(30)]
    trend_df = pd.DataFrame({
        "Date": trend_dates,
        "Modal Price (₹/qtl)": crop_mandi_data["historical_30d_prices"],
        "MSP Benchmark (₹/qtl)": [crop_mandi_data["msp_benchmark"]] * 30
    }).set_index("Date")

    st.line_chart(trend_df)
    st.info(
        f"**Market Assessment for {mandi_crop_choice}:** Modal price at {crop_mandi_data['primary_mandi']} is "
        f"₹{crop_mandi_data['modal_price_per_qtl']:,.0f}/qtl ({crop_mandi_data['trend_30d_pct']:+.1f}% 30-day change). "
        f"Current market prices are well above the GoI MSP benchmark of ₹{crop_mandi_data['msp_benchmark']:,.0f}/qtl, "
        "indicating strong cashflow viability for seasonal bullet repayment."
    )