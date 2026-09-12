/**
 * KisanTrust - Community-Owned Credit Network
 * Frontend Application & Underwriting Interface
 */

// Dynamic API Base URL for Cloud Deployment / GitHub Pages / Localhost
const API_BASE_URL = window.API_BASE_URL || (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" ? "http://127.0.0.1:8000" : "");

// Embedded baseline datasets for resilient offline / file:// protocol execution
const DEFAULT_AGMARKNET = [
  { commodity: "Tomato", market: "Pimpalgaon Mandi", district: "Nashik", state: "Maharashtra", modal_price: 1850, arrivals_tonnes: 310.2, trend: "+12.1%", peak: "August-September" },
  { commodity: "Onion", market: "Lasalgaon Mandi", district: "Nashik", state: "Maharashtra", modal_price: 2320, arrivals_tonnes: 480.5, trend: "+8.4%", peak: "October-November" },
  { commodity: "Grapes", market: "Nashik APMC", district: "Nashik", state: "Maharashtra", modal_price: 5450, arrivals_tonnes: 140.0, trend: "-3.2%", peak: "February-April" },
  { commodity: "Tomato", market: "Kolar APMC Yard", district: "Kolar", state: "Karnataka", modal_price: 2050, arrivals_tonnes: 520.0, trend: "+5.6%", peak: "July-October" },
  { commodity: "Potato", market: "Chintamani Mandi", district: "Chikkaballapur", state: "Karnataka", modal_price: 1580, arrivals_tonnes: 260.4, trend: "+1.8%", peak: "November-January" },
  { commodity: "Chilli (Dry)", market: "Guntur Mirchi Yard", district: "Guntur", state: "Andhra Pradesh", modal_price: 17200, arrivals_tonnes: 890.0, trend: "+4.3%", peak: "January-April" },
  { commodity: "Pomegranate", market: "Anantapur APMC", district: "Anantapur", state: "Andhra Pradesh", modal_price: 8900, arrivals_tonnes: 95.0, trend: "+9.0%", peak: "September-December" },
  { commodity: "Potato", market: "Agra APMC", district: "Agra", state: "Uttar Pradesh", modal_price: 1510, arrivals_tonnes: 720.0, trend: "+3.4%", peak: "February-May" },
  { commodity: "Cauliflower", market: "Varanasi Mandi", district: "Varanasi", state: "Uttar Pradesh", modal_price: 1420, arrivals_tonnes: 180.0, trend: "-2.1%", peak: "December-February" },
  { commodity: "Turmeric", market: "Salem APMC", district: "Salem", state: "Tamil Nadu", modal_price: 12400, arrivals_tonnes: 340.0, trend: "+7.9%", peak: "March-May" },
  { commodity: "Onion", market: "Indore Mandi (Choithram)", district: "Indore", state: "Madhya Pradesh", modal_price: 2180, arrivals_tonnes: 610.0, trend: "+6.7%", peak: "April-June" }
];

const DEFAULT_NHB = [
  { crop: "Tomato", category: "Vegetable", avg_yield: 98.0, cost_acre: 38000, days: 105, drip_boost: 1.18 },
  { crop: "Onion", category: "Vegetable", avg_yield: 88.0, cost_acre: 32000, days: 120, drip_boost: 1.15 },
  { crop: "Potato", category: "Vegetable / Tuber", avg_yield: 115.0, cost_acre: 42000, days: 90, drip_boost: 1.12 },
  { crop: "Grapes", category: "Fruit", avg_yield: 105.0, cost_acre: 68000, days: 150, drip_boost: 1.22 },
  { crop: "Chilli (Dry)", category: "Spice / Cash Crop", avg_yield: 22.5, cost_acre: 45000, days: 140, drip_boost: 1.20 },
  { crop: "Pomegranate", category: "Fruit", avg_yield: 56.0, cost_acre: 55000, days: 180, drip_boost: 1.25 },
  { crop: "Turmeric", category: "Spice / Commercial", avg_yield: 32.0, cost_acre: 48000, days: 210, drip_boost: 1.15 },
  { crop: "Cauliflower", category: "Vegetable", avg_yield: 74.0, cost_acre: 28000, days: 80, drip_boost: 1.12 }
];

const DEFAULT_PMFBY = [
  { district: "Nashik, Maharashtra", crops: "Onion, Tomato, Grapes", loss_ratio: "0.32 (Low Risk)", hazard: "Hailstorm (Feb/Mar)", risk_factor: "1.02x (Favorable)" },
  { district: "Kolar, Karnataka", crops: "Tomato, Potato", loss_ratio: "0.38 (Moderate)", hazard: "Dry spell (May)", risk_factor: "0.98x (Standard)" },
  { district: "Guntur, Andhra Pradesh", crops: "Chilli, Turmeric", loss_ratio: "0.24 (Very Low)", hazard: "Cyclone rain (Nov)", risk_factor: "1.05x (Superior)" },
  { district: "Agra, Uttar Pradesh", crops: "Potato, Mustard", loss_ratio: "0.41 (Moderate)", hazard: "Cold wave / Blight", risk_factor: "0.96x (Standard)" },
  { district: "Salem, Tamil Nadu", crops: "Turmeric, Tapioca", loss_ratio: "0.22 (Very Low)", hazard: "Monsoon delay", risk_factor: "1.06x (Superior)" }
];

const DEFAULT_ICAR = [
  { id: "ICAR-2026-DIS-09", crop: "Tomato", disease: "Early Blight (Alternaria solani)", area: "Kolar, Chittoor", action: "Copper oxychloride @ 2.5g/L; Drip fertigation optimization" },
  { id: "ICAR-2026-DIS-14", crop: "Chilli (Dry)", disease: "Black Thrips (Thrips parvispinus)", area: "Guntur, Khammam", action: "Blue sticky traps + Spinetoram bio-spray" },
  { id: "ICAR-2026-DIS-22", crop: "Onion", disease: "Stemphylium Leaf Blight", area: "Nashik, Indore", action: "Prophylactic Mancozeb spray @ 2g/L" }
];

// FPO Peer Circle Mock Data for Interaction
const PEER_MEMBERS = {
  1: {
    name: "Ramesh Tukaram Patil",
    role: "Primary Borrower",
    location: "Pimpalgaon Baswant, Nashik, MH",
    crop: "Tomato (1.5 Acres)",
    irrigation: "Micro-Drip Installed",
    history: "100% On-Time (3 Seasons)",
    pmkisan: "Active DBT Seeding (data.gov.in)",
    score: 91,
    verified: true
  },
  2: {
    name: "Suresh Shinde",
    role: "Co-Guarantor 1",
    location: "Pimpalgaon Baswant, Nashik, MH",
    crop: "Onion (1.2 Acres)",
    irrigation: "Canal & Borewell",
    history: "100% On-Time (4 Seasons)",
    pmkisan: "Active DBT Seeding",
    score: 88,
    verified: true
  },
  3: {
    name: "Balasaheb Jadhav",
    role: "Co-Guarantor 2",
    location: "Ozar Taluq, Nashik, MH",
    crop: "Grapes (2.0 Acres)",
    irrigation: "Micro-Drip Installed",
    history: "100% On-Time (5 Seasons)",
    pmkisan: "Active DBT Seeding",
    score: 94,
    verified: true
  }
};

let activeSelectedPeer = 1;

// Multilingual Translations
const TRANSLATIONS = {
  en: {
    heading: "Collateral-Free Institutional Credit for Marginal Farmers",
    lead: "Access priority credit at 9.0% – 10.5% interest with zero land titles (*patta*) required. Underwriting is based on your expected crop cashflow, AGMARKNET market prices, and FPO 3-peer social guarantee.",
    voicePrompt: "Namaste Ramesh ji! Tell us which crop you are cultivating and your land area to calculate your approved credit limit.",
    voiceBtn: "Speak Crop Details",
    calcBtn: "Calculate Transparent Credit Sizing",
    voiceSpoken: "Your credit limit is calculated as rupees 1 lakh 2 thousand based on 1.5 acres of tomato cultivation in Nashik and your 3-peer FPO circle. Interest rate is 9 percent with harvest-synchronized bullet repayment."
  },
  hi: {
    heading: "सीमांत किसानों हेतु बिना जमीन बंधक रखे पारदर्शी संस्थागत ऋण",
    lead: "बिना जमीन के पट्टे (सातबारा) के केवल अपनी फसल उत्पादन क्षमता, मंडी भाव एवं 3-साथी FPO गारंटी के आधार पर 9.0% – 10.5% ब्याज पर ऋण पाएं।",
    voicePrompt: "नमस्ते रमेश जी! अपनी फसल का नाम और जमीन का रकबा बताएं, हम 72 घंटे में पारदर्शी ऋण सीमा तय करेंगे।",
    voiceBtn: "आवाज़ में बोलें (Voice)",
    calcBtn: "पारदर्शी ऋण सीमा की गणना करें",
    voiceSpoken: "रमेश जी, नासिक में 1.5 एकड़ टमाटर की फसल और आपकी 3-साथी FPO गारंटी पर आपकी स्वीकृत ऋण सीमा ₹1,02,400 है। ब्याज दर केवल 9% है जिसे फसल कटाई के बाद चुकाना है।"
  },
  mr: {
    heading: "अल्पभूधारक शेतकऱ्यांसाठी सातबारा व तारणाशिवाय संस्थागत कृषी पतपुरवठा",
    lead: "जमिनीच्या सातबारा/तारणाशिवाय, केवळ पीक उत्पादन व ३-शेतकरी हमीच्या बळावर ९.०% – १०.५% दराने कर्ज मिळवा.",
    voicePrompt: "नमस्कार रमेशजी! आपण कोणत्या पिकाची लागवड करत आहात व किती एकर क्षेत्र आहे ते सांगा.",
    voiceBtn: "व्हॉईसने बोला",
    calcBtn: "पारदर्शक पत मर्यादा मोजा",
    voiceSpoken: "रमेशजी, १.५ एकर टोमॅटो पिकासाठी आणि ३-शेतकरी सह्याद्री हमीच्या आधारे तुमची कर्ज मर्यादा ₹१,०२,४०० मंजूर झाली आहे."
  },
  te: {
    heading: "చిన్న, సన్నకారు రైతుల కోసం భూమి పట్టా లేకుండా సంస్థాగత రుణం",
    lead: "భూమి పట్టాదారు పాస్ పుస్తకం లేకుండా, పంట దిగుబడి మరియు 3-రైతుల పరస్పర హాमीతో 9.0% – 10.5% వడ్డీకే సంస్థాగత రుణం పొందండి.",
    voicePrompt: "నమస్కారం రమేష్ గారు! మీరు ఏ పంట వేస్తున్నారు మరియు ఎంత విస్తీర్ణమో చెప్పండి.",
    voiceBtn: "వాయిస్ ప్రారంభించండి",
    calcBtn: "రుణ పరిమితిని లెక్కించండి",
    voiceSpoken: "రమేష్ గారు, మీ పంట అంచనా మరియు ఎఫ్‌పీఓ 3-రైతుల గ్రూప్ ఆధారంగా మీ రుణ పరిమితి ₹1,02,400 గా నిర్ణయించబడింది."
  },
  ta: {
    heading: "குறு, சிறு விவசாயிகளுக்கான நில ஆவணம் இல்லா நிறுவன கடன்",
    lead: "நில ஆவணங்கள் இன்றி, பயிர் வருவாய் மற்றும் 3-விவசாயிகள் சமூக உத்தரவாதத்தின் அடிப்படையில் 9.0% – 10.5% வட்டிக்கு கடன் பெறுங்கள்.",
    voicePrompt: "வணக்கம் ரமேஷ் அவர்களே! பயிர் பெயர் மற்றும் நிலப்பரப்பை கூறுங்கள்.",
    voiceBtn: "குரல் வழி தொடங்கு",
    calcBtn: "கடன் வரம்பைக் கணக்கிடு",
    voiceSpoken: "ரமேஷ் அவர்களே, உங்கள் தக்காளி பயிர் மற்றும் எஃப்.பி.ஓ உத்தரவாதத்தின் அடிப்படையில் ₹1,02,400 கடன் அங்கீகரிக்கப்பட்டுள்ளது."
  },
  bn: {
    heading: "প্রান্তিক কৃষকদের জন্য বন্ধকহীন প্রাতিষ্ঠানিক কৃষি ঋণ",
    lead: "জমির দলিল ছাড়াই ফসল আয় এবং ৩-সদস্য FPO সামাজিক গ্যারান্টির ভিত্তিতে ৯.০% – ১০.৫% সুদে প্রাতিষ্ঠানিক ঋণ নিন।",
    voicePrompt: "নমস্কার রমেশ বাবু! আপনার ফসলের নাম ও জমির পরিমাণ বলুন।",
    voiceBtn: "ভয়েস শুরু করুন",
    calcBtn: "ঋণ সীমা হিসাব করুন",
    voiceSpoken: "রমेश বাবু, ১.৫ একর টমেটো এবং ৩-সদস্য FPO দলের ভিত্তিতে আপনার অনুমোদিত ঋণ সীমা ₹১,০২,৪০০।"
  },
  gu: {
    heading: "સીમાંત ખેડૂતો માટે જમીન ગીરો રાખ્યા વગર પારદર્શક સંસ્થાકીય ધિરાણ",
    lead: "જમીનના સાત-બાર વગર, ફક્ત પાક ઉત્પાદન ક્ષમતા, મંડી ભાવ અને ૩-ખેડૂત FPO ગેરંટી પર ૯.૦% – ૧૦.૫% વ્યાજે ધિરાણ મેળવો.",
    voicePrompt: "નમસ્તે રમેશભાઈ! તમારા પાકનું નામ અને જમીનનો વિસ્તાર જણાવો, અમે ૭૨ કલાકમાં ધિરાણ મર્યાદા નક્કી કરીશું.",
    voiceBtn: "અવાજમાં બોલો (Voice)",
    calcBtn: "ધિરાણ મર્યાદા ગણો",
    voiceSpoken: "રમેશભાઈ, નાસિકમાં ૧.૫ એકર ટામેટાં અને તમારી ૩-ખેડૂત ગેરંટી પર ₹૧,૦૨,૪૦૦ ની ધિરાણ મર્યાદા મંજૂર થઈ છે."
  },
  pa: {
    heading: "ਸੀਮਾਂਤ ਕਿਸਾਨਾਂ ਲਈ ਬਿਨਾਂ ਜ਼ਮੀਨ ਗਹਿਣੇ ਰੱਖੇ ਪਾਰਦਰਸ਼ੀ ਸੰਸਥਾਗਤ ਕਰਜ਼ਾ",
    lead: "ਜ਼ਮੀਨ ਦੀ ਫ਼ਰਦ ਤੋਂ ਬਿਨਾਂ, ਸਿਰਫ਼ ਫ਼ਸਲ ਉਤਪਾਦਨ ਸਮਰੱਥਾ, ਮੰਡੀ ਭਾਅ ਅਤੇ 3-ਕਿਸਾਨ ਗਾਰੰਟੀ ਦੇ ਆਧਾਰ 'ਤੇ 9.0% – 10.5% ਵਿਆਜ 'ਤੇ ਕਰਜ਼ਾ ਲਵੋ।",
    voicePrompt: "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਰਮੇਸ਼ ਜੀ! ਆਪਣੀ ਫ਼ਸਲ ਦਾ ਨਾਮ ਅਤੇ ਜ਼ਮੀਨ ਦਾ ਰਕਬਾ ਦੱਸੋ।",
    voiceBtn: "ਆਵਾਜ਼ ਵਿੱਚ ਬੋਲੋ",
    calcBtn: "ਕਰਜ਼ਾ ਸੀਮਾ ਗਿਣੋ",
    voiceSpoken: "ਰਮੇਸ਼ ਜੀ, 1.5 ਏਕੜ ਟਮਾਟਰ ਦੀ ਫ਼ਸਲ ਅਤੇ 3-ਕਿਸਾਨ ਗਾਰੰਟੀ 'ਤੇ ਤੁਹਾਡੀ ਮਨਜ਼ੂਰਸ਼ੁਦਾ ਕਰਜ਼ਾ ਸੀਮਾ ₹1,02,400 ਹੈ।"
  },
  kn: {
    heading: "ಸಣ್ಣ ಮತ್ತು ಅಲ್ಪಭೂಧಾರಕ ರೈತರಿಗೆ ಭೂಮಿ ಅಡಮಾನವಿಲ್ಲದೆ ಪಾರದರ್ಶಕ ಸಾಲ ಸೌಲಭ್ಯ",
    lead: "ಪಹಣಿ/ಆಸ್ತಿ ಪತ್ರಗಳಿಲ್ಲದೆ, ಕೇವಲ ಬೆಳೆ ಇಳುವರಿ ಮತ್ತು 3-ರೈತರ ಪರಸ್ಪರ ಭದ್ರತೆಯ ಆಧಾರದ ಮೇಲೆ 9.0% – 10.5% ಬಡ್ಡಿ ದರದಲ್ಲಿ ಸಾಲ ಪಡೆಯಿರಿ.",
    voicePrompt: "ನಮಸ್ಕಾರ ರಮೇಶ್ ಅವರೇ! ನಿಮ್ಮ ಬೆಳೆಯ ಹೆಸರು ಮತ್ತು ಜಮೀನಿನ ವಿಸ್ತೀರ್ಣವನ್ನು ತಿಳಿಸಿ.",
    voiceBtn: "ಧ್ವನಿಯಲ್ಲಿ ಮಾತನಾಡಿ",
    calcBtn: "ಸಾಲದ ಮಿತಿ ಲೆಕ್ಕಹಾಕಿ",
    voiceSpoken: "ರಮೇಶ್ ಅವರೇ, 1.5 ಎಕರೆ ಟೊಮೆಟೊ ಬೆಳೆ ಮತ್ತು 3-ರೈತರ ಖಾತರಿಯ ಆಧಾರದ ಮೇಲೆ ನಿಮ್ಮ ಸಾಲದ ಮಿತಿ ₹1,02,400 ಆಗಿದೆ."
  }
};

let currentLang = "en";
let radarChartInstance = null;
let currentProfile = null;

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initLanguageSwitcher();
  initThemeToggle();
  initFarmerForm();
  initVoiceSimulator();
  initPresetButtons();
  initFpoPeerInspector();
  initBankDesk();
  initDatasetFilters();
  initModalHandlers();

  // Try fetching live datasets and FPO pools from local API if available
  fetchLiveDatasets();
  fetchLiveFpoData();

  // Initial calculation
  calculateCreditProfile();
});

// Tab Navigation
function initTabs() {
  const tabs = document.querySelectorAll(".nav-tab");
  const views = document.querySelectorAll(".tab-view");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");
      
      tabs.forEach(t => t.classList.remove("active"));
      views.forEach(v => v.classList.remove("active"));

      tab.classList.add("active");
      const targetView = document.getElementById(targetId);
      if (targetView) targetView.classList.add("active");

      if (targetId === "tab-bank" && currentProfile) {
        updateRadarChart(currentProfile);
      }
    });
  });
}

// Language Switcher
function initLanguageSwitcher() {
  const select = document.getElementById("select-language");
  if (!select) return;

  select.addEventListener("change", (e) => {
    currentLang = e.target.value;
    const t = TRANSLATIONS[currentLang] || TRANSLATIONS.en;
    
    document.getElementById("lbl-farmer-heading").innerText = t.heading;
    document.getElementById("lbl-farmer-lead").innerText = t.lead;
    document.getElementById("txt-voice-msg").innerText = `"${t.voicePrompt}"`;
    document.getElementById("lbl-voice-btn").innerText = t.voiceBtn;
    document.getElementById("btn-calc-credit").innerHTML = `<i class="fa-solid fa-calculator"></i> ${t.calcBtn}`;
  });
}

// Theme Toggle
function initThemeToggle() {
  const btn = document.getElementById("theme-btn");
  if (!btn) return;

  btn.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");
    document.body.classList.toggle("light-theme");
    const isDark = document.body.classList.contains("dark-theme");
    btn.innerHTML = isDark ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    
    if (currentProfile) {
      updateRadarChart(currentProfile);
    }
  });
}

// Form & Sliders
function initFarmerForm() {
  const slider = document.getElementById("slider-land-acres");
  const valLabel = document.getElementById("lbl-acres-val");

  slider.addEventListener("input", (e) => {
    valLabel.innerText = `${e.target.value} Acres`;
    calculateCreditProfile();
  });

  const triggerElements = [
    "input-farmer-village",
    "select-mandi-district",
    "select-crop",
    "input-crop-yield",
    "input-crop-costs",
    "select-irrigation",
    "select-peer-count",
    "chk-pmkisan-verify",
    "chk-pmfby-enroll"
  ];

  triggerElements.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", calculateCreditProfile);
      if (el.tagName === "INPUT") el.addEventListener("input", calculateCreditProfile);
    }
  });

  document.getElementById("btn-calc-credit").addEventListener("click", calculateCreditProfile);

  // Consent toggle
  const consentBtn = document.getElementById("btn-consent-toggle");
  let consentActive = true;
  consentBtn.addEventListener("click", () => {
    consentActive = !consentActive;
    if (consentActive) {
      consentBtn.innerHTML = '<i class="fa-solid fa-lock-open"></i> Consent Active (72h)';
      consentBtn.classList.remove("btn-secondary");
      consentBtn.classList.add("btn-outline");
    } else {
      consentBtn.innerHTML = '<i class="fa-solid fa-lock"></i> Revoked / Private';
      consentBtn.classList.remove("btn-outline");
      consentBtn.classList.add("btn-secondary");
    }
  });
}

// Core Calculation Engine
function calculateCreditProfile() {
  const name = document.getElementById("input-farmer-name").value;
  const locArr = document.getElementById("select-mandi-district").value.split("_");
  const state = locArr[0];
  const district = locArr[1];
  const crop = document.getElementById("select-crop").value;
  const acres = parseFloat(document.getElementById("slider-land-acres").value);
  const irrigation = document.getElementById("select-irrigation").value;
  const peerCount = parseInt(document.getElementById("select-peer-count").value);
  const isPmkisan = document.getElementById("chk-pmkisan-verify").checked;
  const isPmfby = document.getElementById("chk-pmfby-enroll").checked;

  // 1. NHB Norms
  const nhbRecord = DEFAULT_NHB.find(c => c.crop.toLowerCase().includes(crop.toLowerCase())) || DEFAULT_NHB[0];
  let irrigationMultiplier = 1.0;
  if (irrigation === "Drip") irrigationMultiplier = nhbRecord.drip_boost || 1.18;
  else if (irrigation === "Rainfed") irrigationMultiplier = 0.85;

  const yieldInputEl = document.getElementById("input-crop-yield");
  const costsInputEl = document.getElementById("input-crop-costs");
  const customYield = yieldInputEl && parseFloat(yieldInputEl.value) > 0 ? parseFloat(yieldInputEl.value) : null;
  const customCosts = costsInputEl && parseFloat(costsInputEl.value) > 0 ? parseFloat(costsInputEl.value) : null;

  const yieldPerAcre = customYield !== null ? customYield : (Math.round(nhbRecord.avg_yield * irrigationMultiplier * 10) / 10);
  const totalExpectedYield = Math.round(acres * yieldPerAcre * 10) / 10;
  const cultivationCost = customCosts !== null ? Math.round(customCosts) : Math.round(acres * nhbRecord.cost_acre);

  // 2. AGMARKNET Modal Price
  const mandiRecord = DEFAULT_AGMARKNET.find(m => m.commodity.toLowerCase().includes(crop.toLowerCase()) && m.district === district) ||
                      DEFAULT_AGMARKNET.find(m => m.commodity.toLowerCase().includes(crop.toLowerCase())) ||
                      { modal_price: 2000, market: `${district} APMC`, trend: "+5.0%", peak: "Post-Harvest" };

  const modalPrice = mandiRecord.modal_price;
  const grossRevenue = Math.round(totalExpectedYield * modalPrice);
  const netHarvestProfit = Math.max(0, grossRevenue - cultivationCost);

  // 3. Base Formula: Credit Limit = 0.45 * Net Profit
  const baseCreditLimit = Math.round(netHarvestProfit * 0.45);

  // 4. Social Collateral & Risk Adjustments
  let fpoFactor = 1.08;
  let fpoScore = 24.5;
  if (peerCount === 2) { fpoFactor = 1.00; fpoScore = 20.0; }
  else if (peerCount === 1) { fpoFactor = 0.90; fpoScore = 15.0; }

  const pmfbyFactor = isPmfby ? 1.02 : 0.95;
  const pmfbyScore = isPmfby ? 18.5 : 14.0;
  const govtScore = isPmkisan ? 19.5 : 12.0;

  const dscr = Math.round((grossRevenue / (cultivationCost + 1)) * 100) / 100;
  const cashflowScore = dscr >= 2.5 ? 35.0 : (dscr >= 2.0 ? 32.0 : (dscr >= 1.5 ? 28.0 : 20.0));

  const totalScore = Math.round(cashflowScore + fpoScore + govtScore + pmfbyScore);

  let finalApprovedLimit = Math.round(baseCreditLimit * fpoFactor * pmfbyFactor);
  finalApprovedLimit = Math.max(15000, Math.min(finalApprovedLimit, 250000));

  let interestRate = 9.0;
  let ratingGrade = "Grade AAA Prime";
  if (totalScore < 85 && totalScore >= 75) { interestRate = 9.8; ratingGrade = "Grade AA Strong"; }
  else if (totalScore < 75) { interestRate = 10.5; ratingGrade = "Grade A Standard"; }

  const interestSavings = Math.round(finalApprovedLimit * 0.38 * (nhbRecord.days / 365));

  // Tranches Sizing
  const t1 = Math.round(finalApprovedLimit * 0.40);
  const t2 = Math.round(finalApprovedLimit * 0.35);
  const t3 = finalApprovedLimit - t1 - t2;

  // DID Generation
  const didHash = Math.abs(hashString(name + district + crop + acres)).toString(16).padEnd(14, '0').slice(0, 14);
  const didIdentifier = `did:kisan:ind:${didHash}`;

  // Update UI Elements
  document.getElementById("txt-credit-limit").innerText = `₹ ${finalApprovedLimit.toLocaleString('en-IN')}`;
  document.getElementById("txt-trust-score").innerText = totalScore;
  document.getElementById("badge-credit-grade").innerText = ratingGrade;

  document.getElementById("calc-step-yield").innerText = `${acres} Ac × ${yieldPerAcre} Qtl/Ac = ${totalExpectedYield} Quintals`;
  document.getElementById("calc-step-revenue").innerText = `${totalExpectedYield} Qtl × ₹${modalPrice.toLocaleString('en-IN')} = ₹ ${grossRevenue.toLocaleString('en-IN')}`;
  document.getElementById("calc-step-cost").innerText = `- ₹ ${cultivationCost.toLocaleString('en-IN')} (₹${nhbRecord.cost_acre.toLocaleString('en-IN')} / Acre)`;
  document.getElementById("calc-step-profit").innerText = `= ₹ ${netHarvestProfit.toLocaleString('en-IN')}`;
  document.getElementById("calc-step-base").innerText = `0.45 × ₹${netHarvestProfit.toLocaleString('en-IN')} = ₹ ${baseCreditLimit.toLocaleString('en-IN')}`;
  document.getElementById("calc-step-fpo").innerText = `× ${fpoFactor} (${peerCount}-Peer Guarantee Factor)`;

  document.getElementById("txt-interest-rate").innerText = `${interestRate}% p.a.`;
  document.getElementById("txt-interest-savings").innerText = `₹ ${interestSavings.toLocaleString('en-IN')}`;
  document.getElementById("txt-did-identifier").innerText = didIdentifier;
  document.getElementById("bank-active-did").innerText = didIdentifier;

  // Populate Tranches Card
  const tranchesContainer = document.getElementById("container-tranches");
  tranchesContainer.innerHTML = `
    <div class="tranche-item">
      <div class="tranche-kicker">Tranche 1 (40%)</div>
      <div class="tranche-val">₹ ${t1.toLocaleString('en-IN')}</div>
      <div class="tranche-purpose">Seeds & Sowing</div>
    </div>
    <div class="tranche-item">
      <div class="tranche-kicker">Tranche 2 (35%)</div>
      <div class="tranche-val">₹ ${t2.toLocaleString('en-IN')}</div>
      <div class="tranche-purpose">Nutrients & Drip</div>
    </div>
    <div class="tranche-item">
      <div class="tranche-kicker">Tranche 3 (25%)</div>
      <div class="tranche-val">₹ ${t3.toLocaleString('en-IN')}</div>
      <div class="tranche-purpose">Harvest & Logistics</div>
    </div>
  `;

  // Store active profile
  currentProfile = {
    name,
    crop,
    district,
    state,
    acres,
    finalApprovedLimit,
    totalScore,
    interestRate,
    ratingGrade,
    cashflowScore,
    fpoScore,
    govtScore,
    pmfbyScore,
    dscr,
    modalPrice,
    didIdentifier,
    tranche1: t1,
    tranche2: t2,
    tranche3: t3
  };

  // Sync Bank Desk components
  document.getElementById("prog-txt-cashflow").innerText = `${cashflowScore} / 35`;
  document.getElementById("prog-txt-fpo").innerText = `${fpoScore} / 25`;
  document.getElementById("prog-txt-govt").innerText = `${govtScore} / 20`;
  document.getElementById("prog-txt-risk").innerText = `${pmfbyScore} / 20`;

  document.getElementById("prog-bar-cashflow").style.width = `${(cashflowScore / 35) * 100}%`;
  document.getElementById("prog-bar-fpo").style.width = `${(fpoScore / 25) * 100}%`;
  document.getElementById("prog-bar-govt").style.width = `${(govtScore / 20) * 100}%`;
  document.getElementById("prog-bar-risk").style.width = `${(pmfbyScore / 20) * 100}%`;

  document.getElementById("bank-sanction-amount").innerText = `₹ ${finalApprovedLimit.toLocaleString('en-IN')}`;

  // Update bank queue table
  populateBankQueueTable();
}

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return hash;
}

// Voice Assistant Simulator & Web Speech API
// Web Speech API: Live Speech Recognition & Natural Language Extraction
let recognitionInstance = null;
const userManuallyEditedFields = new Set();
let pendingVoiceConflicts = null;
let currentFollowupField = null;
let lastSummarySpokenText = "";

function speakUtterance(text, langCode) {
  if (!('speechSynthesis' in window)) return;
  try {
    window.speechSynthesis.cancel();
    window.speechSynthesis.resume();
    const cleanText = text.replace(/₹\s*([0-9,]+)/g, "$1 rupees ").replace(/•/g, ", ").trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    
    const voices = window.speechSynthesis.getVoices() || [];
    const targetPrefix = (langCode || currentLang || "hi").substring(0, 2);
    const matchedVoice = voices.find(v => (v.lang || "").toLowerCase().startsWith(targetPrefix));
    if (matchedVoice) {
      utterance.voice = matchedVoice;
      utterance.lang = matchedVoice.lang;
    } else {
      utterance.lang = targetPrefix === "hi" ? "hi-IN" : "en-IN";
    }
    window._activeUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  } catch (e) {
    console.warn("TTS speakUtterance error:", e);
  }
}

function initVoiceSimulator() {
  const micBtn = document.getElementById("btn-voice-mic");
  const triggerBtn = document.getElementById("btn-trigger-voice");
  const summaryBtn = document.getElementById("btn-speak-summary");
  const titleEl = document.getElementById("txt-voice-title");
  const msgEl = document.getElementById("txt-voice-msg");
  const recordingBanner = document.getElementById("voice-recording-indicator");
  const stopVoiceBtn = document.getElementById("btn-stop-voice");

  // Optional Typed Speech Input Fallback
  const typedInput = document.getElementById("input-spoken-transcript");
  const parseBtn = document.getElementById("btn-parse-spoken-text");
  if (parseBtn && typedInput) {
    parseBtn.addEventListener("click", () => {
      const text = typedInput.value.trim();
      if (text) {
        processVoiceTranscript(text);
      }
    });
    typedInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const text = typedInput.value.trim();
        if (text) {
          processVoiceTranscript(text);
        }
      }
    });
  }

  // Confirmation Summary Action Buttons
  const confirmBtn = document.getElementById("btn-voice-confirm");
  const recordAgainBtn = document.getElementById("btn-voice-record-again");
  const editFormBtn = document.getElementById("btn-voice-edit-form");
  const listenSummaryBtn = document.getElementById("btn-voice-listen-summary");

  if (confirmBtn) {
    confirmBtn.addEventListener("click", () => {
      if (titleEl) titleEl.innerText = "✅ Details Confirmed by Farmer";
      if (msgEl) msgEl.innerText = "Your information has been verified. You can now click 'Calculate Transparent Credit Sizing' below whenever you are ready.";
      const calcBtn = document.getElementById("btn-calc-credit");
      if (calcBtn) {
        calcBtn.scrollIntoView({ behavior: "smooth", block: "center" });
        calcBtn.classList.add("voice-updated-highlight");
        setTimeout(() => calcBtn.classList.remove("voice-updated-highlight"), 3000);
      }
    });
  }

  if (recordAgainBtn) {
    recordAgainBtn.addEventListener("click", () => {
      const confirmCard = document.getElementById("voice-confirmation-card");
      if (confirmCard) confirmCard.style.display = "none";
      const followupCard = document.getElementById("voice-followup-card");
      if (followupCard) followupCard.style.display = "none";
      const conflictBanner = document.getElementById("voice-conflict-banner");
      if (conflictBanner) conflictBanner.style.display = "none";
      startLiveVoiceRecognition();
    });
  }

  if (editFormBtn) {
    editFormBtn.addEventListener("click", () => {
      const firstInput = document.getElementById("input-farmer-name");
      if (firstInput) {
        firstInput.scrollIntoView({ behavior: "smooth", block: "center" });
        firstInput.focus();
      }
    });
  }

  if (listenSummaryBtn) {
    listenSummaryBtn.addEventListener("click", () => {
      if (lastSummarySpokenText) {
        speakUtterance(lastSummarySpokenText, currentLang);
      }
    });
  }

  // Follow-up Question Actions
  const answerFollowupBtn = document.getElementById("btn-answer-followup-voice");
  const listenFollowupBtn = document.getElementById("btn-listen-followup");
  if (answerFollowupBtn) {
    answerFollowupBtn.addEventListener("click", () => {
      if (currentFollowupField) {
        startLiveVoiceRecognition(currentFollowupField);
      }
    });
  }
  if (listenFollowupBtn) {
    listenFollowupBtn.addEventListener("click", () => {
      const qEl = document.getElementById("txt-followup-question");
      if (qEl && qEl.innerText) {
        speakUtterance(qEl.innerText, currentLang);
      }
    });
  }

  // Conflict Resolution Buttons
  const acceptConflictsBtn = document.getElementById("btn-accept-voice-conflicts");
  const rejectConflictsBtn = document.getElementById("btn-reject-voice-conflicts");
  if (acceptConflictsBtn) {
    acceptConflictsBtn.addEventListener("click", () => {
      if (pendingVoiceConflicts && pendingVoiceConflicts.conflicts) {
        const acceptedLabels = [];
        for (const [key, conf] of Object.entries(pendingVoiceConflicts.conflicts)) {
          setFormFieldValue(key, conf.spoken);
          acceptedLabels.push(formatFieldLabel(key));
        }
        const banner = document.getElementById("voice-conflict-banner");
        if (banner) banner.style.display = "none";
        pendingVoiceConflicts = null;
      }
    });
  }

  if (rejectConflictsBtn) {
    rejectConflictsBtn.addEventListener("click", () => {
      const banner = document.getElementById("voice-conflict-banner");
      if (banner) banner.style.display = "none";
      pendingVoiceConflicts = null;
    });
  }

  // Track user manual changes so voice does not silently overwrite them
  const trackableFieldIds = [
    "input-farmer-name",
    "input-farmer-phone",
    "input-farmer-village",
    "select-mandi-district",
    "select-crop",
    "slider-land-acres",
    "input-crop-yield",
    "input-crop-costs",
    "select-irrigation"
  ];
  trackableFieldIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("change", () => userManuallyEditedFields.add(id));
      el.addEventListener("input", () => userManuallyEditedFields.add(id));
    }
  });

  // Check if browser supports Web Speech API Recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
  const startLiveVoiceRecognition = (targetMissingField = null) => {
    currentFollowupField = targetMissingField;
    if (micBtn) micBtn.classList.add("listening");
    if (triggerBtn) triggerBtn.classList.add("listening");
    if (recordingBanner) recordingBanner.style.display = "flex";
    
    if (targetMissingField) {
      if (titleEl) titleEl.innerText = `🎙️ Listening for ${formatFieldLabel(targetMissingField)}...`;
      if (msgEl) msgEl.innerText = "बोलिए, हम आपकी आवाज़ रिकॉर्ड कर रहे हैं...";
    } else {
      if (titleEl) titleEl.innerText = "🎙️ Listening... Speak your crop, land area, yield & costs";
      if (msgEl) msgEl.innerText = `Microphone active in ${currentLang.toUpperCase()} - speak in Hindi or regional language...`;
    }

    if (SpeechRecognition) {
      try {
        if (recognitionInstance) {
          recognitionInstance.abort();
        }
        recognitionInstance = new SpeechRecognition();
        const langMap = {
          en: "en-IN",
          hi: "hi-IN",
          gu: "gu-IN",
          mr: "mr-IN",
          te: "te-IN",
          ta: "ta-IN",
          bn: "bn-IN",
          pa: "pa-IN",
          kn: "kn-IN"
        };
        recognitionInstance.lang = langMap[currentLang] || "hi-IN";
        recognitionInstance.interimResults = true;
        recognitionInstance.maxAlternatives = 1;

        recognitionInstance.onresult = (event) => {
          const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join("");
          
          if (msgEl) msgEl.innerText = `"${transcript}"`;

          if (event.results[0].isFinal) {
            if (recordingBanner) recordingBanner.style.display = "none";
            if (micBtn) micBtn.classList.remove("listening");
            if (triggerBtn) triggerBtn.classList.remove("listening");
            // Automatically process transcript and populate fields! (No copy/paste or manual button required)
            processVoiceTranscript(transcript, targetMissingField);
          }
        };

        recognitionInstance.onerror = (event) => {
          console.warn("Speech Recognition error / permission denied:", event.error);
          if (recordingBanner) recordingBanner.style.display = "none";
          if (micBtn) micBtn.classList.remove("listening");
          if (triggerBtn) triggerBtn.classList.remove("listening");
          if (titleEl) titleEl.innerText = "⚠️ Microphone Inactive";
          if (msgEl) msgEl.innerText = `Microphone could not be accessed (${event.error || "denied"}). You can type your sentence in the transcript box below.`;
          const detailsEl = document.getElementById("transcript-details");
          if (detailsEl) detailsEl.open = true;
        };

        recognitionInstance.onend = () => {
          if (recordingBanner) recordingBanner.style.display = "none";
          if (micBtn) micBtn.classList.remove("listening");
          if (triggerBtn) triggerBtn.classList.remove("listening");
        };

        recognitionInstance.start();
        return;
      } catch (err) {
        console.warn("SpeechRecognition start failed:", err);
      }
    }
    
    // Browser does not support Web Speech API
    if (recordingBanner) recordingBanner.style.display = "none";
    if (micBtn) micBtn.classList.remove("listening");
    if (triggerBtn) triggerBtn.classList.remove("listening");
    if (titleEl) titleEl.innerText = "ℹ️ Microphone API Not Supported";
    if (msgEl) msgEl.innerText = "Your browser does not support live microphone recognition. You can type in the transcript box below.";
    const detailsEl = document.getElementById("transcript-details");
    if (detailsEl) detailsEl.open = true;
  };

  if (stopVoiceBtn) {
    stopVoiceBtn.addEventListener("click", () => {
      if (recognitionInstance) {
        recognitionInstance.stop();
      }
      if (recordingBanner) recordingBanner.style.display = "none";
      if (micBtn) micBtn.classList.remove("listening");
      if (triggerBtn) triggerBtn.classList.remove("listening");
    });
  }

  if (micBtn) micBtn.addEventListener("click", () => startLiveVoiceRecognition());
  if (triggerBtn) triggerBtn.addEventListener("click", () => startLiveVoiceRecognition());
  if (summaryBtn) summaryBtn.addEventListener("click", speakTextSummary);
}

function getFieldElementId(key) {
  const map = {
    name: "input-farmer-name",
    farmer_name: "input-farmer-name",
    phone: "input-farmer-phone",
    village: "input-farmer-village",
    district: "select-mandi-district",
    crop: "select-crop",
    acres: "slider-land-acres",
    yield: "input-crop-yield",
    yield_quintals: "input-crop-yield",
    projected_yield: "input-crop-yield",
    costs: "input-crop-costs",
    input_costs: "input-crop-costs",
    irrigation: "select-irrigation"
  };
  return map[key] || null;
}

function formatFieldLabel(key) {
  const map = {
    name: "Farmer Name",
    farmer_name: "Farmer Name",
    phone: "Mobile Number",
    village: "Village",
    district: "State & APMC District",
    crop: "Cultivated Crop",
    acres: "Land Acreage",
    yield: "Expected Yield (Qtl/Ac)",
    yield_quintals: "Expected Yield (Qtl/Ac)",
    projected_yield: "Expected Yield (Qtl/Ac)",
    costs: "Input Expenses (₹)",
    input_costs: "Input Expenses (₹)",
    irrigation: "Irrigation Facility"
  };
  return map[key] || key;
}

function highlightField(inputEl, badgeId) {
  if (inputEl) {
    inputEl.classList.add("voice-updated-highlight");
  }
  if (badgeId) {
    const badge = document.getElementById(badgeId);
    if (badge) {
      badge.style.display = "inline-flex";
    }
  }
}

function setFormFieldValue(key, val) {
  if (val === null || val === undefined || val === "") return false;
  
  if (key === "name" || key === "farmer_name") {
    const el = document.getElementById("input-farmer-name");
    if (el) {
      el.value = val;
      highlightField(el, "badge-voice-name");
      return true;
    }
  } else if (key === "phone") {
    const el = document.getElementById("input-farmer-phone");
    if (el) {
      el.value = val;
      highlightField(el, "badge-voice-phone");
      return true;
    }
  } else if (key === "village") {
    const el = document.getElementById("input-farmer-village");
    if (el) {
      el.value = val;
      highlightField(el, "badge-voice-village");
      return true;
    }
  } else if (key === "crop") {
    const el = document.getElementById("select-crop");
    if (el) {
      let matched = false;
      const lowerVal = val.toString().toLowerCase();
      for (let opt of el.options) {
        if (opt.value.toLowerCase() === lowerVal || opt.text.toLowerCase().includes(lowerVal) || lowerVal.includes(opt.value.toLowerCase())) {
          el.value = opt.value;
          matched = true;
          break;
        }
      }
      if (!matched) {
        el.value = "Tomato";
      }
      highlightField(el, "badge-voice-crop");
      return true;
    }
  } else if (key === "acres") {
    const el = document.getElementById("slider-land-acres");
    const num = parseFloat(val);
    if (el && !isNaN(num)) {
      const clamped = Math.min(2.5, Math.max(0.5, num));
      el.value = clamped.toString();
      const lbl = document.getElementById("lbl-acres-val");
      if (lbl) lbl.innerText = `${clamped} Acres`;
      highlightField(el, "badge-voice-acres");
      return true;
    }
  } else if (key === "yield" || key === "yield_quintals" || key === "projected_yield") {
    const el = document.getElementById("input-crop-yield");
    const num = parseFloat(val);
    if (el && !isNaN(num)) {
      el.value = num;
      highlightField(el, "badge-voice-yield");
      return true;
    }
  } else if (key === "costs" || key === "input_costs") {
    const el = document.getElementById("input-crop-costs");
    const num = parseFloat(val);
    if (el && !isNaN(num)) {
      el.value = num;
      highlightField(el, "badge-voice-costs");
      return true;
    }
  } else if (key === "district") {
    const el = document.getElementById("select-mandi-district");
    if (el) {
      const lower = val.toString().toLowerCase();
      for (let opt of el.options) {
        if (opt.value.toLowerCase().includes(lower) || opt.text.toLowerCase().includes(lower)) {
          el.value = opt.value;
          break;
        }
      }
      highlightField(el, "badge-voice-district");
      return true;
    }
  } else if (key === "irrigation") {
    const el = document.getElementById("select-irrigation");
    if (el) {
      for (let opt of el.options) {
        if (opt.value.toLowerCase() === val.toString().toLowerCase()) {
          el.value = opt.value;
          break;
        }
      }
      highlightField(el, "badge-voice-irrigation");
      return true;
    }
  }
  return false;
}

function normalizeSpokenNumbersInText(text) {
  let res = text;
  // Multi-word thousands in Hindi and English
  res = res.replace(/(?:चौबीस|24)\s*(?:हज़ार|हजार|thousand)/gi, "24000");
  res = res.replace(/(?:अठारह|18)\s*(?:हज़ार|हजार|thousand)/gi, "18000");
  res = res.replace(/(?:बीस|20)\s*(?:हज़ार|हजार|thousand)/gi, "20000");
  res = res.replace(/(?:पच्चीस|25)\s*(?:हज़ार|हजार|thousand)/gi, "25000");
  res = res.replace(/(?:तीस|30)\s*(?:हज़ार|हजार|thousand)/gi, "30000");
  res = res.replace(/(?:चालीस|40)\s*(?:हज़ार|हजार|thousand)/gi, "40000");
  res = res.replace(/(?:पचास|50)\s*(?:हज़ार|हजार|thousand)/gi, "50000");
  res = res.replace(/(?:एक|1)\s*(?:लाख|lakh)/gi, "100000");
  res = res.replace(/(?:दो|2)\s*(?:लाख|lakh)/gi, "200000");
  res = res.replace(/twenty\s*four\s*thousand/gi, "24000");
  res = res.replace(/eighteen\s*thousand/gi, "18000");
  res = res.replace(/twenty\s*thousand/gi, "20000");
  res = res.replace(/twenty\s*five\s*thousand/gi, "25000");
  res = res.replace(/thirty\s*thousand/gi, "30000");
  res = res.replace(/forty\s*thousand/gi, "40000");
  res = res.replace(/fifty\s*thousand/gi, "50000");

  // Single number words before units
  res = res.replace(/(?:दो|two)\s+(?=एकड़|acres?)/gi, "2 ");
  res = res.replace(/(?:एक|one)\s+(?=एकड़|acres?)/gi, "1 ");
  res = res.replace(/(?:तीन|three)\s+(?=एकड़|acres?)/gi, "3 ");
  res = res.replace(/(?:डेढ़|dedh|one\s+and\s+a\s+half)\s+(?=एकड़|acres?)/gi, "1.5 ");
  res = res.replace(/(?:ढाई|dhai|two\s+and\s+a\s+half)\s+(?=एकड़|acres?)/gi, "2.5 ");
  res = res.replace(/(?:आधा|half)\s+(?=एकड़|acres?)/gi, "0.5 ");

  res = res.replace(/(?:अठारह|eighteen)\s+(?=क्विंटल|quintals?|qtl)/gi, "18 ");
  res = res.replace(/(?:बीस|twenty)\s+(?=क्विंटल|quintals?|qtl)/gi, "20 ");
  res = res.replace(/(?:पंद्रह|fifteen)\s+(?=क्विंटल|quintals?|qtl)/gi, "15 ");
  res = res.replace(/(?:दस|ten)\s+(?=क्विंटल|quintals?|qtl)/gi, "10 ");
  res = res.replace(/(?:बारह|twelve)\s+(?=क्विंटल|quintals?|qtl)/gi, "12 ");

  return res;
}

/// Client-side fallback NLP parser for offline / direct browser use
function clientSideVoiceParser(text, currentData, targetMissingField = null) {
  // Normalize Indic digits across 8 regional scripts
  let norm = text.replace(/[\u0660-\u0669\u06F0-\u06F9\u0966-\u096F\u09E6-\u09EF\u0A66-\u0A6F\u0AE6-\u0AEF\u0B66-\u0B6F\u0BE6-\u0BEF\u0C66-\u0C6F\u0CE6-\u0CEF]/g, d => d.charCodeAt(0) & 0xf);
  norm = normalizeSpokenNumbersInText(norm);
  const lower = norm.toLowerCase();
  const extracted = {};

  // Farmer Name
  const namePatterns = [
    /(?:mera\s+naam|मेरा\s+नाम|माझे\s+नाव|મારું\s+નામ|నా\s+పేరు|என்\s+பெயர்|my\s+name\s+is)\s+([A-Za-z\u0900-\u0D7F\s\.]+?)(?:है|हूँ|आहे|છે|\.|,|।|मेरे|गाँव|गाव|village|district|acres|जमीन|phone|मोबाइल|$)/i
  ];
  for (const p of namePatterns) {
    const m = norm.match(p);
    if (m && m[1].trim().length >= 2) {
      extracted.farmer_name = m[1].trim();
      extracted.name = extracted.farmer_name;
      break;
    }
  }

  // Phone Number (continuous digits starting with 6-9 or prefixed by phone keyword)
  const phoneMatch = norm.match(/(?:phone|mobile|नंबर|मोबाईल|నంబర్|फोन|फ़ोन|मोबाइल|ఫోన్|மொபைல்)\s*[:\s]?\b([6-9]\d{7,11})\b/i) || norm.match(/\b([6-9]\d{8,11})\b/);
  if (phoneMatch) {
    extracted.phone = phoneMatch[1];
  }

  // Village
  const villagePatterns = [
    /(?:गाँव|गांव|गाव|गावात|ग्राम|village|gaon)\s+([A-Za-z\u0900-\u0D7F]+)/i,
    /([A-Za-z\u0900-\u0D7F]+)\s*(?:गाँव से|गांव से|गावातून|village)/i,
    /(?:in|at)\s+([A-Za-z]+),\s*(?:[A-Za-z]+)/i,
    /(?:from|at)\s+([A-Za-z]+)\s+village/i
  ];
  for (const vp of villagePatterns) {
    const m = norm.match(vp);
    if (m && m[1].trim().length >= 2) {
      const v = m[1].trim();
      if (!["se", "mein", "hai", "district", "acres", "acre", "land", "cultivating", "growing"].includes(v.toLowerCase())) {
        extracted.village = v;
        break;
      }
    }
  }

  // Crop detection
  const crops = [
    { name: "Tomato", matches: ["tomato", "tamatar", "टमाटर", "ટામેટા", "टोमॅटो", "టమాటా", "தக்காளி"] },
    { name: "Onion", matches: ["onion", "pyaz", "kanda", "कांदा", "ડુંગળી", "ఉల్లిపాయ", "வெங்காயம்"] },
    { name: "Chilli (Dry)", matches: ["chilli", "mirchi", "chili", "मिर्च", "મરચાં", "మిర్చి", "மிளகாய்"] },
    { name: "Potato", matches: ["potato", "aloo", "बटाटा", "आलू", "બટાકા", "బంగాళाదుంప", "உருளைக்கிழங்கு"] },
    { name: "Grapes", matches: ["grapes", "angoor", "द्राक्ष", "દ્રાક્ષ", "திராட்சை"] },
    { name: "Turmeric", matches: ["turmeric", "haldi", "हळद", "હળદર", "மஞ்சள்"] },
    { name: "Wheat", matches: ["wheat", "gehun", "गेहूं", "ਕਣਕ"] },
    { name: "Soybean", matches: ["soybean", "soya", "सोयाबीन"] },
    { name: "Cotton", matches: ["cotton", "kapas", "कपास", "कापूस", "పత్తి"] },
    { name: "Maize", matches: ["maize", "makka", "मक्का", "मका", "మొక్కಜೊన్న"] }
  ];
  for (const c of crops) {
    if (c.matches.some(m => lower.includes(m))) {
      extracted.crop = c.name;
      break;
    }
  }

  // Acres detection with numeric and Hindi word support
  const hindiWordAcres = [
    [/आधा/i, 0.5], [/डेढ़|देढ़/i, 1.5], [/ढाई/i, 2.5],
    [/एक/i, 1.0], [/दो/i, 2.0], [/तीन/i, 3.0]
  ];
  let acreFound = null;
  const acreNumMatch = norm.match(/(\d+(?:\.\d+)?)\s*(?:acres?|acre|एकड़|એકર|एकर|ఎకరాలు|ஏக்கர்|एकड़ जमीन)/i);
  if (acreNumMatch) {
    acreFound = parseFloat(acreNumMatch[1]);
  } else {
    for (const [p, val] of hindiWordAcres) {
      if (p.test(norm)) {
        acreFound = val;
        break;
      }
    }
  }
  if (acreFound !== null && acreFound >= 0.1 && acreFound <= 20.0) {
    extracted.acres = acreFound;
  }

  // Yield detection (e.g. Expected 15 quintals per acre yield)
  const yieldMatch = norm.match(/(?:expecting|expected|yield|उपज|उत्पादन|पैदावार)\s*(?:is|of|are)?\s*(\d+(?:\.\d+)?)\s*(?:quintals?|qtl|क्विंटल)?/i) ||
                     norm.match(/(\d+(?:\.\d+)?)\s*(?:quintals?|qtl|क्विंटल)\s*(?:per\s+acre\s+yield|प्रति\s+एकड़|उपज|yield)?/i) ||
                     norm.match(/(\d+(?:\.\d+)?)\s*(?:quintals?|qtl|क्विंटल)/i);
  if (yieldMatch) {
    const yVal = parseFloat(yieldMatch[1]);
    extracted.yield_quintals = yVal;
    extracted.yield = yVal;
    extracted.projected_yield = yVal;
  }

  // Costs / Input Expenses detection (e.g. total input expenses are 3000 rupees)
  const costMatch = norm.match(/(?:expenses?|costs?|खर्च|लागत|खर्चा)\s*(?:are|is|of)?\s*(?:rupees?|rs\.?|₹)?\s*(\d+)/i) ||
                    norm.match(/(\d+)\s*(?:rupees|रुपये|रु|₹)\s*(?:total\s+input\s+expenses?|expenses?|costs?|खर्च|लागत)?/i) ||
                    norm.match(/(?:₹|rs\.?)\s*(\d+)/i) ||
                    norm.match(/(\d+)\s*(?:रुपये|rupees)/i);
  if (costMatch) {
    const cVal = parseFloat(costMatch[1]);
    if (cVal >= 500) {
      extracted.input_costs = cVal;
      extracted.costs = cVal;
    }
  }

  // District detection
  if (lower.includes("kolar") || lower.includes("कोलार") || lower.includes("ಕೋಲಾರ")) {
    extracted.district = "Karnataka_Kolar";
  } else if (lower.includes("guntur") || lower.includes("गुंटूर") || lower.includes("గుంటూరు")) {
    extracted.district = "Andhra Pradesh_Guntur";
  } else if (lower.includes("agra") || lower.includes("आगरा")) {
    extracted.district = "Uttar Pradesh_Agra";
  } else if (lower.includes("salem") || lower.includes("सेलम") || lower.includes("சேலம்")) {
    extracted.district = "Tamil Nadu_Salem";
  } else if (lower.includes("indore") || lower.includes("इंदौर")) {
    extracted.district = "Madhya Pradesh_Indore";
  } else if (lower.includes("nashik") || lower.includes("नासिक") || lower.includes("नाशिक") || lower.includes("pimpalgaon") || lower.includes("रामपुर") || lower.includes("rampur")) {
    extracted.district = "Maharashtra_Nashik";
  }

  // Irrigation detection
  if (lower.includes("drip") || lower.includes("ड्रिप") || lower.includes("ઠિબક") || lower.includes("డ్రిప్")) {
    extracted.irrigation = "Drip";
  } else if (lower.includes("rain") || lower.includes("बारिश") || lower.includes("વરસાદ") || lower.includes("rainfed")) {
    extracted.irrigation = "Rainfed";
  } else if (lower.includes("canal") || lower.includes("नहर")) {
    extracted.irrigation = "Canal";
  }

  // Target Field Fallbacks when answering a specific follow-up question
  if (targetMissingField) {
    if ((targetMissingField === "yield" || targetMissingField === "yield_quintals") && !extracted.yield) {
      const loneNum = norm.match(/(\d+(?:\.\d+)?)/);
      if (loneNum) {
        const v = parseFloat(loneNum[1]);
        extracted.yield = v;
        extracted.yield_quintals = v;
        extracted.projected_yield = v;
      }
    } else if ((targetMissingField === "costs" || targetMissingField === "input_costs") && !extracted.costs) {
      const loneNum = norm.match(/(\d{3,7})/);
      if (loneNum) {
        const v = parseFloat(loneNum[1]);
        extracted.costs = v;
        extracted.input_costs = v;
      }
    } else if (targetMissingField === "acres" && !extracted.acres) {
      const loneNum = norm.match(/(\d+(?:\.\d+)?)/);
      if (loneNum) {
        extracted.acres = parseFloat(loneNum[1]);
      }
    } else if (targetMissingField === "phone" && !extracted.phone) {
      const pNum = norm.match(/([6-9]\d{7,11})/) || norm.match(/(\d{8,12})/);
      if (pNum) {
        extracted.phone = pNum[1];
      }
    } else if ((targetMissingField === "name" || targetMissingField === "farmer_name") && !extracted.name) {
      const cleanName = norm.replace(/^(?:my name is|मेरा नाम|माझे नाव|नाम)\s*/i, "").trim();
      if (cleanName.length >= 2) {
        extracted.name = cleanName;
        extracted.farmer_name = cleanName;
      }
    } else if (targetMissingField === "village" && !extracted.village) {
      const cleanVillage = norm.replace(/^(?:village|गाँव|गाव|ग्राम|from|in)\s*/i, "").trim();
      if (cleanVillage.length >= 2) {
        extracted.village = cleanVillage;
      }
    }
  }

  // Detect proposed changes / conflicts against currentData using float tolerance
  const proposed = {};
  if (currentData) {
    for (const [k, v] of Object.entries(extracted)) {
      if (currentData[k] !== undefined && currentData[k] !== null && currentData[k] !== "") {
        const cVal = currentData[k];
        const numC = parseFloat(cVal);
        const numV = parseFloat(v);
        let differs = false;
        if (!isNaN(numC) && !isNaN(numV)) {
          differs = Math.abs(numC - numV) > 0.05;
        } else {
          differs = cVal.toString().trim().toLowerCase() !== v.toString().trim().toLowerCase();
        }
        if (differs) {
          proposed[k] = { current: cVal, spoken: v };
        }
      }
    }
  }

  // Generate client-side confirmation summary
  const summaryParts = [];
  const nameVal = extracted.name || extracted.farmer_name;
  if (nameVal) summaryParts.push(`Name: ${nameVal}`);
  if (extracted.phone) summaryParts.push(`Phone: ${extracted.phone}`);
  if (extracted.crop) summaryParts.push(`Crop: ${extracted.crop}`);
  if (extracted.acres) summaryParts.push(`Land: ${extracted.acres} Acre${extracted.acres > 1 ? 's' : ''}`);
  if (extracted.village) summaryParts.push(`Village: ${extracted.village}`);
  if (extracted.district) summaryParts.push(`District: ${extracted.district}`);
  if (extracted.yield || extracted.yield_quintals) summaryParts.push(`Yield: ${extracted.yield || extracted.yield_quintals} Qtl/Ac`);
  if (extracted.costs || extracted.input_costs) summaryParts.push(`Expenses: ₹${Number(extracted.costs || extracted.input_costs).toLocaleString('en-IN')}`);
  const summaryText = summaryParts.length > 0 ? summaryParts.join(" • ") : "No details recognized.";

  // Missing fields check for single follow-up question
  const requiredKeys = ["name", "phone", "village", "district", "crop", "acres", "yield", "costs"];
  const missing = [];
  for (const k of requiredKeys) {
    if (k === "yield") {
      const hasYield = (extracted.yield || extracted.yield_quintals || extracted.projected_yield) ||
                       (currentData && (currentData.yield || currentData.yield_quintals || currentData.projected_yield));
      if (!hasYield) missing.push("yield");
    } else if (k === "costs") {
      const hasCosts = (extracted.costs || extracted.input_costs) ||
                       (currentData && (currentData.costs || currentData.input_costs));
      if (!hasCosts) missing.push("costs");
    } else {
      const val = extracted[k] || (currentData ? currentData[k] : null);
      if (!val) missing.push(k);
    }
  }

  let followup = null;
  if (missing.length > 0) {
    const followupMap = {
      name: { en: "Please speak the farmer's full name.", hi: "कृपया किसान का पूरा नाम बोलकर बताएं।" },
      phone: { en: "Please speak your mobile number.", hi: "कृपया अपना मोबाइल नंबर बोलकर बताएं।" },
      village: { en: "Please speak your village name.", hi: "कृपया अपने गाँव का नाम बोलकर बताएं।" },
      district: { en: "In which district is your farm located?", hi: "आपका खेत किस जिले में है?" },
      crop: { en: "Which crop are you cultivating this season?", hi: "कृपया बताएं कि आप कौन सी फसल उगा रहे हैं?" },
      acres: { en: "How many acres of land are you cultivating?", hi: "आपके पास कितने एकड़ कृषि भूमि है?" },
      yield: { en: "What is your expected yield per acre in quintals?", hi: "प्रति एकड़ आपकी अनुमानित पैदावार कितने क्विंटल है?" },
      costs: { en: "What are your total input cultivation expenses in rupees?", hi: "खाद, बीज और मजदूरी में कुल कितना खर्च आया है?" }
    };
    const firstMissing = missing[0];
    const qObj = followupMap[firstMissing] || { en: `Please provide ${firstMissing}.`, hi: `कृपया ${firstMissing} बताएं।` };
    const qText = (typeof currentLang !== "undefined" && currentLang === "hi") ? qObj.hi : qObj.en;
    followup = {
      field: firstMissing,
      question: qText,
      field_label: formatFieldLabel(firstMissing)
    };
  }

  return {
    raw_transcript: text,
    extracted_fields: extracted,
    mapped_fields: extracted,
    proposed_changes: proposed,
    confirmation_summary: summaryText,
    followup_question: followup,
    missing_fields: missing
  };
}

// Master Voice Transcript Processor
async function processVoiceTranscript(transcript, targetMissingField = null) {
  if (!transcript || !transcript.trim()) return;

  const titleEl = document.getElementById("txt-voice-title");
  const msgEl = document.getElementById("txt-voice-msg");
  const typedInput = document.getElementById("input-spoken-transcript");

  if (titleEl) titleEl.innerText = "🗣️ Voice Transcript Captured:";
  if (msgEl) msgEl.innerText = `"${transcript}"`;
  if (typedInput) typedInput.value = transcript;

  // Gather current form data for conflict detection and field retention
  const currentData = {
    name: document.getElementById("input-farmer-name") ? document.getElementById("input-farmer-name").value.trim() : "",
    farmer_name: document.getElementById("input-farmer-name") ? document.getElementById("input-farmer-name").value.trim() : "",
    phone: document.getElementById("input-farmer-phone") ? document.getElementById("input-farmer-phone").value.trim() : "",
    village: document.getElementById("input-farmer-village") ? document.getElementById("input-farmer-village").value.trim() : "",
    crop: document.getElementById("select-crop") ? document.getElementById("select-crop").value : "",
    acres: document.getElementById("slider-land-acres") ? parseFloat(document.getElementById("slider-land-acres").value) : 1.5,
    district: document.getElementById("select-mandi-district") ? document.getElementById("select-mandi-district").value : "",
    yield: document.getElementById("input-crop-yield") ? parseFloat(document.getElementById("input-crop-yield").value) : 18.0,
    yield_quintals: document.getElementById("input-crop-yield") ? parseFloat(document.getElementById("input-crop-yield").value) : 18.0,
    costs: document.getElementById("input-crop-costs") ? parseFloat(document.getElementById("input-crop-costs").value) : 24000.0,
    input_costs: document.getElementById("input-crop-costs") ? parseFloat(document.getElementById("input-crop-costs").value) : 24000.0,
    irrigation: document.getElementById("select-irrigation") ? document.getElementById("select-irrigation").value : ""
  };

  let parseResult = null;

  // Attempt backend API call first
  try {
    const parseUrl = API_BASE_URL ? `${API_BASE_URL}/api/v1/voice/parse` : "/api/v1/voice/parse";
    const resp = await fetch(parseUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        transcript: transcript,
        lang_code: currentLang || "hi",
        current_data: currentData,
        target_field: targetMissingField || currentFollowupField || null
      })
    });
    if (resp.ok) {
      parseResult = await resp.json();
    }
  } catch (err) {
    console.info("Using resilient local NLP parser (backend unavailable):", err);
  }

  if (!parseResult) {
    parseResult = clientSideVoiceParser(transcript, currentData, targetMissingField || currentFollowupField);
  }

  applyVoiceParsingResult(parseResult, transcript);
}

function applyVoiceParsingResult(data, transcript) {
  const extracted = data.extracted_fields || data.mapped_fields || {};
  const conflicts = data.proposed_changes || {};

  const conflictBanner = document.getElementById("voice-conflict-banner");
  const conflictList = document.getElementById("voice-conflict-list");
  const statusAlert = document.getElementById("voice-status-alert");
  const statusText = document.getElementById("voice-status-text");
  const confirmCard = document.getElementById("voice-confirmation-card");
  const summaryTextEl = document.getElementById("voice-summary-text");
  const followupCard = document.getElementById("voice-followup-card");
  const followupQuestionEl = document.getElementById("txt-followup-question");

  // Only present conflict if user had manually entered a value that conflicts
  const realConflicts = {};
  for (const [k, conf] of Object.entries(conflicts)) {
    const fieldId = getFieldElementId(k);
    if (fieldId && userManuallyEditedFields.has(fieldId)) {
      realConflicts[k] = conf;
    }
  }

  const conflictKeys = Object.keys(realConflicts);
  if (conflictKeys.length > 0) {
    pendingVoiceConflicts = { conflicts: realConflicts, extracted: extracted };
    if (conflictBanner && conflictList) {
      conflictList.innerHTML = conflictKeys.map(k => {
        return `<div style="margin-bottom: 2px;">• <strong>${formatFieldLabel(k)}:</strong> Current manual value: <code>${realConflicts[k].current}</code> ➔ Spoken voice value: <code>${realConflicts[k].spoken}</code></div>`;
      }).join("");
      conflictBanner.style.display = "block";
    }
  } else {
    if (conflictBanner) conflictBanner.style.display = "none";
  }

  // Populate non-conflicting extracted fields directly into the visible form
  const updatedLabels = [];
  for (const [k, v] of Object.entries(extracted)) {
    if (!realConflicts[k]) {
      const success = setFormFieldValue(k, v);
      if (success) {
        updatedLabels.push(formatFieldLabel(k));
      }
    }
  }

  // Update Confirmation Summary Card (Farmer Review)
  let summary = data.confirmation_summary || "";
  if (!summary) {
    const summaryParts = [];
    const nameVal = extracted.name || extracted.farmer_name;
    if (nameVal) summaryParts.push(`Name: ${nameVal}`);
    if (extracted.phone) summaryParts.push(`Phone: ${extracted.phone}`);
    if (extracted.crop) summaryParts.push(`Crop: ${extracted.crop}`);
    if (extracted.acres) summaryParts.push(`Land: ${extracted.acres} Acre${extracted.acres > 1 ? 's' : ''}`);
    if (extracted.village) summaryParts.push(`Village: ${extracted.village}`);
    if (extracted.district) summaryParts.push(`District: ${extracted.district}`);
    if (extracted.yield || extracted.yield_quintals || extracted.projected_yield) {
      summaryParts.push(`Yield: ${extracted.yield || extracted.yield_quintals || extracted.projected_yield} Qtl/Ac`);
    }
    if (extracted.costs || extracted.input_costs) {
      summaryParts.push(`Expenses: ₹${Number(extracted.costs || extracted.input_costs).toLocaleString('en-IN')}`);
    }
    summary = summaryParts.join(" • ");
  }

  if (summary && summaryTextEl && confirmCard) {
    summaryTextEl.innerText = summary;
    confirmCard.style.display = "block";
    lastSummarySpokenText = summary;
  }

  // Handle single follow-up question if any required fields are missing
  if (data.followup_question && data.followup_question.question && followupCard && followupQuestionEl) {
    currentFollowupField = data.followup_question.field;
    followupQuestionEl.innerText = data.followup_question.question;
    followupCard.style.display = "block";
    // Speak the single targeted follow-up question aloud
    speakUtterance(data.followup_question.question, currentLang);
  } else {
    currentFollowupField = null;
    if (followupCard) followupCard.style.display = "none";
    // When all required fields are complete, speak the confirmation summary aloud
    if (summary) {
      speakUtterance(summary, currentLang);
    }
  }

  // Display status banner for farmer review (DO NOT auto-submit or auto-calculate!)
  if (updatedLabels.length > 0 && statusAlert && statusText) {
    statusText.innerText = `🎙️ ${updatedLabels.length} field(s) populated from voice: [${updatedLabels.join(", ")}]. Please review your inputs and click 'Confirm & Continue' or 'Calculate Transparent Credit Sizing' to submit.`;
    statusAlert.style.display = "block";
  }
}

function speakTextSummary() {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  window.speechSynthesis.resume();

  const name = currentProfile ? currentProfile.name : "Ramesh Patil";
  const limit = currentProfile ? `₹ ${currentProfile.finalApprovedLimit.toLocaleString('en-IN')}` : "₹ 1,02,400";
  const rate = currentProfile ? `${currentProfile.interestRate}%` : "9.0%";
  const crop = currentProfile ? currentProfile.crop : "Tomato";
  const acres = currentProfile ? currentProfile.acres : 1.5;
  const dist = currentProfile ? currentProfile.district : "Nashik";

  const dynamicSpeechMapNative = {
    en: `Namaste ${name}! Based on your ${acres} acres of ${crop} in ${dist} and 3-peer FPO circle, your sanctioned credit limit is ${limit} at ${rate} annual interest with harvest bullet repayment.`,
    hi: `नमस्ते ${name} जी! ${dist} में आपकी ${acres} एकड़ ${crop} की फसल और FPO गारंटी के आधार पर, आपकी स्वीकृत ऋण सीमा ${limit} तय की गई है, जिस पर ${rate} ब्याज दर है।`,
    gu: `નમસ્તે ${name}ભાઈ! ${dist} માં તમારી ${acres} એકર ${crop} ની ખેતી અને FPO ગેરંટી પર તમારી મંજૂર થયેલ ધિરાણ મર્યાદા ${limit} છે, ${rate} વ્યાજ દરે.`,
    mr: `नमस्कार ${name}जी! ${dist} मध्ये आपली ${acres} एकर ${crop} लागवड आणि ३-शेतकरी हमीवर आपली मंजूर कर्ज मर्यादा ${limit} असून ${rate} सवलतीचा व्याज दर आहे.`,
    te: `నమస్కారం ${name} గారు! ${dist} లో మీ ${acres} ఎకరాల ${crop} పంట మరియు ఎఫ్‌పీఓ గ్రూప్ ఆధారంగా మీ ఆమోదిత రుణ పరిమితి ${limit}, ${rate} వడ్డీ రేటుతో.`,
    ta: `வணக்கம் ${name} அவர்களே! ${dist} இல் உங்கள் ${acres} ஏக்கர் ${crop} பயிர் அடிப்படையில், உங்கள் அங்கீகரிக்கப்பட்ட கடன் வரம்பு ${limit}, ${rate} வட்டி விகிதத்தில்.`,
    bn: `নমস্কার ${name} বাবু! ${dist} এ আপনার ${acres} একর ${crop} এবং FPO দলের ভিত্তিতে আপনার অনুমোদিত ঋণ সীমা ${limit}, ${rate} সুদে।`,
    pa: `ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ ${name} ਜੀ! ${dist} ਵਿੱਚ ਤੁਹਾਡੀ ${acres} ਏਕੜ ${crop} ਫ਼ਸਲ ਲਈ ਪ੍ਰਵਾਨਿਤ ਕਰਜ਼ਾ ਸੀਮਾ ${limit} ਹੈ, ${rate} ਵਿਆਜ ਦਰ 'ਤੇ।`,
    kn: `ನಮಸ್ಕಾರ ${name} ಅವರೇ! ${dist} ನಲ್ಲಿ ನಿಮ್ಮ ${acres} ಎಕರೆ ${crop} ಬೆಳೆಗೆ ಅನುಮೋದಿತ ಸಾಲದ ಮಿತಿ ${limit} ಆಗಿದೆ, ${rate} ಬಡ್ಡಿದರದಲ್ಲಿ.`
  };

  const dynamicSpeechMapPhonetic = {
    en: `Namaste ${name}! Based on your ${acres} acres of ${crop} in ${dist} and 3-peer FPO circle, your sanctioned credit limit is ${limit} at ${rate} annual interest with harvest bullet repayment.`,
    hi: `Namaste ${name} ji! ${dist} mein aapki ${acres} acre ${crop} ki fasal aur FPO guarantee ke aadhar par, aapki manzoor rin seema ${limit} tay ki gayi hai, jis par ${rate} byaj dar hai.`,
    gu: `Namaste ${name} bhai! ${dist} ma tamari ${acres} ekar ${crop} ni kheti ane FPO guarantee aadhare, tamari manjoor dhee-ran maryada ${limit} chhe, ${rate} vyaj dare.`,
    mr: `Namaskar ${name} ji! ${dist} madhye aapli ${acres} acre ${crop} lagwad aani teen shetkari hami var aapli manzoor karza maryada ${limit} asun ${rate} vyaj dar aahe.`,
    te: `Namaskaram ${name} garu! ${dist} lo mee ${acres} ekarala ${crop} panta mariyu FPO group aadharamga mee aamodhitha runa parimithi ${limit}, ${rate} vaddi rethotho.`,
    ta: `Vanakkam ${name} avargale! ${dist} il ungal ${acres} acre ${crop} payir adipadayil, ungal angeekarikka patta kadan varambu ${limit}, ${rate} vatti vigithathil.`,
    bn: `Nomoshkar ${name} babu! ${dist} e aponar ${acres} acre ${crop} ebong FPO doler bhittite aponar anumodito rin seema ${limit}, ${rate} sude.`,
    pa: `Sat Sri Akal ${name} ji! ${dist} vich tuhadi ${acres} acre ${crop} fasal layi approved karza limit ${limit} hai, ${rate} vyaj dar te.`,
    kn: `Namaskara ${name} avare! ${dist} nalli nimma ${acres} acre ${crop} belege matthu FPO group aadharadalli nimma anumoditha saalada mithi ${limit}, ${rate} baddi daradalli.`
  };

  const langConfig = {
    en: { code: "en-IN", keywords: ["en-in", "en_in", "english", "india", "en-us"] },
    hi: { code: "hi-IN", keywords: ["hi-in", "hi_in", "hindi", "हिन्दी", "kalpana", "hemant", "google हिन्दी"] },
    gu: { code: "gu-IN", keywords: ["gu-in", "gu_in", "gujarati", "ગુજરાતી", "dhwani"] },
    mr: { code: "mr-IN", keywords: ["mr-in", "mr_in", "marathi", "मराठी", "aarohi"] },
    te: { code: "te-IN", keywords: ["te-in", "te_in", "telugu", "తెలుగు", "mohan"] },
    ta: { code: "ta-IN", keywords: ["ta-in", "ta_in", "tamil", "தமிழ்", "valluvar"] },
    bn: { code: "bn-IN", keywords: ["bn-in", "bn_in", "bengali", "বাংলা", "bangla", "bashkar"] },
    pa: { code: "pa-IN", keywords: ["pa-in", "pa_in", "punjabi", "ਪੰਜਾਬੀ", "panjabi"] },
    kn: { code: "kn-IN", keywords: ["kn-in", "kn_in", "kannada", "ಕನ್ನಡ", "gagan"] }
  };

  const cfg = langConfig[currentLang] || langConfig.en;
  const nativeText = dynamicSpeechMapNative[currentLang] || dynamicSpeechMapNative.en;
  const phoneticText = dynamicSpeechMapPhonetic[currentLang] || dynamicSpeechMapPhonetic.en;

  const playSpeech = () => {
    const voices = window.speechSynthesis.getVoices() || [];
    let chosenVoice = null;
    let textToSpeak = nativeText;
    let targetLang = cfg.code;

    if (voices.length > 0) {
      // 1. Exact match for regional language
      chosenVoice = voices.find(v => {
        const vl = (v.lang || "").toLowerCase().replace("_", "-");
        const vn = (v.name || "").toLowerCase();
        return vl.startsWith(currentLang) || cfg.keywords.some(k => vl.includes(k) || vn.includes(k));
      });

      // 2. If no exact voice, check if Hindi voice can speak Hindi/Marathi
      if (!chosenVoice && (currentLang === 'hi' || currentLang === 'mr')) {
        chosenVoice = voices.find(v => {
          const vl = (v.lang || "").toLowerCase();
          const vn = (v.name || "").toLowerCase();
          return vl.startsWith("hi") || vn.includes("hindi") || vn.includes("हिन्दी");
        });
      }

      // 3. If still no regional voice, use phonetic transliteration with Indian English / default voice
      if (!chosenVoice) {
        textToSpeak = phoneticText;
        chosenVoice = voices.find(v => {
          const vl = (v.lang || "").toLowerCase();
          const vn = (v.name || "").toLowerCase();
          return vl.includes("in") || vn.includes("india") || vn.includes("hindi") || vl.startsWith("en");
        }) || voices.find(v => v.default) || voices[0];
        targetLang = chosenVoice ? chosenVoice.lang : "en-IN";
      }
    } else {
      textToSpeak = (currentLang === 'en' || currentLang === 'hi') ? nativeText : phoneticText;
      targetLang = (currentLang === 'hi') ? "hi-IN" : "en-IN";
    }

    const cleanText = textToSpeak.replace(/₹\s*([0-9,]+)/g, "$1 rupees ").trim();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.rate = 0.92;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = targetLang;
    if (chosenVoice) {
      utterance.voice = chosenVoice;
    }

    utterance.onerror = () => {
      try {
        const fallbackUtterance = new SpeechSynthesisUtterance(phoneticText.replace(/₹\s*([0-9,]+)/g, "$1 rupees "));
        fallbackUtterance.rate = 0.92;
        fallbackUtterance.lang = "en-IN";
        window._activeUtterance = fallbackUtterance;
        window.speechSynthesis.speak(fallbackUtterance);
      } catch (e) {}
    };

    utterance.onend = () => {
      window._activeUtterance = null;
    };

    window._activeUtterance = utterance;
    window.speechSynthesis.speak(utterance);
  };

  if (window.speechSynthesis.getVoices().length === 0) {
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.onvoiceschanged = null;
      playSpeech();
    };
    setTimeout(playSpeech, 100);
  } else {
    playSpeech();
  }
}

function initPresetButtons() {
  const chips = document.querySelectorAll(".chip");
  const presetUtterances = {
    tomato_nashik: "मेरा नाम रमेश पाटिल है। मैं गाँव पिंपलगांव नासिक से हूँ। मेरे पास 1.5 एकड़ जमीन है और मैं टमाटर उगाता हूँ। ड्रिप सिंचाई है।",
    chilli_guntur: "నా పేరు సాంబ రావు. గుంటూరులో 2 ఎకరాల మిర్చి సాగు చేస్తున్నాను, డ్రిప్ ఇరిగేషన్.",
    potato_agra: "मेरा नाम राम नरेश है। आगरा में 2.2 एकड़ आलू की फसल है और नहर से सिंचाई है।",
    turmeric_salem: "என் பெயர் முருகன். சேலத்தில் 1.8 ஏக்கர் மஞ்சள் பயிரிடுகிறேன், சொட்டு நீர் பாசனம்.",
    onion_lasalgaon: "माझे नाव सुरेश जाधव आहे। नाशिक लासलगाव येथे 1.2 एकर कांदा पीक आहे। ठिबक सिंचन आहे।"
  };

  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const preset = chip.getAttribute("data-preset");
      const utterance = presetUtterances[preset];
      if (utterance) {
        processVoiceTranscript(utterance);
      }
    });
  });
}

// FPO 3-Peer Circle Interactive Inspector
function initFpoPeerInspector() {
  const peerCards = document.querySelectorAll(".peer-node-card");
  peerCards.forEach(card => {
    card.addEventListener("click", () => {
      peerCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      const peerId = parseInt(card.getAttribute("data-peer"));
      activeSelectedPeer = peerId;
      updatePeerInspectorDisplay(peerId);
    });
  });

  const toggleVerifyBtn = document.getElementById("btn-toggle-peer-verify");
  toggleVerifyBtn.addEventListener("click", () => {
    const peer = PEER_MEMBERS[activeSelectedPeer];
    if (peer) {
      peer.verified = !peer.verified;
      updatePeerInspectorDisplay(activeSelectedPeer);
    }
  });

  const endorseBtn = document.getElementById("btn-endorse-circle");
  endorseBtn.addEventListener("click", () => {
    alert("3-Peer Guarantee Circle #48 has been formally verified and signed by FPO Coordinator for institutional credit disbursal.");
  });

  // Search input for circles
  const searchInput = document.getElementById("input-search-circles");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase();
      const rows = document.querySelectorAll("#table-fpo-circles tbody tr");
      rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(query) ? "" : "none";
      });
    });
  }
}

function updatePeerInspectorDisplay(peerId) {
  const peer = PEER_MEMBERS[peerId];
  if (!peer) return;

  document.getElementById("inspector-name").innerText = `${peer.name} (${peer.role})`;
  document.getElementById("inspector-loc").innerText = peer.location;
  document.getElementById("inspector-crop").innerText = peer.crop;
  document.getElementById("inspector-irrigation").innerText = peer.irrigation;
  document.getElementById("inspector-history").innerText = peer.history;
  document.getElementById("inspector-pmkisan").innerText = peer.pmkisan;

  const statusEl = document.getElementById("inspector-status");
  if (peer.verified) {
    statusEl.className = "status-badge status-success";
    statusEl.innerHTML = '<i class="fa-solid fa-check"></i> Field Verified';
  } else {
    statusEl.className = "status-badge status-warning";
    statusEl.innerHTML = '<i class="fa-solid fa-clock"></i> Verification Pending';
  }
}

window.selectCircleRow = function(name) {
  document.getElementById("tab-btn-farmer").click();
  const nameInput = document.getElementById("input-farmer-name");
  nameInput.value = name;
  calculateCreditProfile();
};

// Bank Desk Underwriting & Radar Chart
function initBankDesk() {
  const stressBtns = document.querySelectorAll(".btn-chip");
  stressBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      stressBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const shock = parseInt(btn.getAttribute("data-shock"));
      runStressTest(shock);
    });
  });

  const openDisburseBtn = document.getElementById("btn-open-disburse");
  openDisburseBtn.addEventListener("click", () => {
    if (!currentProfile) return;
    document.getElementById("receipt-farmer-name").innerText = currentProfile.name;
    document.getElementById("receipt-tranche-amt").innerText = `₹ ${currentProfile.tranche1.toLocaleString('en-IN')}`;
    document.getElementById("receipt-total-limit").innerText = `₹ ${currentProfile.finalApprovedLimit.toLocaleString('en-IN')}`;
    document.getElementById("receipt-tx-hash").innerText = `0x${hashString(Date.now().toString()).toString(16).padEnd(28, '4f')}`;
    document.getElementById("modal-disbursement").classList.add("active");
  });
}

function runStressTest(shockPct) {
  if (!currentProfile) return;
  const basePrice = currentProfile.modalPrice;
  const stressedPrice = Math.round(basePrice * (1 + shockPct / 100));
  const stressedDscr = Math.round((currentProfile.dscr * (1 + shockPct / 100)) * 100) / 100;
  
  const textEl = document.getElementById("txt-stress-output");
  if (shockPct === 0) {
    textEl.innerHTML = `Under baseline modal price (₹${basePrice}/Qtl), DSCR is <strong>${currentProfile.dscr}x</strong>. Loan is safely covered by expected harvest revenues.`;
  } else if (shockPct === -15) {
    textEl.innerHTML = `Under a <strong>-15% price shock</strong> (₹${stressedPrice}/Qtl), DSCR remains healthy at <strong class="text-success">${stressedDscr}x</strong> (> 1.5x minimum benchmark).`;
  } else {
    textEl.innerHTML = `Under extreme <strong>-30% crash</strong> (₹${stressedPrice}/Qtl), DSCR is <strong class="text-warning">${stressedDscr}x</strong>. Covered by PMFBY crop insurance and 3-peer FPO surety.`;
  }
}

function populateBankQueueTable() {
  const tbody = document.getElementById("bank-queue-tbody");
  if (!tbody || !currentProfile) return;

  tbody.innerHTML = `
    <tr style="background: var(--color-primary-subtle);">
      <td>
        <strong>${currentProfile.name}</strong><br>
        <code style="font-size: 0.7rem; color: var(--color-accent);">${currentProfile.didIdentifier}</code>
      </td>
      <td>${currentProfile.crop} (${currentProfile.acres} Ac)<br><span style="font-size:0.72rem; color: var(--text-muted);">${currentProfile.district}</span></td>
      <td><strong class="text-success">₹ ${currentProfile.finalApprovedLimit.toLocaleString('en-IN')}</strong></td>
      <td><span class="badge-score score-high">${currentProfile.totalScore} / 100</span></td>
      <td><span class="status-badge status-success">Favorable</span></td>
      <td><button class="btn btn-xs btn-primary" onclick="document.getElementById('btn-open-disburse').click()">Sanction</button></td>
    </tr>
    <tr>
      <td>
        <strong>Venkatesh Gowda</strong><br>
        <code style="font-size: 0.7rem; color: var(--color-accent);">did:kisan:ind:4a7e9102c813f5</code>
      </td>
      <td>Tomato (2.0 Ac)<br><span style="font-size:0.72rem; color: var(--text-muted);">Kolar, KA</span></td>
      <td><strong>₹ 1,32,000</strong></td>
      <td><span class="badge-score score-high">89 / 100</span></td>
      <td><span class="status-badge status-info">Standard</span></td>
      <td><button class="btn btn-xs btn-secondary" onclick="document.getElementById('btn-open-disburse').click()">Review</button></td>
    </tr>
    <tr>
      <td>
        <strong>Samba Siva Rao</strong><br>
        <code style="font-size: 0.7rem; color: var(--color-accent);">did:kisan:ind:7b3c29910d54a8</code>
      </td>
      <td>Chilli (2.2 Ac)<br><span style="font-size:0.72rem; color: var(--text-muted);">Guntur, AP</span></td>
      <td><strong>₹ 1,75,000</strong></td>
      <td><span class="badge-score score-high">94 / 100</span></td>
      <td><span class="status-badge status-success">Superior</span></td>
      <td><span class="status-badge status-info"><i class="fa-solid fa-check"></i> Disbursed</span></td>
    </tr>
  `;
}

function updateRadarChart(data) {
  const canvas = document.getElementById("chartUnderwritingRadar");
  if (!canvas) return;

  const isDark = document.body.classList.contains("dark-theme");
  const textColor = isDark ? '#94a3b8' : '#64748b';
  const gridColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)';

  if (radarChartInstance) {
    radarChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');
  radarChartInstance = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: [
        'Agri Cashflow (35)',
        '3-Peer Social Guarantee (25)',
        'PM-KISAN Verification (20)',
        'Mandi & PMFBY Stability (20)'
      ],
      datasets: [{
        label: 'Underwriting Score Components',
        data: [
          (data.cashflowScore / 35) * 100,
          (data.fpoScore / 25) * 100,
          (data.govtScore / 20) * 100,
          (data.pmfbyScore / 20) * 100
        ],
        backgroundColor: 'rgba(22, 163, 74, 0.2)',
        borderColor: '#16a34a',
        borderWidth: 2,
        pointBackgroundColor: '#16a34a',
        pointBorderColor: '#ffffff',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: gridColor },
          grid: { color: gridColor },
          pointLabels: {
            color: textColor,
            font: { size: 11, family: "'Plus Jakarta Sans', sans-serif", weight: '600' }
          },
          ticks: { display: false, max: 100, min: 0 }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

// Open Datasets Table Filters
function initDatasetFilters() {
  renderAgmarknetTable(DEFAULT_AGMARKNET);
  renderNhbTable(DEFAULT_NHB);
  renderPmfbyTable(DEFAULT_PMFBY);
  renderIcarAlerts(DEFAULT_ICAR);

  const agmarkInput = document.getElementById("input-filter-agmark");
  if (agmarkInput) {
    agmarkInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = DEFAULT_AGMARKNET.filter(r => 
        r.commodity.toLowerCase().includes(q) || r.market.toLowerCase().includes(q) || r.district.toLowerCase().includes(q)
      );
      renderAgmarknetTable(filtered);
    });
  }

  const nhbInput = document.getElementById("input-filter-nhb");
  if (nhbInput) {
    nhbInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      const filtered = DEFAULT_NHB.filter(r => r.crop.toLowerCase().includes(q) || r.category.toLowerCase().includes(q));
      renderNhbTable(filtered);
    });
  }
}

function renderAgmarknetTable(records) {
  const tbody = document.getElementById("agmarknet-tbody");
  if (!tbody) return;
  tbody.innerHTML = records.map(r => `
    <tr>
      <td><strong>${r.commodity}</strong></td>
      <td>${r.market}</td>
      <td>${r.state}</td>
      <td><strong class="text-success">₹ ${r.modal_price.toLocaleString('en-IN')}</strong></td>
      <td>${r.arrivals_tonnes} MT</td>
      <td><span class="${r.trend.startsWith('+') ? 'text-success' : 'text-danger'} font-bold">${r.trend}</span></td>
    </tr>
  `).join("");
}

function renderNhbTable(records) {
  const tbody = document.getElementById("nhb-tbody");
  if (!tbody) return;
  tbody.innerHTML = records.map(r => `
    <tr>
      <td><strong>${r.crop}</strong></td>
      <td><span class="status-badge status-info">${r.category}</span></td>
      <td><strong>${r.avg_yield}</strong> Qtl</td>
      <td>₹ ${r.cost_acre.toLocaleString('en-IN')}</td>
      <td>${r.days} Days</td>
      <td><span class="text-success font-bold">+${Math.round((r.drip_boost - 1) * 100)}%</span></td>
    </tr>
  `).join("");
}

function renderPmfbyTable(records) {
  const tbody = document.getElementById("pmfby-tbody");
  if (!tbody) return;
  tbody.innerHTML = records.map(r => `
    <tr>
      <td><strong>${r.district}</strong></td>
      <td>${r.crops}</td>
      <td>${r.loss_ratio}</td>
      <td>${r.hazard}</td>
      <td><span class="text-success font-bold">${r.risk_factor}</span></td>
    </tr>
  `).join("");
}

function renderIcarAlerts(alerts) {
  const container = document.getElementById("icar-feed-list");
  if (!container) return;
  container.innerHTML = alerts.map(a => `
    <div class="icar-alert-card">
      <div class="alert-head">
        <span><i class="fa-solid fa-triangle-exclamation"></i> ${a.crop}: ${a.disease}</span>
        <span>${a.area}</span>
      </div>
      <div class="alert-body">
        <strong>Advisory:</strong> ${a.action}
      </div>
    </div>
  `).join("");
}

// Fetch Live Datasets from server API (if available) with static fallback
function fetchLiveDatasets() {
  const datasetsUrl = API_BASE_URL ? `${API_BASE_URL}/api/datasets` : "/api/datasets";
  fetch(datasetsUrl)
    .then(res => res.json())
    .then(data => {
      if (data.agmarknet && data.agmarknet.length > 0) {
        renderAgmarknetTable(data.agmarknet);
      }
    })
    .catch(() => {
      // If deployed on GitHub Pages or static host, load local static JSON data
      fetch("data/agmarknet_data.json")
        .then(res => res.json())
        .then(data => {
          if (data && data.length > 0) {
            renderAgmarknetTable(data);
          }
        })
        .catch(() => {
          // Gracefully silent fallback to embedded default datasets
        });
    });
}

// Modal Handlers
function initModalHandlers() {
  const modal = document.getElementById("modal-disbursement");
  const closeBtn = document.getElementById("btn-close-modal");
  const doneBtn = document.getElementById("btn-modal-dismiss");
  const printBtn = document.getElementById("btn-print-sanction");

  const closeModal = () => modal.classList.remove("active");
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (doneBtn) doneBtn.addEventListener("click", closeModal);
  
  if (printBtn) {
    printBtn.addEventListener("click", () => {
      window.print();
    });
  }

  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
}

// Fetch Live FPO Groups and Unassigned Farmers from backend
function fetchLiveFpoData() {
  const fpoGroupsUrl = API_BASE_URL ? `${API_BASE_URL}/api/v1/fpo/groups` : "/api/v1/fpo/groups";
  const unassignedUrl = API_BASE_URL ? `${API_BASE_URL}/api/v1/fpo/unassigned-farmers` : "/api/v1/fpo/unassigned-farmers";

  // 1. Fetch Guarantee Groups
  fetch(fpoGroupsUrl)
    .then(res => res.json())
    .then(groups => {
      if (Array.isArray(groups) && groups.length > 0) {
        const tbody = document.querySelector("#table-fpo-circles tbody");
        if (tbody) {
          tbody.innerHTML = groups.map(g => {
            const m = g.members || [];
            const pLeader = m.find(x => x.role === "LEADER") || m[0] || { name: "Open Slot" };
            const m1 = m.filter(x => x !== pLeader)[0] || { name: "Open Slot" };
            const m2 = m.filter(x => x !== pLeader)[1] || { name: "Open Slot" };
            const isFull = g.is_full || m.length >= 3;
            const statusBadge = isFull 
              ? '<span class="status-badge status-success">Active 3/3</span>' 
              : `<span class="status-badge status-warning">Forming (${m.length}/3)</span>`;
            const avgScore = m.length > 0 ? Math.round(m.reduce((acc, x) => acc + (x.credit_score || 75), 0) / m.length) : 75;

            return `
              <tr>
                <td><code>#${g.group_code}</code></td>
                <td><strong>${pLeader.name}</strong></td>
                <td>${m1.name}</td>
                <td>${m2.name}</td>
                <td>${g.fpo_name} (₹${(g.total_pool_credit_limit || 0).toLocaleString('en-IN')})</td>
                <td><span class="text-success font-bold">${g.village}, ${g.district}</span></td>
                <td><span class="badge-score score-high">${avgScore} / 100</span></td>
                <td>${statusBadge}</td>
                <td><button class="btn btn-xs btn-outline" onclick="selectCircleRow('${pLeader.name}')">View</button></td>
              </tr>
            `;
          }).join("");
        }
      }
    })
    .catch(() => {});

  // 2. Fetch Unassigned Farmers
  fetch(unassignedUrl)
    .then(res => res.json())
    .then(farmers => {
      const tbody = document.getElementById("tbody-unassigned-farmers");
      const badge = document.getElementById("badge-unassigned-count");
      if (badge) badge.innerText = `${farmers.length} Farmers`;
      if (tbody) {
        if (!Array.isArray(farmers) || farmers.length === 0) {
          tbody.innerHTML = `<tr><td colspan="9" class="text-muted" style="text-align: center; padding: 1.5rem;">All onboarded farmers are currently assigned to active 3-member guarantee pools.</td></tr>`;
        } else {
          tbody.innerHTML = farmers.map(f => `
            <tr>
              <td><code>#FARMER-${f.farmer_id}</code></td>
              <td><strong>${f.name}</strong></td>
              <td>${f.phone}</td>
              <td>${f.village}, ${f.district}</td>
              <td>${f.fpo_name}</td>
              <td>${f.crop_name}</td>
              <td><span class="badge-score score-mid">${f.credit_score} / 100</span></td>
              <td><strong>₹ ${(f.credit_limit || 0).toLocaleString('en-IN')}</strong></td>
              <td><span class="status-badge status-warning">⏳ Awaiting Pool</span></td>
            </tr>
          `).join("");
        }
      }
    })
    .catch(() => {});
}

