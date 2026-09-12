/**
 * KisanTrust - Community-Owned Credit Network
 * Frontend Application & Underwriting Interface
 */

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

  // Try fetching live datasets from local API if available
  fetchLiveDatasets();

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
    "select-mandi-district",
    "select-crop",
    "select-irrigation",
    "select-peer-count",
    "chk-pmkisan-verify",
    "chk-pmfby-enroll"
  ];

  triggerElements.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", calculateCreditProfile);
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

  const yieldPerAcre = Math.round(nhbRecord.avg_yield * irrigationMultiplier * 10) / 10;
  const totalExpectedYield = Math.round(acres * yieldPerAcre * 10) / 10;
  const cultivationCost = Math.round(acres * nhbRecord.cost_acre);

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
// Web Speech API: Live Speech Recognition & Multi-Language Synthesis
let recognitionInstance = null;

function initVoiceSimulator() {
  const micBtn = document.getElementById("btn-voice-mic");
  const triggerBtn = document.getElementById("btn-trigger-voice");
  const summaryBtn = document.getElementById("btn-speak-summary");
  const titleEl = document.getElementById("txt-voice-title");
  const msgEl = document.getElementById("txt-voice-msg");

  // Check if browser supports Web Speech API Recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
  const startLiveVoiceRecognition = () => {
    micBtn.classList.add("listening");
    titleEl.innerText = "🎙️ Listening... Speak your crop, land area, & district now";
    msgEl.innerText = `Microphone active in ${currentLang.toUpperCase()} - (e.g. "Tomato on 2 acres in Nashik with drip irrigation")`;

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
        recognitionInstance.lang = langMap[currentLang] || "en-IN";
        recognitionInstance.interimResults = true;
        recognitionInstance.maxAlternatives = 1;

        recognitionInstance.onresult = (event) => {
          const transcript = Array.from(event.results)
            .map(result => result[0].transcript)
            .join("");
          
          msgEl.innerText = `"${transcript}"`;

          if (event.results[0].isFinal) {
            parseSpokenAgronomicInput(transcript);
          }
        };

        recognitionInstance.onerror = (event) => {
          console.warn("Speech Recognition error / permission denied, using simulation:", event.error);
          triggerFallbackSimulation();
        };

        recognitionInstance.onend = () => {
          micBtn.classList.remove("listening");
        };

        recognitionInstance.start();
        return;
      } catch (err) {
        console.warn("SpeechRecognition start failed:", err);
      }
    }
    
    // Fallback simulation if mic is unavailable or blocked in browser
    triggerFallbackSimulation();
  };

  const triggerFallbackSimulation = () => {
    micBtn.classList.add("listening");
    titleEl.innerText = "🎙️ Synthesizing Voice Input...";
    msgEl.innerText = "Recognizing spoken phonemes and extracting agronomic telemetry...";

    setTimeout(() => {
      micBtn.classList.remove("listening");
      const sample = getSampleTextForLang(currentLang);
      titleEl.innerText = "🗣️ Spoken Input Captured & Synchronized:";
      msgEl.innerText = `"${sample}"`;
      
      // Auto populate and recalculate
      document.getElementById("input-farmer-name").value = "Ramesh Tukaram Patil";
      document.getElementById("select-mandi-district").value = "Maharashtra_Nashik";
      document.getElementById("select-crop").value = "Tomato";
      document.getElementById("slider-land-acres").value = "1.5";
      document.getElementById("lbl-acres-val").innerText = "1.5 Acres";
      document.getElementById("select-irrigation").value = "Drip";
      
      calculateCreditProfile();
      speakTextSummary();
    }, 1800);
  };

  micBtn.addEventListener("click", startLiveVoiceRecognition);
  triggerBtn.addEventListener("click", startLiveVoiceRecognition);
  summaryBtn.addEventListener("click", speakTextSummary);
}

function getSampleTextForLang(lang) {
  const samples = {
    en: "Ramesh Patil: 1.5 acres of Tomato crop in Nashik with Drip Irrigation and 3-peer FPO circle.",
    hi: "नमस्ते रमेश पाटिल: नासिक में 1.5 एकड़ टमाटर की फसल, ड्रिप सिंचाई और 3-साथी गारंटी।",
    gu: "રમેશભાઈ પટેલ: નાસિકમાં ૧.૫ એકર ટામેટાં, ડ્રિપ ઇરિગેશન અને ૩-ખેડૂત ગેરંટી.",
    mr: "रमेश पाटील: नाशिकमध्ये १.५ एकर टोमॅटो पीक, ठिबक सिंचन आणि ३-शेतकरी हमी गट.",
    te: "రమేష్ పాటిల్: నాసిక్‌లో 1.5 ఎకరాల టమాటా, డ్రిప్ ఇరిగేషన్ మరియు 3-రైతుల గ్రూప్.",
    ta: "ரமேஷ் பாட்டீல்: நாசிக்கில் 1.5 ஏக்கர் தக்காளி, சொட்டு நீர் பாசனம்.",
    bn: "রমেশ পাটিল: নাসিকে ১.৫ একর টমেটো, ড্রিপ সেচ এবং ৩-সদস্যের দল।",
    pa: "ਰਮੇਸ਼ ਪਾਟਿਲ: ਨਾਸਿਕ ਵਿੱਚ 1.5 ਏਕੜ ਟਮਾਟਰ, ਤੁਪਕਾ ਸਿੰਚਾਈ।",
    kn: "ರಮೇಶ್ ಪಾಟೀಲ್: ನಾಸಿಕ್‌ನಲ್ಲಿ 1.5 ಎಕರೆ ಟೊಮೆಟೊ, ಹನಿ ನೀರಾವರಿ."
  };
  return samples[lang] || samples.en;
}

// Natural Language Parser for Spoken Agronomic Parameters
function parseSpokenAgronomicInput(text) {
  const lower = text.toLowerCase();
  
  // Crop detection
  const crops = [
    { name: "Tomato", matches: ["tomato", "tamatar", "टमाटर", "ટામેટા", "टोमॅटो", "టమాటా", "தக்காளி"] },
    { name: "Onion", matches: ["onion", "pyaz", "kanda", "कांदा", "ડુંગળી", "ఉల్లిపాయ", "வெங்காயம்"] },
    { name: "Chilli (Dry)", matches: ["chilli", "mirchi", "chili", "मिर्च", "મરચાં", "మిర్చి", "மிளகாய்"] },
    { name: "Potato", matches: ["potato", "aloo", "बटाटा", "आलू", "બટાકા", "బంగాళాదుంప", "உருளைக்கிழங்கு"] },
    { name: "Grapes", matches: ["grapes", "angoor", "द्राक्ष", "દ્રાક્ષ", "திராட்சை"] },
    { name: "Turmeric", matches: ["turmeric", "haldi", "हळद", "હળદર", "மஞ்சள்"] }
  ];

  for (const c of crops) {
    if (c.matches.some(m => lower.includes(m))) {
      document.getElementById("select-crop").value = c.name;
      break;
    }
  }

  // Acres detection (regex for numbers)
  const acreMatch = lower.match(/([0-9]+(?:\.[0-9]+)?)\s*(?:acres?|acre|एकड़|એકર|एकर|ఎకరాలు|ஏக்கர்)/i) || lower.match(/([0-9]+(?:\.[0-9]+)?)/);
  if (acreMatch) {
    const val = parseFloat(acreMatch[1]);
    if (val >= 0.5 && val <= 2.5) {
      document.getElementById("slider-land-acres").value = val.toString();
      document.getElementById("lbl-acres-val").innerText = `${val} Acres`;
    }
  }

  // District detection
  if (lower.includes("kolar") || lower.includes("कोलार") || lower.includes("ಕೋಲಾರ")) {
    document.getElementById("select-mandi-district").value = "Karnataka_Kolar";
  } else if (lower.includes("guntur") || lower.includes("गुंटूर") || lower.includes("గుంటూరు")) {
    document.getElementById("select-mandi-district").value = "Andhra Pradesh_Guntur";
  } else if (lower.includes("agra") || lower.includes("आगरा")) {
    document.getElementById("select-mandi-district").value = "Uttar Pradesh_Agra";
  } else if (lower.includes("salem") || lower.includes("सेलम") || lower.includes("சேலம்")) {
    document.getElementById("select-mandi-district").value = "Tamil Nadu_Salem";
  } else {
    document.getElementById("select-mandi-district").value = "Maharashtra_Nashik";
  }

  // Irrigation detection
  if (lower.includes("drip") || lower.includes("ड्रिप") || lower.includes("ઠિબક") || lower.includes("డ్రిప్")) {
    document.getElementById("select-irrigation").value = "Drip";
  } else if (lower.includes("rain") || lower.includes("बारिश") || lower.includes("વરસાદ")) {
    document.getElementById("select-irrigation").value = "Rainfed";
  } else {
    document.getElementById("select-irrigation").value = "Canal";
  }

  calculateCreditProfile();
  speakTextSummary();
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
  chips.forEach(chip => {
    chip.addEventListener("click", () => {
      const preset = chip.getAttribute("data-preset");
      if (preset === "tomato_nashik") {
        document.getElementById("input-farmer-name").value = "Ramesh Tukaram Patil";
        document.getElementById("select-mandi-district").value = "Maharashtra_Nashik";
        document.getElementById("select-crop").value = "Tomato";
        document.getElementById("slider-land-acres").value = "1.5";
        document.getElementById("lbl-acres-val").innerText = "1.5 Acres";
        document.getElementById("select-irrigation").value = "Drip";
      } else if (preset === "chilli_guntur") {
        document.getElementById("input-farmer-name").value = "Samba Siva Rao";
        document.getElementById("select-mandi-district").value = "Andhra Pradesh_Guntur";
        document.getElementById("select-crop").value = "Chilli (Dry)";
        document.getElementById("slider-land-acres").value = "2.0";
        document.getElementById("lbl-acres-val").innerText = "2.0 Acres";
        document.getElementById("select-irrigation").value = "Drip";
      } else if (preset === "potato_agra") {
        document.getElementById("input-farmer-name").value = "Ram Naresh Yadav";
        document.getElementById("select-mandi-district").value = "Uttar Pradesh_Agra";
        document.getElementById("select-crop").value = "Potato";
        document.getElementById("slider-land-acres").value = "2.2";
        document.getElementById("lbl-acres-val").innerText = "2.2 Acres";
        document.getElementById("select-irrigation").value = "Canal";
      } else if (preset === "turmeric_salem") {
        document.getElementById("input-farmer-name").value = "Murugan Sengodan";
        document.getElementById("select-mandi-district").value = "Tamil Nadu_Salem";
        document.getElementById("select-crop").value = "Turmeric";
        document.getElementById("slider-land-acres").value = "1.8";
        document.getElementById("lbl-acres-val").innerText = "1.8 Acres";
        document.getElementById("select-irrigation").value = "Drip";
      } else if (preset === "onion_lasalgaon") {
        document.getElementById("input-farmer-name").value = "Suresh Balasaheb Jadhav";
        document.getElementById("select-mandi-district").value = "Maharashtra_Nashik";
        document.getElementById("select-crop").value = "Onion";
        document.getElementById("slider-land-acres").value = "1.2";
        document.getElementById("lbl-acres-val").innerText = "1.2 Acres";
        document.getElementById("select-irrigation").value = "Drip";
      }
      calculateCreditProfile();
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

// Fetch Live Datasets from server API (if available)
function fetchLiveDatasets() {
  fetch("/api/datasets")
    .then(res => res.json())
    .then(data => {
      if (data.agmarknet && data.agmarknet.length > 0) {
        renderAgmarknetTable(data.agmarknet);
      }
    })
    .catch(() => {
      // Gracefully silent fallback to embedded default datasets
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
