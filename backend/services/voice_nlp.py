"""
Multilingual Voice Recognition & Agronomic Entity Extraction Engine
Supports 10+ Indian regional languages:
1. Hindi (हिंदी)
2. Marathi (मराठी)
3. Gujarati (ગુજરાતી)
4. Telugu (తెలుగు)
5. Tamil (தமிழ்)
6. Kannada (ಕನ್ನಡ)
7. Punjabi (ਪੰਜਾਬੀ)
8. Bengali (বাংলা)
9. Odia (ଓଡ଼ିଆ)
10. Assamese (অসমীয়া)
11. English

Transforms spoken farmer utterances into verified structured form fields:
Borrower Name, Phone, Crop, Acreage, Expected Yield, Input Costs, Peer Guarantors, Location.
"""

from typing import Dict, Any, List, Optional
import re
import math


# Supported 11 Indian Agricultural Languages
SUPPORTED_LANGUAGES: Dict[str, Dict[str, str]] = {
    "hi": {"name": "Hindi", "native": "हिंदी", "code": "hi-IN"},
    "mr": {"name": "Marathi", "native": "मराठी", "code": "mr-IN"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "code": "gu-IN"},
    "te": {"name": "Telugu", "native": "తెలుగు", "code": "te-IN"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "code": "ta-IN"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "code": "kn-IN"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "code": "pa-IN"},
    "bn": {"name": "Bengali", "native": "বাংলা", "code": "bn-IN"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "code": "or-IN"},
    "as": {"name": "Assamese", "native": "অসমীয়া", "code": "as-IN"},
    "en": {"name": "English", "native": "English", "code": "en-IN"}
}

# Curated Vernacular Utterance Templates for 1-Click Demonstration
SAMPLE_VOICE_UTTERANCES: Dict[str, Dict[str, Any]] = {
    "hi": {
        "audio_label": "Hindi Voice Sample (Nashik Tomato Farmer)",
        "transcript": "मेरा नाम रमेश पटेल है, मोबाइल नंबर 9876543210। पिंपलगांव नासिक में 2 एकड़ जमीन पर टमाटर लगाया है। 18 क्विंटल प्रति एकड़ पैदावार की उम्मीद है और लगभग 24000 रुपये खाद बीज और मजदूरी में खर्च हुए हैं।",
        "expected": {
            "name": "रमेश पटेल (Ramesh Patel)",
            "phone": "9876543210",
            "village": "Pimpalgaon",
            "district": "Nashik",
            "state": "Maharashtra",
            "crop": "Tomato (Horticulture)",
            "acres": 2.0,
            "yield_quintals": 18.0,
            "costs": 24000.0,
            "fpo": "Sahyadri Agro Producer Co.",
            "p1": "Suresh Kumar",
            "p2": "Dinesh Bhai",
            "p3": "Mahesh Solanki"
        }
    },
    "mr": {
        "audio_label": "Marathi Voice Sample (Vidarbha Cotton Farmer)",
        "transcript": "माझे नाव विलासराव देशमुख, फोन नंबर 9822334455. अमरावती जिल्ह्यात 2.5 एकर शेतात कपाशीची लागवड केली आहे. 8 क्विंटल उत्पादन अपेक्षित आहे आणि बियाणे व खताचा खर्च 26000 रुपये झाला आहे.",
        "expected": {
            "name": "विलासराव देशमुख (Vilasrao Deshmukh)",
            "phone": "9822334455",
            "village": "Nandgaon",
            "district": "Amravati",
            "state": "Maharashtra",
            "crop": "Cotton",
            "acres": 2.5,
            "yield_quintals": 8.0,
            "costs": 26000.0,
            "fpo": "MahaCotton Farmers Producer Co.",
            "p1": "Ganesh Shinde",
            "p2": "Pravin Patil",
            "p3": "Pandurang Koli"
        }
    },
    "gu": {
        "audio_label": "Gujarati Voice Sample (Saurashtra Groundnut/Soybean)",
        "transcript": "મારું નામ કાનજીભાઈ પટેલ છે, મોબાઈલ નંબર 9879112233. રાજકોટ પાસે 1.5 એકર જમીનમાં સોયાબીન વાવેલ છે. 10 ક્વિન્ટલ ઉપજની ધારણા છે અને 18000 રૂપિયા ખર્ચ થયો છે.",
        "expected": {
            "name": "કાનજીભાઈ પટેલ (Kanjibhai Patel)",
            "phone": "9879112233",
            "village": "Gondal",
            "district": "Rajkot",
            "state": "Gujarat",
            "crop": "Soybean",
            "acres": 1.5,
            "yield_quintals": 10.0,
            "costs": 18000.0,
            "fpo": "Tapi Valley Organic FPO",
            "p1": "Dinesh Bhai",
            "p2": "Jayesh Vora",
            "p3": "Govind Solanki"
        }
    },
    "te": {
        "audio_label": "Telugu Voice Sample (Warangal Cotton Farmer)",
        "transcript": "నా పేరు కొండయ్య రావు, ఫోన్ నంబర్ 9440123456. వరంగల్ జిల్లాలో 2 ఎకరాల్లో పత్తి సాగు చేస్తున్నాను. ఎకరానికి 7 క్వింటాళ్ల దిగుబడి ఆశిస్తున్నాను మరియు ఖర్చులు 22000 రూపాయలు అయ్యాయి.",
        "expected": {
            "name": "కొండయ్య రావు (Kondaiah Rao)",
            "phone": "9440123456",
            "village": "Wardhannapet",
            "district": "Warangal",
            "state": "Telangana",
            "crop": "Cotton",
            "acres": 2.0,
            "yield_quintals": 7.0,
            "costs": 22000.0,
            "fpo": "Telangana Rythu Mithra FPO",
            "p1": "Narsimha Reddy",
            "p2": "Srinivas Rao",
            "p3": "Chandraiah"
        }
    },
    "ta": {
        "audio_label": "Tamil Voice Sample (Dindigul Tomato Farmer)",
        "transcript": "என் பெயர் சுப்பிரமணியன், கைபேசி எண் 9443198765. திண்டுக்கல் மாவட்டத்தில் 1.5 ஏக்கரில் தக்காளி பயிரிட்டுள்ளேன். 16 குவிண்டால் விளைச்சல் எதிர்பார்க்கிறேன், செலவு 20000 ரூபாய்.",
        "expected": {
            "name": "சுப்பிரமணியன் (Subramanian)",
            "phone": "9443198765",
            "village": "Oddanchatram",
            "district": "Dindigul",
            "state": "Tamil Nadu",
            "crop": "Tomato (Horticulture)",
            "acres": 1.5,
            "yield_quintals": 16.0,
            "costs": 20000.0,
            "fpo": "Uzhava Sandhai Producer Collective",
            "p1": "Murugan K",
            "p2": "Palanisamy V",
            "p3": "Karthik R"
        }
    },
    "kn": {
        "audio_label": "Kannada Voice Sample (Davanagere Maize Farmer)",
        "transcript": "ನನ್ನ ಹೆಸರು ಬಸವರಾಜ್ ಗೌಡ, ಮೊಬೈಲ್ 9845012345. ದಾವಣಗೆರೆಯಲ್ಲಿ 2.0 ಎಕರೆ ಜಮೀನಿನಲ್ಲಿ ಮೆಕ್ಕೆಜೋಳ ಬೆಳೆದಿದ್ದೇನೆ. 18 ಕ್ವಿಂಟಾಲ್ ಇಳುವರಿ ನಿರೀಕ್ಷೆಯಿದೆ, 21000 ರೂ ಖರ್ಚಾಗಿದೆ.",
        "expected": {
            "name": "ಬಸವರಾಜ್ ಗೌಡ (Basavaraj Gowda)",
            "phone": "9845012345",
            "village": "Harihar",
            "district": "Davanagere",
            "state": "Karnataka",
            "crop": "Maize",
            "acres": 2.0,
            "yield_quintals": 18.0,
            "costs": 21000.0,
            "fpo": "Tunga Agro Farmers Collective",
            "p1": "Manjunath Patil",
            "p2": "Shivanand Swamy",
            "p3": "Eshwarappa"
        }
    },
    "pa": {
        "audio_label": "Punjabi Voice Sample (Khanna Wheat Farmer)",
        "transcript": "ਮੇਰਾ ਨਾਮ ਗੁਰਪ੍ਰੀਤ ਸਿੰਘ ਹੈ, ਮੋਬਾਈਲ ਨੰਬਰ 9814098765. ਖੰਨਾ ਕੋਲ 2.0 ਏਕੜ ਵਿੱਚ ਕਣਕ ਬੀਜੀ ਹੈ। 19 ਕੁਇੰਟਲ ਝਾੜ ਦੀ ਉਮੀਦ ਹੈ ਅਤੇ 25000 ਰੁਪਏ ਕੁੱਲ ਖਰਚਾ ਆਇਆ ਹੈ।",
        "expected": {
            "name": "ਗੁਰਪ੍ਰੀਤ ਸਿੰਘ (Gurpreet Singh)",
            "phone": "9814098765",
            "village": "Alour",
            "district": "Ludhiana",
            "state": "Punjab",
            "crop": "Wheat",
            "acres": 2.0,
            "yield_quintals": 19.0,
            "costs": 25000.0,
            "fpo": "Malwa Progressive Farmers FPO",
            "p1": "Harbhajan Singh",
            "p2": "Jagjit Singh",
            "p3": "Balwinder Singh"
        }
    },
    "bn": {
        "audio_label": "Bengali Voice Sample (Hooghly Potato/Tomato)",
        "transcript": "আমার নাম সুব্রত দাস, ফোন নম্বর 9830054321। হুগলিতে 1.5 একর জমিতে টমেটো চাষ করেছি। 17 কুইন্টাল ফলন প্রত্যাশা করছি এবং খরচ হয়েছে 23000 টাকা।",
        "expected": {
            "name": "সুব্রত দাস (Subrata Das)",
            "phone": "9830054321",
            "village": "Tarakeswar",
            "district": "Hooghly",
            "state": "West Bengal",
            "crop": "Tomato (Horticulture)",
            "acres": 1.5,
            "yield_quintals": 17.0,
            "costs": 23000.0,
            "fpo": "Radhanagar Krishi Kalyan FPO",
            "p1": "Bikash Ghosh",
            "p2": "Tapan Mondal",
            "p3": "Anup Roy"
        }
    },
    "or": {
        "audio_label": "Odia Voice Sample (Cuttack Vegetable/Tomato)",
        "transcript": "ମୋର ନାମ ବିକ୍ରମ ମହାନ୍ତି, ମୋବାଇଲ 9437012345. କଟକ ଜିଲ୍ଲାରେ 1.5 ଏକର ଜମିରେ ଟମାଟୋ ଚାଷ କରିଛି। 15 କ୍ୱିଣ୍ଟାଲ ଅମଳ ଆଶା କରୁଛି ଏବଂ 19000 ଟଙ୍କା ଖର୍ଚ୍ଚ ହୋଇଛି।",
        "expected": {
            "name": "ବିକ୍ରମ ମହାନ୍ତି (Bikram Mohanty)",
            "phone": "9437012345",
            "village": "Banki",
            "district": "Cuttack",
            "state": "Odisha",
            "crop": "Tomato (Horticulture)",
            "acres": 1.5,
            "yield_quintals": 15.0,
            "costs": 19000.0,
            "fpo": "Mahanadi Farmers Producer Co.",
            "p1": "Pratap Jena",
            "p2": "Sudhir Nayak",
            "p3": "Rabindra Sahu"
        }
    },
    "as": {
        "audio_label": "Assamese Voice Sample (Nagaon Maize/Vegetable)",
        "transcript": "মোৰ নাম ৰঞ্জন বৰা, ফোন নম্বৰ 9435012345। নগাঁও জিলাত 2.0 একৰ মাটিত গোমধান খেতি কৰিছো। 16 কুইন্টল উৎপাদনৰ আশা আৰু 20000 টকা খৰচ হৈছে।",
        "expected": {
            "name": "ৰঞ্জন বৰা (Ranjan Borah)",
            "phone": "9435012345",
            "village": "Raha",
            "district": "Nagaon",
            "state": "Assam",
            "crop": "Maize",
            "acres": 2.0,
            "yield_quintals": 16.0,
            "costs": 20000.0,
            "fpo": "Kaziranga Organic Farmers Collective",
            "p1": "Deben Saikia",
            "p2": "Biren Kalita",
            "p3": "Mukul Hazarika"
        }
    },
    "en": {
        "audio_label": "English Voice Sample (Direct Smallholder Intake)",
        "transcript": "My name is Ramesh Patel, phone 9876543210. I am cultivating 2.0 acres of Tomato in Pimpalgaon, Nashik. Expecting 18 quintals per acre yield and total input expenses are 24000 rupees.",
        "expected": {
            "name": "Ramesh Patel",
            "phone": "9876543210",
            "village": "Pimpalgaon",
            "district": "Nashik",
            "state": "Maharashtra",
            "crop": "Tomato (Horticulture)",
            "acres": 2.0,
            "yield_quintals": 18.0,
            "costs": 24000.0,
            "fpo": "Sahyadri Agro Producer Co.",
            "p1": "Suresh Kumar",
            "p2": "Dinesh Bhai",
            "p3": "Mahesh Solanki"
        }
    }
}


from backend.services.voice_service import voice_service

INDIC_NUMERAL_TRANS = str.maketrans({
    '\u0966': '0', '\u0967': '1', '\u0968': '2', '\u0969': '3', '\u096A': '4',
    '\u096B': '5', '\u096C': '6', '\u096D': '7', '\u096E': '8', '\u096F': '9',  # Devanagari
    '\u0AE6': '0', '\u0AE7': '1', '\u0AE8': '2', '\u0AE9': '3', '\u0AEA': '4',
    '\u0AEB': '5', '\u0AEC': '6', '\u0AED': '7', '\u0AEE': '8', '\u0AEF': '9',  # Gujarati
    '\u09E6': '0', '\u09E7': '1', '\u09E8': '2', '\u09E9': '3', '\u09EA': '4',
    '\u09EB': '5', '\u09EC': '6', '\u09ED': '7', '\u09EE': '8', '\u09EF': '9',  # Bengali
    '\u0A66': '0', '\u0A67': '1', '\u0A68': '2', '\u0A69': '3', '\u0A6A': '4',
    '\u0A6B': '5', '\u0A6C': '6', '\u0A6D': '7', '\u0A6E': '8', '\u0A6F': '9',  # Gurmukhi
    '\u0C66': '0', '\u0C67': '1', '\u0C68': '2', '\u0C69': '3', '\u0C6A': '4',
    '\u0C6B': '5', '\u0C6C': '6', '\u0C6D': '7', '\u0C6E': '8', '\u0C6F': '9',  # Telugu
    '\u0CE6': '0', '\u0CE7': '1', '\u0CE8': '2', '\u0CE9': '3', '\u0CEA': '4',
    '\u0CEB': '5', '\u0CEC': '6', '\u0CED': '7', '\u0CEE': '8', '\u0CEF': '9',  # Kannada
    '\u0BE6': '0', '\u0BE7': '1', '\u0BE8': '2', '\u0BE9': '3', '\u0BEA': '4',
    '\u0BEB': '5', '\u0BEC': '6', '\u0BED': '7', '\u0BEE': '8', '\u0BEF': '9',  # Tamil
    '\u0B66': '0', '\u0B67': '1', '\u0B68': '2', '\u0B69': '3', '\u0B6A': '4',
    '\u0B6B': '5', '\u0B6C': '6', '\u0B6D': '7', '\u0B6E': '8', '\u0B6F': '9',  # Odia
})

HINDI_NUM_MAP: Dict[str, float] = {
    'एक': 1.0, 'one': 1.0, 'ek': 1.0,
    'आधा': 0.5, 'half': 0.5,
    'सवा': 1.25, 'डेढ़': 1.5, 'देढ़': 1.5, 'one and a half': 1.5, 'one and half': 1.5, 'dedh': 1.5,
    'पौने दो': 1.75, 'दो': 2.0, 'two': 2.0, 'दोन': 2.0, 'બે': 2.0, 'రెండు': 2.0, 'do': 2.0,
    'सवा दो': 2.25, 'ढाई': 2.5, 'two and a half': 2.5, 'two and half': 2.5, 'dhai': 2.5,
    'पौने तीन': 2.75, 'तीन': 3.0, 'three': 3.0, 'teen': 3.0,
    'चार': 4.0, 'four': 4.0, 'char': 4.0,
    'पांच': 5.0, 'पाँच': 5.0, 'five': 5.0, 'panch': 5.0,
    'छह': 6.0, 'छः': 6.0, 'six': 6.0, 'chhah': 6.0,
    'सात': 7.0, 'seven': 7.0, 'saat': 7.0,
    'आठ': 8.0, 'eight': 8.0, 'aath': 8.0,
    'नौ': 9.0, 'nine': 9.0, 'nau': 9.0,
    'दस': 10.0, 'ten': 10.0, 'das': 10.0,
    'ग्यारह': 11.0, 'eleven': 11.0, 'gyarah': 11.0,
    'बारह': 12.0, 'twelve': 12.0, 'barah': 12.0,
    'तेरह': 13.0, 'thirteen': 13.0, 'terah': 13.0,
    'चौदह': 14.0, 'fourteen': 14.0, 'chaudah': 14.0,
    'पंद्रह': 15.0, 'fifteen': 15.0, 'pandrah': 15.0,
    'सोलह': 16.0, 'sixteen': 16.0, 'solah': 16.0,
    'सत्रह': 17.0, 'seventeen': 17.0, 'satrah': 17.0,
    'अठारह': 18.0, 'eighteen': 18.0, 'atharah': 18.0,
    'उन्नीस': 19.0, 'nineteen': 19.0, 'unnis': 19.0,
    'बीस': 20.0, 'twenty': 20.0, 'bees': 20.0,
    'इक्कीस': 21.0, 'twenty one': 21.0, 'twenty-one': 21.0,
    'बाईस': 22.0, 'twenty two': 22.0, 'twenty-two': 22.0,
    'तेईस': 23.0, 'twenty three': 23.0, 'twenty-three': 23.0,
    'चौबीस': 24.0, 'twenty four': 24.0, 'twenty-four': 24.0, 'chaubis': 24.0,
    'पच्चीस': 25.0, 'twenty five': 25.0, 'twenty-five': 25.0, 'pachis': 25.0, 'pachchis': 25.0,
    'छब्बीस': 26.0, 'twenty six': 26.0, 'twenty-six': 26.0,
    'सत्ताईस': 27.0, 'twenty seven': 27.0, 'twenty-seven': 27.0,
    'अट्ठाईस': 28.0, 'twenty eight': 28.0, 'twenty-eight': 28.0,
    'उनतीस': 29.0, 'twenty nine': 29.0, 'twenty-nine': 29.0,
    'तीस': 30.0, 'thirty': 30.0, 'tees': 30.0,
    'पैंतीस': 35.0, 'thirty five': 35.0, 'thirty-five': 35.0,
    'चालीस': 40.0, 'forty': 40.0, 'chalis': 40.0,
    'पैंतालीस': 45.0, 'forty five': 45.0, 'forty-five': 45.0,
    'पचास': 50.0, 'fifty': 50.0, 'pachas': 50.0,
    'साठ': 60.0, 'sixty': 60.0,
    'सत्तर': 70.0, 'seventy': 70.0,
    'अस्सी': 80.0, 'eighty': 80.0,
    'नब्बे': 90.0, 'ninety': 90.0,
    'सौ': 100.0, 'hundred': 100.0,
}

HINDI_NUMBER_WORDS = [
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:डेढ़|देढ़|dedh|one and a half|one and half)(?:(?=[\s,।॥\(\)\[\]])|$)', 1.5),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:ढाई|dhai|two and a half|two and half)(?:(?=[\s,।॥\(\)\[\]])|$)', 2.5),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:सवा दो)(?:(?=[\s,।॥\(\)\[\]])|$)', 2.25),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:पौने दो)(?:(?=[\s,।॥\(\)\[\]])|$)', 1.75),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:सवा एक|सवा)(?:(?=[\s,।॥\(\)\[\]])|$)', 1.25),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:आधा|half)(?:(?=[\s,।॥\(\)\[\]])|$)', 0.5),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:एक|one|ek|ਇੱਕ|એક|ఒకటి|ఒక|ஒன்று|ஒரு|ಒಂದು|এক|ଗୋଟିଏ)(?:(?=[\s,।॥\(\)\[\]])|$)', 1.0),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:दो|two|do|ਦੋ|બે|రెండు|இரண்டு|ಎರಡು|দুই|ଦୁଇ|दोन)(?:(?=[\s,।॥\(\)\[\]])|$)', 2.0),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:तीन|three|teen|ਤਿੰਨ|ત્રણ|మూడు|மூன்று|ಮೂರು|তিন|ତିନି)(?:(?=[\s,।॥\(\)\[\]])|$)', 3.0),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:चार|four|char|ਚਾਰ|ચાર|నాలుగు|நான்கு|ನಾಲ್ಕು|চার|ଚାରି)(?:(?=[\s,।॥\(\)\[\]])|$)', 4.0),
    (r'(?:(?<=[\s,।॥\(\)\[\]])|^)(?:पांच|पाँच|five|panch|ਪੰਜ|પાંચ|ఐదు|ஐந்து|ಐದು|পাঁচ|ପାଞ୍ଚ)(?:(?=[\s,।॥\(\)\[\]])|$)', 5.0),
]

def normalize_spoken_numbers(text: str) -> str:
    """Normalize spoken Indic and English number words, units, thousands, and lakhs into digits."""
    if not text:
        return text
    sorted_keys = sorted(HINDI_NUM_MAP.keys(), key=lambda k: len(k), reverse=True)
    num_pattern = '|'.join(re.escape(k) for k in sorted_keys)

    # 1. Compound thousands: e.g. 'चौबीस हज़ार', '24 हज़ार', 'twenty four thousand'
    th_pat = rf'(?:(?<=[\s,।॥\(\)\[\]])|^)({num_pattern}|\d+)\s*(?:हज़ार|हजार|thousand)(?:(?=[\s,।॥\(\)\[\]])|$)'
    def replace_thousand(m):
        val_str = m.group(1).lower()
        if val_str.isdigit():
            v = int(val_str)
        else:
            v = HINDI_NUM_MAP.get(val_str, 0)
        return str(int(v * 1000))
    text = re.sub(th_pat, replace_thousand, text, flags=re.IGNORECASE)

    # 2. Compound lakhs: e.g. 'एक लाख', '1 लाख', 'one lakh'
    lakh_pat = rf'(?:(?<=[\s,।॥\(\)\[\]])|^)({num_pattern}|\d+)\s*(?:लाख|lakh|lac)(?:(?=[\s,।॥\(\)\[\]])|$)'
    def replace_lakh(m):
        val_str = m.group(1).lower()
        if val_str.isdigit():
            v = int(val_str)
        else:
            v = HINDI_NUM_MAP.get(val_str, 0)
        return str(int(v * 100000))
    text = re.sub(lakh_pat, replace_lakh, text, flags=re.IGNORECASE)

    # 3. Units with number words: acres, quintals, rupees
    unit_pat = rf'(?:(?<=[\s,।॥\(\)\[\]])|^)({num_pattern})\s*(acres?|acre|एकड़|एकर|એકર|ఎకరాలు|ஏக்கர்|quintals?|qtl|क्विंटल|ക്വിന്റൽ|rupees?|रुपये|रुपया|રૂપિયા|रू|rs\.?)(?:(?=[\s,।॥\(\)\[\]])|$)'
    def replace_units(m):
        num_word = m.group(1).lower()
        unit = m.group(2)
        v = HINDI_NUM_MAP.get(num_word, num_word)
        if isinstance(v, float) and v.is_integer():
            v = int(v)
        return f'{v} {unit}'
    text = re.sub(unit_pat, replace_units, text, flags=re.IGNORECASE)

    return text


KNOWN_CROPS = [
    ("Tomato (Horticulture)", ["tomato", "tamatar", "टमाटर", "ટામેટા", "टोमॅटो", "టమాటా", "தக்காளி", "টমেটো", "ଟମାଟୋ", "ਟਮਾਟਰ", "ಟೊಮೆಟೊ"]),
    ("Cotton", ["cotton", "kapas", "kapaas", "कपास", "કપાસ", "कापूस", "कपाशी", "పత్తి", "பருத்தி", "তুলা", "ਕਪਾਹ", "ಹತ್ತಿ", "କପା"]),
    ("Soybean", ["soybean", "soya", "सोयाबीन", "સોયાબીન", "సోయాబీನ್", "சோயாபீன்", "সয়াবিন", "ਸੋਇਆਬੀਨ", "ಸೋಯಾಬೀನ್", "ସୋୟାବିନ୍"]),
    ("Wheat", ["wheat", "gehun", "gehu", "गेहूं", "ઘઉં", "गहू", "గోధుమ", "கோதுமை", "গম", "ਕਣਕ", "ಗೋಧಿ", "ଗହମ"]),
    ("Onion", ["onion", "pyaz", "kanda", "कांदा", "प्याज", "ડુંગળી", "ఉల్లిపాయ", "வெங்காயம்", "পেঁয়াজ", "ਪਿਆਜ਼", "ಈರುಳ್ಳಿ", "ପିଆଜ"]),
    ("Maize", ["maize", "makka", "maka", "मक्का", "मका", "మక్కజొన్న", "ಮೆಕ್ಕೆಜೋಳ", "গোমধান", "ਭੁੱਟਾ", "ମକା"]),
    ("Potato", ["potato", "aloo", "alu", "बटाटा", "आलू", "બટાકા", "ఆలూ", "உருளைக்கிழங்கு", "আলু", "ਆਲੂ", "ಆಲೂಗಡ್ಡೆ", "ଆଳୁ"]),
    ("Chilli (Dry)", ["chilli", "chili", "mirchi", "मिर्च", "मिरची", "મરચાં", "మిర్చి", "மிளகாய்", "মরিচ", "ਮਿਰਚ", "ಮೆಣಸಿನಕಾಯಿ", "ଲଙ୍କା"]),
    ("Turmeric", ["turmeric", "haldi", "हल्दी", "हळद", "હળદર", "పసుపు", "மஞ்சள்", "হলুদ", "ਹਲਦੀ", "ಅರಿಶಿನ", "ହଳଦୀ"]),
    ("Grapes", ["grapes", "angoor", "अंगूर", "द्राक्ष", "દ્રાક્ષ", "திராட்சை", "আঙুর", "ਅੰਗੂਰ", "ದ್ರಾಕ್ಷಿ", "ଅଙ୍ଗୁର"]),
    ("Pomegranate", ["pomegranate", "anaar", "anar", "अनार", "डाळिंब", "દાડમ", "దానిమ్మ", "மாதுளை", "ದಾಳಿಂಬೆ"]),
    ("Cauliflower", ["cauliflower", "gobhi", "phool gobhi", "फुलगोभी", "કોબીજ", "క్యಾಲੀఫ్ලవర్", "காலிஃபிளவர்", "ফুলকপি"])
]

KNOWN_DISTRICTS = [
    ("Nashik", ["nashik", "nasik", "नासिक", "नाशिक", "નાસિક", "నాసిక్", "நாசிக்", "নাসিক", "ਨਾਸਿਕ", "ನಾಸಿಕ್", "ନଶିକ"]),
    ("Guntur", ["guntur", "गुंटूर", "ગુંટૂર", "గుంటూరు", "குண்டூர்", "গুন্টুর", "ਗੁੰਟੂਰ", "ಗುಂಟೂರು", "ଗୁଣ୍ଟୁର"]),
    ("Kolar", ["kolar", "कोलार", "કોલાર", "కోలార్", "கோலார்", "কোলার", "ਕੋਲਾਰ", "ಕೋಲಾರ", "କୋଲାର"]),
    ("Agra", ["agra", "आगरा", "આગ્રા", "ఆగ్రా", "ஆக்ரா", "আগ্রা", "ਆਗਰਾ", "ಆગ್ರಾ", "ଆଗ୍ରା"]),
    ("Salem", ["salem", "सेलम", "સેલમ", "సేలం", "சேலம்", "সালেম", "ਸਲੇਮ", "ಸೇಲಂ", "ସାଲେମ"]),
    ("Amravati", ["amravati", "अमरावती", "અમરાવતી"]),
    ("Rajkot", ["rajkot", "राजकोट", "રાજકોટ"]),
    ("Warangal", ["warangal", "वारंगल", "వరంగల్"]),
    ("Dindigul", ["dindigul", "डिंडीगुल", "திண்டுக்கல்"]),
    ("Davanagere", ["davanagere", "दावणगेरे", "ದಾವಣಗೆರೆ"]),
    ("Ludhiana", ["ludhiana", "khanna", "ਲੁਧਿਆਣਾ", "ਖੰਨਾ", "लुधियाना", "खन्ना"]),
    ("Hooghly", ["hooghly", "हुगली", "হুগলি"]),
    ("Cuttack", ["cuttack", "कटक", "କଟକ"]),
    ("Nagaon", ["nagaon", "नगांव", "নগাঁও"]),
    ("Indore", ["indore", "इंदौर", "ઇન્દોર", "ఇండోర్"])
]

FOLLOWUP_QUESTIONS = {
    "name": {
        "hi": "कृपया किसान का पूरा नाम बताएं। (उदा. रमेश पटेल)",
        "en": "Please provide the farmer's full name (e.g. Ramesh Patel).",
        "mr": "कृपया शेतकऱ्याचे पूर्ण नाव सांगा. (उदा. रमेश पटेल)",
        "gu": "કૃપા કરીને ખેડૂતનું પૂરું નામ જણાવો. (દા.ત. રમેશ પટેલ)"
    },
    "phone": {
        "hi": "कृपया अपना 10 अंकों का मोबाइल नंबर बताएं। (उदा. 9876543210)",
        "en": "Please provide your 10-digit mobile number (e.g. 9876543210).",
        "mr": "कृपया आपला १० अंकी मोबाईल नंबर सांगा. (उदा. ९८७६५४३२१०)",
        "gu": "કૃપા કરીને તમારો ૧૦ અંકનો મોબાઈલ નંબર જણાવો. (દા.ત. ૯૮૭૯૧૧૨૨૩૩)"
    },
    "village": {
        "hi": "कृपया अपने गाँव का नाम बताएं। (उदा. पिंपलगांव, रामपुर)",
        "en": "Please state your village name (e.g. Pimpalgaon, Rampur).",
        "mr": "कृपया आपल्या गावाचे नाव सांगा. (उदा. पिंपळगाव, नांदगाव)",
        "gu": "કૃપા કરીને તમારા ગામનું નામ જણાવો. (દા.ત. ગોંડલ)"
    },
    "crop": {
        "hi": "कृपया बताएं कि आप इस मौसम में कौन सी फसल उगा रहे हैं? (उदा. टमाटर, प्याज, कपास, गेहूं)",
        "en": "Which crop are you cultivating this season? (e.g. Tomato, Onion, Cotton, Wheat)",
        "mr": "तुम्ही कोणते पीक घेत आहात? (उदा. टोमॅटो, कांदा, कापूस, गहू)",
        "gu": "તમે કયો પાક વાવી રહ્યા છો? (દા.ત. ટામેટા, સોયાબીન, કપાસ)",
        "te": "మీరు ఏ పంట సాగు చేస్తున్నారు? (ఉదా. టమాటా, పత్తి)",
        "ta": "நீங்கள் என்ன பயிர் பயிரிடுகிறீர்கள்? (எ.கா. தக்காளி, பருத்தி)",
        "kn": "ನೀವು ಯಾವ ಬೆಳೆಯನ್ನು ಬೆಳೆಯುತ್ತಿದ್ದೀರಿ? (ಉದಾ. ಟೊಮೆಟೊ, ಮೆಕ್ಕೆಜೋಳ)",
        "pa": "ਤੁਸੀਂ ਕਿਹੜੀ ਫ਼ਸਲ ਉਗਾ ਰਹੇ ਹੋ? (ਜਿਵੇਂ ਕਣਕ, ਕਪਾਹ)",
        "bn": "আপনি কোন ফসল চাষ করছেন? (যেমন টমেটো, আলু)",
        "or": "ଆପଣ କେଉଁ ଫସଲ ଚାଷ କରୁଛନ୍ତି? (ଉଦା. ଟମାଟୋ)",
        "as": "আপুনি কি শস্য খেতি কৰিছে? (যেনে গোমধান)"
    },
    "acres": {
        "hi": "आपके पास कितने एकड़ कृषि भूमि है? (उदा. 1.5 एकड़, 2 एकड़)",
        "en": "How many acres of land are you cultivating? (e.g. 1.5 acres, 2 acres)",
        "mr": "आपल्याकडे किती एकर जमीन आहे? (उदा. १.५ एकर, २ एकर)",
        "gu": "તમારી પાસે કેટલા એકર જમીન છે? (દા.ત. ૧.૫ એકર, ૨ એકર)",
        "te": "మీరు ఎన్ని ఎకరాలలో సాగు చేస్తున్నారు? (ఉదా. 1.5 ఎకరాలు, 2 ఎకరాలు)",
        "ta": "நீங்கள் எத்தனை ஏக்கரில் பயிரிடுகிறீர்கள்? (எ.கா. 1.5 ஏக்கர், 2 ஏக்கர்)",
        "kn": "ನೀವು ಎಷ್ಟು ಎಕರೆ ಜಮೀನಿನಲ್ಲಿ ಕೃಷಿ ಮಾಡುತ್ತಿದ್ದೀರಿ? (ಉದಾ. 1.5 ಎಕರೆ, 2 ಎಕರೆ)",
        "pa": "ਤੁਹਾਡੇ ਕੋਲ ਕਿੰਨੇ ਏਕੜ ਜ਼ਮੀਨ ਹੈ? (ਜਿਵੇਂ 1.5 ਏਕੜ, 2 ਏਕੜ)",
        "bn": "আপনার কত একর জমি আছে? (যেমন ১.৫ একর, ২ একর)",
        "or": "ଆପଣଙ୍କର କେତେ ଏକର ଜମି ଅଛି? (ଉଦା. ୧.୫ ଏକର, ୨ ଏକର)",
        "as": "আপোনাৰ কিমান একৰ মাটি আছে? (যেনে ২.০ একৰ)"
    },
    "district": {
        "hi": "आपका खेत किस जिले या मंडी क्षेत्र में स्थित है? (उदा. नासिक, गुंटूर, कोलार, आगरा)",
        "en": "In which district is your farm located? (e.g. Nashik, Guntur, Kolar, Agra)",
        "mr": "आपले शेत कोणत्या जिल्ह्यात आहे? (उदा. नाशिक, अमरावती, गुंटूर)",
        "gu": "તમારું ખેતર કયા જિલ્લામાં આવેલું છે? (દા.ત. રાજકોટ, નાસિક)",
        "te": "మీ పొలం ఏ జిల్లాలో ఉంది? (ఉదా. వరంగల్, గుంటూరు)",
        "ta": "உங்கள் பண்ணை எந்த மாவட்டத்தில் உள்ளது? (எ.கா. திண்டுக்கல், சேலம்)",
        "kn": "ನಿಮ್ಮ ಜಮೀನು ಯಾವ ಜಿಲ್ಲೆಯಲ್ಲಿದೆ? (ಉದಾ. ದಾವಣಗೆರೆ, ಕೋಲಾರ)",
        "pa": "ਤੁਹਾਡਾ ਖੇਤ ਕਿਸ ਜ਼ਿਲ੍ਹੇ ਵਿੱਚ ਹੈ? (ਜਿਵੇਂ ਲੁਧਿਆਣਾ, ਖੰਨਾ)",
        "bn": "আপনার খামারটি কোন জেলায় অবস্থিত? (যেমন হুগলি, নদীয়া)",
        "or": "ଆପଣଙ୍କ ଜମି କେଉଁ ଜିଲ୍ଲାରେ ଅଛି? (ଉଦା. କଟକ)",
        "as": "আপোনাৰ পথাৰ কোনখন জিলাত অৱস্থিত? (যেনে নগাঁও)"
    },
    "yield": {
        "hi": "प्रति एकड़ आपकी अनुमानित पैदावार कितने क्विंटल है? (उदा. 18 क्विंटल प्रति एकड़)",
        "en": "What is your expected yield per acre in quintals? (e.g. 18 quintals/acre)",
        "mr": "प्रति एकर आपले अंदाजे उत्पादन किती क्विंटल आहे? (उदा. ८ क्विंटल)",
        "gu": "પ્રતિ એકર તમારી અંદાજિત ઉપજ કેટલા ક્વિન્ટલ છે? (દા.ત. ૧૦ ક્વિન્ટલ)",
        "te": "ఎకరాకు మీ అంచనా దిగుబడి ఎన్ని క్వింటాళ్లు? (ఉదా. 7 క్వింటాళ్లు)",
        "ta": "ஒரு ஏக்கருக்கு உங்கள் எதிர்பார்க்கப்படும் விளைச்சல் எத்தனை குவிண்டால்?",
        "kn": "ಪ್ರತಿ ಎಕರೆಗೆ ನಿಮ್ಮ ನಿರೀಕ್ಷಿತ ಇಳುವರಿ ಎಷ್ಟು ಕ್ವಿಂಟಾಲ್‌ಗಳು?",
        "pa": "ਪ੍ਰਤੀ ਏਕੜ ਤੁਹਾਡੀ ਅਨੁਮਾਨਿਤ ਪੈਦਾਵਾਰ ਕਿੰਨੇ ਕੁਇੰਟਲ ਹੈ?",
        "bn": "প্রতি একরে আপনার আনুমানিক ফলন কত কুইন্টাল?",
        "or": "ପ୍ରତି ଏକର କେତେ କ୍ୱିଣ୍ଟାଲ ଅମଳ ଆଶା କରୁଛନ୍ତି?",
        "as": "প্ৰতি একৰত কিমান কুইন্টল উৎপাদনৰ আশা কৰিছে?"
    },
    "costs": {
        "hi": "अनुमानित खेती का कुल खर्च कितना है? (उदा. 24000 रुपये)",
        "en": "What are your total estimated input expenses? (e.g. 24000 rupees)",
        "mr": "आपला एकूण शेती खर्च किती आहे? (उदा. २६००० रुपये)",
        "gu": "ખેતીનો અંદાજિત કુલ ખર્ચ કેટલો થયો છે? (દા.ત. ૧૮૦૦૦ રૂપિયા)",
        "te": "మొత్తం ఖర్చులు ఎన్ని రూపాయలు అయ్యాయి? (ఉదా. 22000 రూపాయలు)",
        "ta": "மொத்த சாகுபடி செலவு எவ்வளவு? (எ.கா. 20000 ரூபாய்)",
        "kn": "ಒಟ್ಟು ಕೃಷಿ ವೆಚ್ಚ ಎಷ್ಟು? (ಉದಾ. 21000 ರೂ)",
        "pa": "ਕੁੱਲ ਕਿੰਨਾ ਖਰਚਾ ਆਇਆ ਹੈ? (ਜਿਵੇਂ 25000 ਰੁਪਏ)",
        "bn": "মোট কত খরচ হয়েছে? (যেমন ২৩০০০ টাকা)",
        "or": "ମୋଟ କେତେ ଟଙ୍କା ଖର୍ଚ୍ଚ ହୋଇଛି? (ଉଦା. ୧୯୦୦୦ ଟଙ୍କା)",
        "as": "খেতিত মুঠ কিমান টকা খৰচ হৈছে? (যেনে ২০০০০ টকা)"
    }
}


class VoiceNLPService:
    """Service to process spoken utterances, transcribe, and map into form fields."""

    @staticmethod
    def get_supported_languages() -> Dict[str, Dict[str, str]]:
        return SUPPORTED_LANGUAGES

    @staticmethod
    def get_sample_utterance(lang_code: str) -> Dict[str, Any]:
        """Return sample audio transcription text and expected field mapping for any of the 11 languages."""
        return SAMPLE_VOICE_UTTERANCES.get(lang_code, SAMPLE_VOICE_UTTERANCES["hi"])

    @staticmethod
    def transcribe_audio_bytes(audio_bytes: bytes, lang_code: str = "hi") -> Dict[str, Any]:
        """
        Process recorded audio bytes using VoiceService (OpenAI Whisper or Google Speech)
        and return true transcribed text. Never returns fake hardcoded sample transcripts.
        """
        byte_length = len(audio_bytes) if audio_bytes else 0
        if not audio_bytes or byte_length < 100:
            return {
                "success": False,
                "error": "Empty or corrupted audio recording. Please speak clearly into your microphone.",
                "raw_transcript": "",
                "confidence_score": 0.0,
                "stt_engine": "none",
                "lang_code": lang_code,
                "audio_size_bytes": byte_length,
                "data_status": "EMPTY_AUDIO"
            }

        res = voice_service.transcribe_audio(audio_bytes, lang_code=lang_code, filename="recorded_audio.wav")
        if res.get("success") and res.get("transcript"):
            return {
                "success": True,
                "lang_code": lang_code,
                "audio_size_bytes": byte_length,
                "raw_transcript": res["transcript"],
                "confidence_score": 0.94,
                "stt_engine": res.get("provider", "SpeechRecognition (Google Speech)"),
                "data_status": "REALTIME_PROCESSED"
            }
        else:
            return {
                "success": False,
                "lang_code": lang_code,
                "audio_size_bytes": byte_length,
                "raw_transcript": "",
                "error": res.get("error", "Speech could not be understood. Please speak clearly or use typed input."),
                "confidence_score": 0.0,
                "stt_engine": res.get("provider", "none"),
                "data_status": "ERROR"
            }

    @staticmethod
    def parse_transcript_to_fields(
        transcript: str,
        lang_code: str = "hi",
        current_data: Optional[Dict[str, Any]] = None,
        target_field: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Extract verified agronomic entities from spoken/typed transcript across 11 Indian languages.
        Strictly does NOT invent values or assume missing information.
        Leaves unmentioned fields unchanged and detects proposed changes/conflicts with current_data.
        """
        if not transcript or not transcript.strip():
            return {
                "mapped_fields": dict(current_data) if current_data else {},
                "extracted_fields": {},
                "proposed_changes": {},
                "confidence_scores": {},
                "missing_fields": ["crop", "acres", "district", "yield", "costs"],
                "clarifications": ["कृपया अपने खेत और फसल का विवरण बोलें या टाइप करें।"],
                "contradictions": [],
                "raw_transcript": transcript or "",
                "requires_review": True
            }

        raw = transcript.strip()
        norm_text = normalize_spoken_numbers(raw.translate(INDIC_NUMERAL_TRANS))
        lower = norm_text.lower()

        extracted: Dict[str, Any] = {}
        confidences: Dict[str, float] = {}
        clarifications: List[str] = []
        contradictions: List[str] = []

        # 1. Phone number (continuous digits starting with 6-9, or prefixed by phone keyword)
        phone_match = re.search(r'(?:phone|mobile|नंबर|मोबाईल|నంబర్|फोन|फ़ोन|मोबाइल|ఫోన్|மொபைல்)\s*[:\s]?\b([6-9]\d{7,11})\b', norm_text, re.IGNORECASE) or re.search(r'\b([6-9]\d{8,11})\b', norm_text)
        if phone_match:
            extracted["phone"] = phone_match.group(1)
            confidences["phone"] = 0.99

        # 2. Farmer Name Detection
        name_cand = None
        name_patterns = [
            r'(?:mera\s+naam|मेरा\s+नाम|माझे\s+नाव|મારું\s+નામ|ਮੇਰਾ\s+ਨਾਮ|আমার\s+নাম|ମୋର\s+ନାମ|মোৰ\s+নাম)\s+([A-Za-z\u0900-\u0D7F\s\.]+?)(?:है|हूँ|हूं|आहे|છે|\.|,|।|\bफोन|\bमोबाइल|\bगाव|\bगाँव|\bगावात|\bजिल्हा|\bजिला|\bमेरे|\bમેં|$)',
            r'(?:నా\s+పేరు|என்\s+பெயர்|ನನ್ನ\s+ಹೆಸರು)\s+([A-Za-z\u0900-\u0D7F\s\.]+?)(?:,|\.|।|\s+ఫోన్|\s+கைபேசி|\s+ಮೊಬೈಲ್|$)',
            r'(?:my\s+name\s+is|i\s+am)\s+([A-Za-z\s\.]+?)(?:,|\.|\bphone|\bfrom|\band|\bvillage|\bdistrict|\bwith|$)',
            r'^([A-Za-z\u0900-\u0D7F\s]+?)\s*[:：]\s*(?:\d|\bacres|\btomato|\bwheat|\bcotton|\b1|\b2)',
            r'^([A-Za-z\u0900-\u0D7F\s]{3,25})\s+([6-9]\d{9})'
        ]
        for np in name_patterns:
            m = re.search(np, norm_text, flags=re.IGNORECASE)
            if m:
                cand = m.group(1).strip()
                cand = re.sub(r'^(?:shri|mr|mrs|smt|namaste|hello|namaskar)\b\s*', '', cand, flags=re.IGNORECASE).strip()
                cand = re.sub(r'\s*(?:hai|hoon|hath|ji|sahab|kumar|sharma)?$', '', cand, flags=re.IGNORECASE).strip()
                if len(cand) >= 2 and not any(k[0].lower() in cand.lower() for k in KNOWN_CROPS) and not re.search(r'^\d+$', cand):
                    name_cand = cand
                    break

        if name_cand:
            extracted["name"] = name_cand
            extracted["farmer_name"] = name_cand
            confidences["name"] = 0.94
            confidences["farmer_name"] = 0.94

        # 3. District Detection (Evaluated before village so districts like Nashik are not classified as villages)
        district_cand = None
        for dist_name, dist_keywords in KNOWN_DISTRICTS:
            if any(k in lower for k in dist_keywords):
                district_cand = dist_name
                break

        if not district_cand:
            dist_match = re.search(r'(?:जिला|जिले में|जिल्हा|જિલ્લો|జిల్లా|மாவட்டம்|ಜಿಲ್ಲೆ|ਜ਼ਿਲ੍ਹਾ|জেলা|ଜିଲ୍ଲା|district)\s+([A-Za-z\u0900-\u0D7F]+)', norm_text, flags=re.IGNORECASE)
            if dist_match:
                cand_d = dist_match.group(1).strip()
                if len(cand_d) >= 3 and cand_d.lower() not in ["mein", "se", "hai"]:
                    district_cand = cand_d

        if district_cand:
            extracted["district"] = district_cand
            confidences["district"] = 0.95

        # 4. Village Detection
        village_cand = None
        v_suffix = re.search(r'([A-Za-z\u0900-\u0D7F]+(?:गांव|गाव|गाँव|pur|nagar|wadi|वाडी|पुर|नगर))', norm_text, flags=re.IGNORECASE)
        if v_suffix:
            cand_v = v_suffix.group(1).strip()
            if not any(cand_v.lower() in [kw.lower() for kw in d[1]] for d in KNOWN_DISTRICTS):
                village_cand = cand_v

        if not village_cand:
            village_patterns = [
                r'(?:गाँव|गांव|गाव|गावात|ग्राम|village|gaon)\s+([A-Za-z\u0900-\u0D7F]+)',
                r'([A-Za-z\u0900-\u0D7F]+)\s*(?:गाँव से|गांव से|गावातून|गावात|village\b)',
                r'(?:in|at)\s+([A-Za-z]+),\s*(?:[A-Za-z]+)',
                r'(?:from|at)\s+([A-Za-z]+)\s+village',
                r'(?:from)\s+([A-Za-z]+)(?:,|\s+village|\s+district)'
            ]
            for vp in village_patterns:
                m = re.search(vp, norm_text, flags=re.IGNORECASE)
                if m:
                    v = m.group(1).strip()
                    if len(v) >= 2 and v.lower() not in ["se", "mein", "hai", "district", "acres", "acre", "land", "cultivating", "growing"] and not any(v.lower() in [kw.lower() for kw in d[1]] for d in KNOWN_DISTRICTS):
                        village_cand = v
                        break

        if not village_cand:
            for known_v in ["Pimpalgaon", "पिंपलगांव", "Rampur", "रामपुर", "Nandgaon", "नांदगाव", "Gondal", "Wardhannapet", "Oddanchatram", "Harihar", "Alour", "Tarakeswar", "Banki", "Raha", "Lasalgaon"]:
                if known_v.lower() in lower:
                    village_cand = known_v
                    break

        if village_cand:
            extracted["village"] = village_cand
            confidences["village"] = 0.92

        # 5. Crop Detection
        crop_cand = None
        for crop_name, keywords in KNOWN_CROPS:
            if any(k in lower for k in keywords):
                crop_cand = crop_name
                break

        if crop_cand:
            extracted["crop"] = crop_cand
            confidences["crop"] = 0.96

        # 6. Land Area / Acreage Detection & Normalization
        acres_cand = None
        # Check for contradictory acreages: e.g. "2 एकड़ या शायद 5 एकड़"
        mult_acres = re.findall(r'(\d+(?:\.\d+)?)\s*(?:acres?|acre|एकड़|एकर[ात]?|એકર|ఎకరా[లు|ల|ల్లో]?|ஏக்கர்|ஏக்கரில்|ಎಕರೆ|ਏਕੜ|একর|ଏକର|একৰ)', norm_text, flags=re.IGNORECASE)
        if len(mult_acres) > 1 and len(set(mult_acres)) > 1:
            contradictions.append(f"Contradictory acreage detected: {', '.join(mult_acres)} acres. Please clarify exact land area.")
            clarifications.append(f"जमीन का रकबा स्पष्ट करें: {mult_acres[0]} या {mult_acres[1]} एकड़?")
        else:
            acre_num_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:acres?|acre|एकड़|एकर[ात]?|એકર|ఎకరా[లు|ల|ల్లో]?|ஏக்கர்|ஏக்கரில்|ಎಕರೆ|ਏਕੜ|একর|ଏକର|একৰ|एकड़ जमीन|acre land)', norm_text, flags=re.IGNORECASE)
            if acre_num_match:
                try:
                    v = float(acre_num_match.group(1))
                    if 0.1 <= v <= 20.0:
                        acres_cand = v
                except ValueError:
                    pass

            if acres_cand is None:
                for pat, val in HINDI_NUMBER_WORDS:
                    full_pat = pat + r'\s*(?:acres?|acre|एकड़|एकर[ात]?|એકર|ఎకరా[లు|ల|ల్లో]?|ஏக்கர்|ஏக்கரில்|ಎಕರೆ|ਏਕੜ|একর|ଏକର|একৰ|एकड़ जमीन|acre land)'
                    if re.search(full_pat, norm_text, flags=re.IGNORECASE):
                        acres_cand = val
                        break

            if acres_cand is None:
                m = re.search(r'(?:मेरे पास|mere paas|पास)\s*(\d+(?:\.\d+)?)\s*(?:acre|एकड़|एकर)', norm_text, flags=re.IGNORECASE)
                if m:
                    try:
                        v = float(m.group(1))
                        if 0.1 <= v <= 20.0:
                            acres_cand = v
                    except ValueError:
                        pass

        if acres_cand is not None:
            extracted["acres"] = acres_cand
            confidences["acres"] = 0.95
            if acres_cand > 2.5:
                clarifications.append(f"सूचना: {acres_cand} एकड़ सीमांत किसान सीमा (2.5 एकड़) से अधिक है।")

        # 7. Projected Yield (Quintals)
        yield_cand = None
        yield_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:quintals?|qtl|क्विंटल|ક્વિન્ટલ|કવિન્ટલ|ಕ್ವಿಂಟಾಲ್|క్వింటా[లు|ళ్లు|ల|ళ్ల]?|குவிண்டால்|কুইন্টাল|ਕੁਇੰਟਲ|ക്വിന്റാಲ್|କ୍ୱିଣ୍ଟାଲ|কুইন্টল)', norm_text, flags=re.IGNORECASE)
        if not yield_match:
            yield_match = re.search(r'(?:yield|yields?|पैदावार|దిగుబడి|उत्पादन|ਝਾੜ|ফলন|ଅମଳ|விளைச்சல்|ಇಳುವரி)\s*(?:is|of|:)?\s*(\d+(?:\.\d+)?)', norm_text, flags=re.IGNORECASE)
        if yield_match:
            try:
                y = float(yield_match.group(1))
                if 0.5 <= y <= 120.0:
                    yield_cand = y
            except ValueError:
                pass
        if yield_cand is not None:
            extracted["projected_yield"] = yield_cand
            extracted["yield_quintals"] = yield_cand
            confidences["yield"] = 0.93
            confidences["projected_yield"] = 0.93
            confidences["yield_quintals"] = 0.93

        # 8. Costs / Expenses (Rupees)
        costs_cand = None
        cost_match = re.search(r'(\d{3,7})\s*(?:rupees?|rs\.?|₹|रुपये|रुपया|રૂપિયા|రూపాయలు|రూ|ரூபாய்|টাকা|ਟଙ୍କਾ|টকা|ਰੁਪਏ|ರೂಪಾಯಿ|ರೂ|ଟଙ୍କା)', norm_text, flags=re.IGNORECASE)
        if not cost_match:
            cost_match = re.search(r'(?:खर्च|लागत|expenses?|costs?|cost|खर्चा|ਖਰਚਾ|ఖర్చు|செலவு|খরচ|ਖਰਚ|খৰচ|ವೆಚ್ಚ)\s*(?:लगभग|लगभग है|है|हुआ है|हुआ|आया है|झाला आहे|হৈছে|হয়েছে|is|of|:)?\s*(?:₹|rs\.?|rupees?)?\s*(\d{3,7})', norm_text, flags=re.IGNORECASE)
        if not cost_match:
            cost_match = re.search(r'(\d{3,7})\s*(?:रुपये|खर्च|लागत)', norm_text, flags=re.IGNORECASE)

        if cost_match:
            try:
                c = float(cost_match.group(1).replace(",", ""))
                if 500.0 <= c <= 500000.0:
                    costs_cand = c
            except ValueError:
                pass
        if costs_cand is not None:
            extracted["input_costs"] = costs_cand
            extracted["costs"] = costs_cand
            confidences["costs"] = 0.94
            confidences["input_costs"] = 0.94

        # 9. Irrigation
        if any(w in lower for w in ["drip", "ड्रिप", "ઠિબક", "ठिबक", "డ్రిప్", "சொட்டு நீர்", "ਤੁਪਕਾ", "ಹನಿ"]):
            extracted["irrigation"] = "Drip"
            confidences["irrigation"] = 0.90
        elif any(w in lower for w in ["rain", "rainfed", "बारिश", "વરસાદ", "पाऊस", "వర్షం", "மழை", "ਮੀਂਹ", "ਮಳೆ"]):
            extracted["irrigation"] = "Rainfed"
            confidences["irrigation"] = 0.90
        elif any(w in lower for w in ["canal", "नहर", "कालवा", "కాలువ", "கால்வாய்", "ਨਹਿਰ"]):
            extracted["irrigation"] = "Canal"
            confidences["irrigation"] = 0.90

        # Target Field Fallbacks when farmer is answering a specific follow-up question
        if target_field:
            if target_field in ["yield", "yield_quintals", "projected_yield"] and "yield_quintals" not in extracted:
                num_m = re.search(r'(\d+(?:\.\d+)?)', norm_text)
                if num_m:
                    v = float(num_m.group(1))
                    if 0.5 <= v <= 120.0:
                        extracted["yield"] = v
                        extracted["yield_quintals"] = v
                        extracted["projected_yield"] = v
                        confidences["yield"] = 0.95
            elif target_field in ["costs", "input_costs"] and "costs" not in extracted:
                num_m = re.search(r'(\d{3,7})', norm_text)
                if num_m:
                    v = float(num_m.group(1))
                    extracted["costs"] = v
                    extracted["input_costs"] = v
                    confidences["costs"] = 0.95
            elif target_field == "acres" and "acres" not in extracted:
                num_m = re.search(r'(\d+(?:\.\d+)?)', norm_text)
                if num_m:
                    v = float(num_m.group(1))
                    if 0.1 <= v <= 20.0:
                        extracted["acres"] = v
                        confidences["acres"] = 0.95
            elif target_field == "phone" and "phone" not in extracted:
                p_m = re.search(r'([6-9]\d{7,11})', norm_text) or re.search(r'(\d{8,12})', norm_text)
                if p_m:
                    extracted["phone"] = p_m.group(1)
                    confidences["phone"] = 0.95
            elif target_field in ["name", "farmer_name"] and "name" not in extracted and "farmer_name" not in extracted:
                clean_n = re.sub(r'^(?:my name is|मेरा नाम|माझे नाव|नाम)\s*', '', norm_text, flags=re.IGNORECASE).strip()
                if len(clean_n) >= 2:
                    extracted["name"] = clean_n
                    extracted["farmer_name"] = clean_n
                    confidences["name"] = 0.95
            elif target_field == "village" and "village" not in extracted:
                clean_v = re.sub(r'^(?:village|गाँव|गाव|ग्राम|from|in)\s*', '', norm_text, flags=re.IGNORECASE).strip()
                if len(clean_v) >= 2:
                    extracted["village"] = clean_v
                    confidences["village"] = 0.95

        # Build missing fields and follow-ups
        required_keys = ["name", "phone", "village", "district", "crop", "acres", "yield", "costs"]
        missing: List[str] = []
        for k in required_keys:
            if k == "name":
                val = extracted.get("name") or extracted.get("farmer_name")
                cur_val = current_data.get("name") or current_data.get("farmer_name") if current_data else None
            elif k == "yield":
                val = extracted.get("yield_quintals") or extracted.get("projected_yield")
                cur_val = current_data.get("yield_quintals") or current_data.get("projected_yield") if current_data else None
            elif k == "costs":
                val = extracted.get("costs") or extracted.get("input_costs")
                cur_val = current_data.get("costs") or current_data.get("input_costs") if current_data else None
            else:
                val = extracted.get(k)
                cur_val = current_data.get(k) if current_data else None

            if val is None or (isinstance(val, str) and not val.strip()):
                if not cur_val:
                    missing.append(k)
                    if len(clarifications) < 3:
                        prompt_map = FOLLOWUP_QUESTIONS.get(k, {})
                        if prompt_map:
                            clarifications.append(prompt_map.get(lang_code, prompt_map.get("hi", f"Please provide {k}.")))

        # Handle proposed changes / conflicts with current_data using numerical tolerance
        def _values_conflict(v1: Any, v2: Any) -> bool:
            if v1 is None or v2 is None:
                return False
            try:
                f1, f2 = float(v1), float(v2)
                return abs(f1 - f2) > 0.05
            except (ValueError, TypeError):
                s1 = str(v1).strip().lower()
                s2 = str(v2).strip().lower()
                return s1 != "" and s2 != "" and s1 != s2

        proposed_changes: Dict[str, Any] = {}
        if current_data:
            canonical_check = {
                "name": extracted.get("name") or extracted.get("farmer_name"),
                "phone": extracted.get("phone"),
                "village": extracted.get("village"),
                "district": extracted.get("district"),
                "crop": extracted.get("crop"),
                "acres": extracted.get("acres"),
                "yield_quintals": extracted.get("yield_quintals") or extracted.get("projected_yield"),
                "costs": extracted.get("costs") or extracted.get("input_costs"),
                "irrigation": extracted.get("irrigation")
            }
            for k, new_v in canonical_check.items():
                if new_v is not None:
                    curr_v = current_data.get(k)
                    if curr_v is None and k == "name":
                        curr_v = current_data.get("farmer_name")
                    elif curr_v is None and k == "yield_quintals":
                        curr_v = current_data.get("projected_yield") or current_data.get("yield")
                    elif curr_v is None and k == "costs":
                        curr_v = current_data.get("input_costs")

                    if curr_v is not None and str(curr_v).strip() != "" and _values_conflict(curr_v, new_v):
                        proposed_changes[k] = {
                            "current": curr_v,
                            "spoken": new_v
                        }

        # Merge mapped fields: only keep what was in current_data or newly extracted
        # If there is a proposed change/conflict, preserve current_data until explicitly accepted
        mapped_fields: Dict[str, Any] = dict(current_data) if current_data else {}
        for k, v in extracted.items():
            canon = "name" if k == "farmer_name" else ("costs" if k == "input_costs" else ("yield_quintals" if k in ["projected_yield", "yield"] else k))
            if canon not in proposed_changes:
                mapped_fields[k] = v

        # Generate clean confirmation summary in farmer's language
        summary_text = VoiceNLPService.generate_confirmation_summary(extracted, lang_code)
        
        # Get one specific follow-up question if required fields are missing
        followup = VoiceNLPService.get_single_followup(missing, lang_code)

        return {
            "mapped_fields": mapped_fields,
            "extracted_fields": extracted,
            "proposed_changes": proposed_changes,
            "confidence_scores": confidences,
            "missing_fields": missing,
            "clarifications": clarifications,
            "contradictions": contradictions,
            "raw_transcript": raw,
            "confirmation_summary": summary_text,
            "followup_question": followup,
            "requires_review": True
        }

    @staticmethod
    def generate_confirmation_summary(data: Dict[str, Any], lang_code: str = "hi") -> str:
        """Generate a concise, human-friendly summary of the populated fields in the farmer's language."""
        name = data.get("name") or data.get("farmer_name")
        phone = data.get("phone")
        crop = data.get("crop")
        acres = data.get("acres")
        yield_val = data.get("yield_quintals") or data.get("projected_yield") or data.get("yield")
        costs = data.get("costs") or data.get("input_costs")
        village = data.get("village")
        district = data.get("district")

        parts = []
        if lang_code == "hi":
            if name: parts.append(f"नाम: {name}")
            if phone: parts.append(f"फोन: {phone}")
            if crop: parts.append(f"फसल: {crop}")
            if acres: parts.append(f"जमीन: {acres} एकड़")
            if village: parts.append(f"गाँव: {village}")
            if district: parts.append(f"जिला: {district}")
            if yield_val: parts.append(f"उपज: {yield_val} क्विंटल/एकड़")
            if costs: parts.append(f"कुल खर्च: ₹{int(costs):,}")
            return " • ".join(parts) if parts else "कोई विवरण प्राप्त नहीं हुआ।"
        elif lang_code == "mr":
            if name: parts.append(f"नाव: {name}")
            if phone: parts.append(f"फोन: {phone}")
            if crop: parts.append(f"पीक: {crop}")
            if acres: parts.append(f"जमीन: {acres} एकर")
            if village: parts.append(f"गाव: {village}")
            if district: parts.append(f"जिल्हा: {district}")
            if yield_val: parts.append(f"उत्पादन: {yield_val} क्विंटल/एकर")
            if costs: parts.append(f"खर्च: ₹{int(costs):,}")
            return " • ".join(parts) if parts else "माहिती उपलब्ध नाही."
        elif lang_code == "gu":
            if name: parts.append(f"નામ: {name}")
            if phone: parts.append(f"ફોન: {phone}")
            if crop: parts.append(f"પાક: {crop}")
            if acres: parts.append(f"જમીન: {acres} એકર")
            if village: parts.append(f"ગામ: {village}")
            if district: parts.append(f"જિલ્લો: {district}")
            if yield_val: parts.append(f"ઉપજ: {yield_val} ક્વિન્ટલ/એકર")
            if costs: parts.append(f"ખર્ચ: ₹{int(costs):,}")
            return " • ".join(parts) if parts else "માહિતી ઉપલબ્ધ નથી."
        else: # default English
            if name: parts.append(f"Name: {name}")
            if phone: parts.append(f"Phone: {phone}")
            if crop: parts.append(f"Crop: {crop}")
            if acres: parts.append(f"Land: {acres} acre{'s' if acres > 1 else ''}")
            if village: parts.append(f"Village: {village}")
            if district: parts.append(f"District: {district}")
            if yield_val: parts.append(f"Yield: {yield_val} quintals/acre")
            if costs: parts.append(f"Expenses: ₹{int(costs):,}")
            return " • ".join(parts) if parts else "No details detected."

    @staticmethod
    def get_single_followup(missing_fields: List[str], lang_code: str = "hi") -> Optional[Dict[str, str]]:
        """Return exactly one short, specific follow-up question for the first missing required field."""
        if not missing_fields:
            return None
        first_missing = missing_fields[0]
        q_map = FOLLOWUP_QUESTIONS.get(first_missing, {})
        q_text = q_map.get(lang_code, q_map.get("en", f"Please provide {first_missing}."))
        labels = {
            "name": {"en": "Farmer Name", "hi": "किसान का नाम"},
            "phone": {"en": "Phone Number", "hi": "मोबाइल नंबर"},
            "village": {"en": "Village", "hi": "गाँव का नाम"},
            "district": {"en": "District", "hi": "जिला"},
            "crop": {"en": "Cultivated Crop", "hi": "फसल"},
            "acres": {"en": "Land Acreage", "hi": "जमीन का रकबा"},
            "yield": {"en": "Expected Yield", "hi": "अनुमानित पैदावार"},
            "costs": {"en": "Cultivation Expenses", "hi": "कुल खर्च"}
        }
        lbl = labels.get(first_missing, {}).get(lang_code, labels.get(first_missing, {}).get("en", first_missing))
        return {
            "field": first_missing,
            "question": q_text,
            "field_label": lbl
        }

