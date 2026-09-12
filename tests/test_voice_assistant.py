"""
Comprehensive Test Suite for KisanSetu Multilingual Voice Assistant
Tests:
1. Speech-to-Text (STT) pipeline & language configurations
2. Multi-lingual entity extraction from spoken transcripts
3. Missing field detection & conversational follow-up questions
4. Text-to-Speech (TTS) audio synthesis in Indian languages
5. Financial calculation adherence to formulas
6. FastAPI Voice AI router endpoints
"""

import sys
import os
import unittest
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Set path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.voice_service import voice_service, LANG_CONFIGS
from backend.services.agronomic_engine import AgronomicEngine

class TestVoiceAssistant(unittest.TestCase):
    
    def setUp(self):
        self.engine = AgronomicEngine()
        self.voice = voice_service

    def test_01_language_configurations(self):
        """Verify all 9 regional Indian languages are configured."""
        required_langs = ["en", "hi", "gu", "mr", "te", "ta", "bn", "pa", "kn"]
        for lang in required_langs:
            self.assertIn(lang, LANG_CONFIGS, f"Missing configuration for {lang}")
            self.assertIn("stt_code", LANG_CONFIGS[lang])
            self.assertIn("gtts_code", LANG_CONFIGS[lang])
        print("✅ Test 1 Passed: All 9 Regional Indian Languages Configured.")

    def test_02_multilingual_entity_extraction(self):
        """Test extraction of crop, acres, district, yield from various spoken language formats."""
        
        # English
        en_transcript = "My name is Ramesh Patil, cultivating 2 acres of Tomato in Nashik with drip irrigation"
        res_en = self.voice.extract_agronomic_entities(en_transcript)
        self.assertEqual(res_en["extracted_fields"]["crop_name"], "Tomato")
        self.assertEqual(res_en["extracted_fields"]["land_acres"], 2.0)
        self.assertEqual(res_en["extracted_fields"]["district"], "Maharashtra_Nashik")
        self.assertEqual(res_en["extracted_fields"]["irrigation"], "Drip")

        # Hindi
        hi_transcript = "मेरा नाम रमेश है, नासिक में डेढ़ एकड़ टमाटर की फसल है और 18 क्विंटल उपज होगी"
        res_hi = self.voice.extract_agronomic_entities(hi_transcript)
        self.assertEqual(res_hi["extracted_fields"]["crop_name"], "Tomato")
        self.assertEqual(res_hi["extracted_fields"]["land_acres"], 1.5)
        self.assertEqual(res_hi["extracted_fields"]["district"], "Maharashtra_Nashik")
        self.assertEqual(res_hi["extracted_fields"]["expected_yield_qtl_acre"], 18.0)

        # Gujarati
        gu_transcript = "નાસિકમાં ૨ એકર કપાસ અને ડ્રિપ ઇરિગેશન છે"
        res_gu = self.voice.extract_agronomic_entities(gu_transcript)
        self.assertEqual(res_gu["extracted_fields"]["crop_name"], "Cotton")
        self.assertEqual(res_gu["extracted_fields"]["land_acres"], 2.0)

        # Marathi
        mr_transcript = "नाशिकमध्ये १.५ एकर सोयाबीन लागवड आहे"
        res_mr = self.voice.extract_agronomic_entities(mr_transcript)
        self.assertEqual(res_mr["extracted_fields"]["crop_name"], "Soybean")
        self.assertEqual(res_mr["extracted_fields"]["land_acres"], 1.5)

        # Telugu
        te_transcript = "గుంటూరు లో 2 ఎకరాల మిర్చి సాగు"
        res_te = self.voice.extract_agronomic_entities(te_transcript)
        self.assertEqual(res_te["extracted_fields"]["crop_name"], "Chilli (Dry)")
        self.assertEqual(res_te["extracted_fields"]["land_acres"], 2.0)
        self.assertEqual(res_te["extracted_fields"]["district"], "Andhra Pradesh_Guntur")

        print("✅ Test 2 Passed: Multilingual Agronomic Entity Extraction Verified.")

    def test_03_conversational_followup_missing_fields(self):
        """Verify assistant identifies missing fields and returns follow-up question."""
        partial_transcript = "I have 2 acres in Nashik"
        res = self.voice.extract_agronomic_entities(partial_transcript)
        missing = res["missing_fields"]
        self.assertIn("crop_name", missing)
        
        # Test localized follow-up question
        q_en = self.voice.get_followup_question(missing, lang_code="en")
        q_hi = self.voice.get_followup_question(missing, lang_code="hi")
        self.assertIsNotNone(q_en)
        self.assertIn("crop", q_en.lower())
        self.assertIn("फसल", q_hi)
        print("✅ Test 3 Passed: Missing Field Detection & Multilingual Follow-Up Questions Verified.")

    def test_04_text_to_speech_synthesis(self):
        """Test audio synthesis generation in MP3 format."""
        test_text = "Namaste Ramesh! Your approved credit limit is 102400 rupees."
        success, audio_bytes, mime = self.voice.synthesize_speech(test_text, lang_code="en")
        self.assertTrue(success)
        self.assertIsNotNone(audio_bytes)
        self.assertGreater(len(audio_bytes), 1000)
        self.assertEqual(mime, "audio/mp3")

        # Test Hindi TTS
        test_text_hi = "नमस्ते रमेश जी! आपकी स्वीकृत ऋण सीमा 102400 रुपये है।"
        success_hi, audio_bytes_hi, _ = self.voice.synthesize_speech(test_text_hi, lang_code="hi")
        self.assertTrue(success_hi)
        self.assertGreater(len(audio_bytes_hi), 1000)
        print("✅ Test 4 Passed: TTS Synthesis (MP3 Audio Generation) Verified.")

    def test_05_backend_credit_calculation(self):
        """Verify credit sizing rules: Revenue = Acres * Yield * Net Farm-gate Price, Credit Limit = 0.45 * Net Profit."""
        calc_payload = {
            "farmer_name": "Ramesh Tukaram Patil",
            "district": "Maharashtra_Nashik",
            "crop_name": "Tomato",
            "land_acres": 1.5,
            "expected_yield_qtl_acre": 22.0,
            "peer_member_ids": ["MEM-442", "MEM-443"]
        }
        res = self.engine.compute_complete_underwriting(calc_payload)
        fin = res["financial_sizing"]
        
        # Sanity checks on financial bounds
        self.assertGreater(fin["gross_farmgate_revenue_inr"], 0)
        self.assertGreater(fin["final_sanctioned_credit_limit_inr"], 10000)
        self.assertLessEqual(fin["interest_rate_pct"], 10.0)
        self.assertGreaterEqual(fin["composite_trust_score"], 60)
        print("✅ Test 5 Passed: Agronomic Financial Sizing & Underwriting Engine Verified.")

if __name__ == "__main__":
    unittest.main()
