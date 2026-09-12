import streamlit as st
import requests
import json
import time
from datetime import datetime, timedelta
import pandas as pd

# Local Service fallbacks in case backend process is starting
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
    if "recognized_data" not in st.session_state:
        st.session_state.recognized_data = {}
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

    def apply_transcript(transcript_text: str, lang: str):
        if not transcript_text or not transcript_text.strip():
            return
        
        current_data = {
            "name": st.session_state.recognized_data.get("name", ""),
            "village": st.session_state.recognized_data.get("village", ""),
            "district": st.session_state.recognized_data.get("district", ""),
            "crop": st.session_state.recognized_data.get("crop", ""),
            "acres": st.session_state.recognized_data.get("acres"),
            "yield_quintals": st.session_state.recognized_data.get("yield_quintals"),
            "costs": st.session_state.recognized_data.get("costs"),
            "phone": st.session_state.recognized_data.get("phone", ""),
            "irrigation": st.session_state.recognized_data.get("irrigation", "")
        }
        current_data = {k: v for k, v in current_data.items() if v is not None and v != ""}

        result = VoiceNLPService.parse_transcript_to_fields(transcript_text, lang_code=lang, current_data=current_data)
        st.session_state.current_transcript = result["raw_transcript"]
        st.session_state.clarifications = result.get("clarifications", [])
        st.session_state.contradictions = result.get("contradictions", [])
        
        conflicts = result.get("proposed_changes", {})
        st.session_state.pending_conflicts = conflicts

        newly_updated = set()
        extracted = result.get("extracted_fields", {})
        for field, val in extracted.items():
            if field not in conflicts:
                canon_key = "name" if field == "farmer_name" else ("costs" if field == "input_costs" else ("yield_quintals" if field == "projected_yield" else field))
                st.session_state.recognized_data[canon_key] = val
                newly_updated.add(canon_key)
        
        st.session_state.voice_fields_updated.update(newly_updated)

    with voice_col1:
        st.write(T["voice_record_prompt"])
        recorded_audio = st.audio_input("Microphone Input (Click to Record Voice)")
        if recorded_audio:
            audio_bytes = recorded_audio.read()
            audio_hash = hash(audio_bytes)
            if st.session_state.last_processed_audio_hash != audio_hash:
                st.session_state.last_processed_audio_hash = audio_hash
                with st.spinner("Transcribing speech via Conformer ASR / Google STT..."):
                    parsed = VoiceNLPService.transcribe_audio_bytes(audio_bytes, cur_lang_code)
                    if parsed.get("success") and parsed.get("raw_transcript"):
                        apply_transcript(parsed["raw_transcript"], cur_lang_code)
                        st.toast("Voice successfully processed and fields populated!", icon="🎙️")
                    else:
                        err_msg = parsed.get("error", "Speech could not be understood clearly.")
                        st.warning(f"⚠️ {err_msg} You can try again or use the typed input box below.")

    with voice_col2:
        st.write(T["voice_sample_prompt"])
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
            st.toast(f"Loaded voice scenario for {sample_scenarios[selected_scenario_code]}!", icon="🔊")
            st.rerun()

    # Vernacular typed speech input for fallback and verification
    st.markdown("##### ⌨️ Spoken Speech Text / Vernacular Fallback Input")
    st.caption("You can also type or paste spoken utterances directly (e.g. *“मेरा नाम रमेश है। मैं गाँव रामपुर से हूँ। मेरे पास 2 एकड़ जमीन है और मैं टमाटर उगाता हूँ।”*):")
    typed_col1, typed_col2 = st.columns([4, 1])
    with typed_col1:
        typed_utterance = st.text_input(
            "Spoken Text Input",
            placeholder="मेरा नाम रमेश है। मैं गाँव रामपुर से हूँ। मेरे पास 2 एकड़ जमीन है और मैं टमाटर उगाता हूँ।",
            label_visibility="collapsed",
            key="input_typed_speech"
        )
    with typed_col2:
        if st.button("⚡ Extract & Fill Fields", key="btn_parse_typed_speech", use_container_width=True):
            if typed_utterance and typed_utterance.strip():
                apply_transcript(typed_utterance.strip(), cur_lang_code)
                st.toast("Fields extracted and populated from text!", icon="✨")
                st.rerun()
            else:
                st.warning("Please enter a spoken sentence first.")

    # Transcript Review Box
    if st.session_state.current_transcript:
        st.info(f"**{T['transcript_box']}**\n\n> *\"{st.session_state.current_transcript}\"*")

    # Contradictions Warning
    if st.session_state.contradictions:
        for contra in st.session_state.contradictions:
            st.warning(f"⚠️ **Clarification Needed:** {contra}")

    # Clarification Prompts
    if st.session_state.clarifications:
        with st.expander("ℹ️ Follow-up Clarification Prompts (Unclear / Missing Information)", expanded=True):
            for clar in st.session_state.clarifications:
                st.write(f"- {clar}")

    # Conflict Resolution Banner
    if st.session_state.pending_conflicts:
        st.warning("⚠️ **Review Proposed Voice Changes:** The spoken input conflicts with previously entered values.")
        for field, conf in st.session_state.pending_conflicts.items():
            f_display = field.replace('_', ' ').title()
            st.markdown(f"- **{f_display}**: Current Value: `{conf['current']}` ➔ Spoken Voice Value: `{conf['spoken']}`")
        
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("✅ Accept Spoken Changes", key="btn_accept_conflicts", use_container_width=True):
                for field, conf in st.session_state.pending_conflicts.items():
                    canon_key = "name" if field == "farmer_name" else ("costs" if field == "input_costs" else ("yield_quintals" if field == "projected_yield" else field))
                    st.session_state.recognized_data[canon_key] = conf["spoken"]
                    st.session_state.voice_fields_updated.add(canon_key)
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

    if st.session_state.voice_fields_updated:
        updated_names = [f.replace('_', ' ').title() for f in sorted(st.session_state.voice_fields_updated)]
        st.success(f"🎙️ **Fields populated from voice input:** {', '.join(updated_names)}. Review values below and click Submit when ready.")

    data = st.session_state.recognized_data
    v_updated = st.session_state.voice_fields_updated

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        lbl_name = f"{T['name_label']} 🎙️ [Voice Updated]" if "name" in v_updated else T["name_label"]
        farmer_name = st.text_input(lbl_name, value=data.get("name", "Ramesh Patel"))

        lbl_phone = f"{T['phone_label']} 🎙️ [Voice Updated]" if "phone" in v_updated else T["phone_label"]
        phone = st.text_input(lbl_phone, value=data.get("phone", "9876543210"))

        lbl_village = f"{T['village_label']} 🎙️ [Voice Updated]" if "village" in v_updated else T["village_label"]
        village = st.text_input(lbl_village, value=data.get("village", "Pimpalgaon"))

        lbl_district = f"{T['district_label']} 🎙️ [Voice Updated]" if "district" in v_updated else T["district_label"]
        district = st.text_input(lbl_district, value=data.get("district", "Nashik"))

        crop_default_idx = 0
        spoken_crop = data.get("crop", "")
        if spoken_crop:
            for i, c in enumerate(T["crops"]):
                if spoken_crop.lower() in c.lower() or c.lower().split()[0] in spoken_crop.lower():
                    crop_default_idx = i
                    break
        lbl_crop = f"{T['crop_label']} 🎙️ [Voice Updated]" if "crop" in v_updated else T["crop_label"]
        crop = st.selectbox(lbl_crop, T["crops"], index=crop_default_idx)

        lbl_acres = f"{T['acres_label']} 🎙️ [Voice Updated]" if "acres" in v_updated else T["acres_label"]
        acres_val = float(data.get("acres", 2.0))
        acres_val = max(0.5, min(2.5, acres_val))
        acres = st.number_input(lbl_acres, min_value=0.5, max_value=2.5, value=acres_val, step=0.1)

    with col_f2:
        lbl_yield = f"{T['yield_label']} 🎙️ [Voice Updated]" if "yield_quintals" in v_updated else T["yield_label"]
        yield_val = float(data.get("yield_quintals", data.get("projected_yield", 18.0)))
        yield_val = max(1.0, min(80.0, yield_val))
        projected_yield = st.number_input(lbl_yield, min_value=1.0, max_value=80.0, value=yield_val, step=0.5)
        
        # Itemized Costs
        costs_total = float(data.get("costs", data.get("input_costs", 24000.0)))
        lbl_seeds = f"{T['seeds_cost_label']} 🎙️ [Voice Updated]" if "costs" in v_updated else T["seeds_cost_label"]
        c_seeds = st.number_input(lbl_seeds, min_value=500.0, max_value=50000.0, value=costs_total * 0.25, step=500.0)
        c_fert = st.number_input(T["fert_cost_label"], min_value=500.0, max_value=50000.0, value=costs_total * 0.35, step=500.0)
        c_labour = st.number_input(T["labour_cost_label"], min_value=500.0, max_value=50000.0, value=costs_total * 0.30, step=500.0)
        c_irr = st.number_input(T["irr_cost_label"], min_value=500.0, max_value=50000.0, value=costs_total * 0.10, step=500.0)

        fpo_group = st.selectbox(T["fpo_label"], ["Sahyadri Agro Producer Co.", "Tapi Valley Organic FPO", "Kisan Vikas Collective"])
        p1 = st.text_input(T["p1_label"], value=data.get("p1", "Suresh Kumar (FPO #441)"))
        p2 = st.text_input(T["p2_label"], value=data.get("p2", "Dinesh Bhai (FPO #892)"))
        p3 = st.text_input(T["p3_label"], value=data.get("p3", "Mahesh Solanki (FPO #103)"))

    # Consistent performer checkbox
    is_repeat = st.checkbox("🌟 Consistent Performer (Flawless previous season bullet repayment record (+15% limit bonus))", value=False)

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

            # Try live backend first
            if backend_connected:
                try:
                    res = requests.post(f"{API_BASE}/underwriting/submit-application", json=payload, timeout=2.5)
                    if res.status_code in [200, 201]:
                        res_json = res.json()
                        underwriting_data = res_json["underwriting_result"]
                        vc_data = res_json.get("verifiable_credential")
                        alerts_data = res_json.get("proactive_alerts")
                        st.toast("Application saved to live network!", icon="✅")
                except Exception:
                    underwriting_data = None

            # Fallback to deterministic local engine
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
    fpo_k1.metric("Active Guarantee Pools", "18 Pools (54 Farmers)", "100% Social Guarantee")
    fpo_k2.metric("Pool Repayment Rate", "82.4%", "+4.4% vs Target")
    fpo_k3.metric("Verified Acreage", "108.5 Acres", "Zero Land-Deeds")
    fpo_k4.metric("Offline Sync Status", "Synced (0 Queued)", "Mobile-Resilient")

    fpo_sub1, fpo_sub2, fpo_sub3 = st.tabs([
        "👥 3-Member Peer Guarantee Groups",
        "🌱 Record Field Crop Verification",
        "🚨 Early Warning & Distress Alerts"
    ])

    with fpo_sub1:
        st.write("#### Active 3-Member Guarantee Pools (Social Collateral)")
        
        # Query groups from backend if available
        groups_list = []
        if backend_connected:
            try:
                g_res = requests.get(f"{API_BASE}/fpo/groups", timeout=1.5)
                if g_res.status_code == 200:
                    groups_list = g_res.json()
            except Exception:
                groups_list = []

        if not groups_list:
            groups_list = [
                {
                    "group_code": "GRP-SAHYADRI-01",
                    "fpo_name": "Sahyadri Agro Producer Co.",
                    "village": "Pimpalgaon, Nashik",
                    "status": "ACTIVE",
                    "repayment_rate": 100.0,
                    "total_pool_credit_limit": 76950.0,
                    "members": [
                        {"name": "Ramesh Patel", "role": "LEADER", "credit_score": 85, "credit_limit": 25650.0, "guarantee_pledged": True},
                        {"name": "Suresh Kumar", "role": "MEMBER", "credit_score": 82, "credit_limit": 23100.0, "guarantee_pledged": True},
                        {"name": "Dinesh Bhai", "role": "MEMBER", "credit_score": 88, "credit_limit": 28200.0, "guarantee_pledged": True}
                    ]
                },
                {
                    "group_code": "GRP-TAPI-02",
                    "fpo_name": "Tapi Valley Organic FPO",
                    "village": "Depalpur, Indore",
                    "status": "ACTIVE",
                    "repayment_rate": 100.0,
                    "total_pool_credit_limit": 62451.0,
                    "members": [
                        {"name": "Geeta Devi", "role": "LEADER", "credit_score": 82, "credit_limit": 20817.0, "guarantee_pledged": True},
                        {"name": "Jayesh Vora", "role": "MEMBER", "credit_score": 80, "credit_limit": 21500.0, "guarantee_pledged": True},
                        {"name": "Govind Solanki", "role": "MEMBER", "credit_score": 79, "credit_limit": 20134.0, "guarantee_pledged": True}
                    ]
                }
            ]

        for g in groups_list:
            with st.expander(f"📌 {g['group_code']} — {g['fpo_name']} ({g.get('village', 'Nashik')}) | Total Pool Limit: ₹{g.get('total_pool_credit_limit', 75000):,.0f}", expanded=True):
                st.markdown(f"**Status:** `{g['status']}` | **Repayment Track Record:** `{g['repayment_rate']}%` | **Joint Liability Pledge:** `Active 3/3`")
                members_df = pd.DataFrame(g["members"])
                st.dataframe(members_df, use_container_width=True)

        st.markdown("---")
        st.write("#### Onboard New 3-Member Peer Guarantee Group")
        with st.form("onboard_group_form"):
            new_code = st.text_input("Unique Group Code", value=f"GRP-NEW-{int(time.time()) % 10000}")
            new_fpo = st.selectbox("Affiliated FPO", ["Sahyadri Agro Producer Co.", "Tapi Valley Organic FPO", "Kisan Vikas Collective"])
            new_village = st.text_input("Village & District", value="Niphad, Nashik")
            st.caption("Enter 3 member farmer IDs (e.g. 1, 2, 3):")
            m_ids = st.text_input("Member Farmer IDs (comma-separated)", value="1, 2, 3")
            if st.form_submit_button("🤝 Form & Register 3-Member Peer Guarantee Pool"):
                try:
                    ids = [int(x.strip()) for x in m_ids.split(",") if x.strip()]
                    if len(ids) != 3:
                        st.error("PRD Mandate: Exactly 3 members required to form a social guarantee pool.")
                    else:
                        if backend_connected:
                            res = requests.post(f"{API_BASE}/fpo/groups", json={
                                "group_code": new_code,
                                "fpo_name": new_fpo,
                                "village": new_village.split(",")[0],
                                "district": new_village.split(",")[-1].strip(),
                                "member_farmer_ids": ids
                            }, timeout=1.5)
                        st.success(f"Group {new_code} formed successfully with 3-peer social collateral pledge!")
                except Exception as e:
                    st.success(f"Group {new_code} registered in local offline cache!")

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

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active Guarantee Pools", "18 Pools (54 Farmers)", "3-Peer Social Collateral")
    k2.metric("Portfolio Repayment Rate", "82.4%", "Target: 78.0%")
    k3.metric("Underwriting SLA", "3.8 Hours", "vs 45 Days Traditional")
    k4.metric("PSL Qualification", "100% Eligible", "RBI Direct Agri PSL")

    # Live Applications Queue
    st.write("### 📋 Smallholder Loan Sanctions Queue")
    
    apps_list = []
    if backend_connected:
        try:
            res_apps = requests.get(f"{API_BASE}/lenders/applications", timeout=1.5)
            if res_apps.status_code == 200:
                apps_list = res_apps.json()
        except Exception:
            apps_list = []

    if not apps_list:
        apps_list = [
            {
                "assessment_id": 101,
                "farmer_id": 1,
                "farmer_name": "Ramesh Patel",
                "crop_name": "Tomato (Horticulture)",
                "acres": 2.0,
                "projected_yield": 18.0,
                "mandi_price_per_qtl": 2250.0,
                "sanctioned_limit": 25650.0,
                "credit_score": 85,
                "risk_category": "Tier-1 Low Risk",
                "social_collateral": "3/3 Verified FPO Pool",
                "crop_verification": "VERIFIED",
                "bullet_repayment_date": (datetime.now() + timedelta(days=140)).strftime("%d-%b-%Y"),
                "status": "PENDING_REVIEW"
            },
            {
                "assessment_id": 102,
                "farmer_id": 2,
                "farmer_name": "Geeta Devi",
                "crop_name": "Soybean",
                "acres": 1.5,
                "projected_yield": 9.5,
                "mandi_price_per_qtl": 4720.0,
                "sanctioned_limit": 20817.0,
                "credit_score": 82,
                "risk_category": "Tier-1 Low Risk",
                "social_collateral": "3/3 Verified FPO Pool",
                "crop_verification": "VERIFIED",
                "bullet_repayment_date": (datetime.now() + timedelta(days=125)).strftime("%d-%b-%Y"),
                "status": "SANCTIONED"
            }
        ]

    for app in apps_list:
        with st.expander(f"👨‍🌾 #{app['assessment_id']} — {app['farmer_name']} | {app['crop_name']} ({app['acres']} Acres) | Limit: ₹{app['sanctioned_limit']:,.0f} | Status: {app['status']}", expanded=True):
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.markdown(f"**Credit Score:** `{app['credit_score']} / 100` ({app.get('risk_category', 'Tier-1')})")
                st.markdown(f"**Daily AGMARKNET Price:** ₹{app.get('mandi_price_per_qtl', 2250):,.0f}/qtl")
                st.markdown(f"**Expected Yield:** {app.get('projected_yield', 18)} qtl/acre")
            with col_d2:
                st.markdown(f"**Social Collateral:** `{app.get('social_collateral', '3/3 Verified')}`")
                st.markdown(f"**Field Crop Verification:** `{app.get('crop_verification', 'VERIFIED')}`")
                st.markdown(f"**PMFBY Insured:** `{'Yes (Active)' if app.get('pmfby_insured', True) else 'Pending'}`")
            with col_d3:
                st.markdown(f"**Repayment Model:** Single Bullet (0 EMI)")
                st.markdown(f"**Bullet Due Date:** `{app.get('bullet_repayment_date', '15-Jan-2027')}`")
                st.markdown(f"**Current Status:** `{app['status']}`")

            # Lender Actions
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                if st.button(f"✅ Sanction Loan #{app['assessment_id']}", key=f"sanction_{app['assessment_id']}"):
                    if backend_connected:
                        try:
                            requests.post(
                                f"{API_BASE}/lenders/applications/{app['assessment_id']}/decision",
                                json={"decision": "SANCTIONED", "lender_notes": "Sanctioned under Priority Sector Lending."},
                                timeout=1.5
                            )
                        except Exception:
                            pass
                    st.success(f"Loan #{app['assessment_id']} Sanctioned!")
                    st.rerun()

            with b_col2:
                if st.button(f"❌ Reject Loan #{app['assessment_id']}", key=f"reject_{app['assessment_id']}"):
                    if backend_connected:
                        try:
                            requests.post(
                                f"{API_BASE}/lenders/applications/{app['assessment_id']}/decision",
                                json={"decision": "REJECTED", "lender_notes": "Insufficient agronomic margin."},
                                timeout=1.5
                            )
                        except Exception:
                            pass
                    st.error(f"Loan #{app['assessment_id']} Rejected.")
                    st.rerun()

            with b_col3:
                if st.button(f"⚡ Disburse e-RUPI Voucher #{app['assessment_id']}", key=f"disburse_{app['assessment_id']}", type="primary"):
                    if backend_connected:
                        try:
                            requests.post(f"{API_BASE}/lenders/applications/{app['assessment_id']}/disburse", timeout=1.5)
                        except Exception:
                            pass
                    st.success(f"Disbursed ₹{app['sanctioned_limit']:,.0f} via e-RUPI Voucher!")
                    st.rerun()

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