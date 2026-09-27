"""API error type and the Hindi+English message table (Hindi strings are listed in
app/data/hindi_review/backend-core.md for the owner to verify)."""

MESSAGES = {
    "stt_failed": (
        "अभी आवाज़ समझने में दिक्कत आ रही है। कृपया थोड़ी देर बाद कोशिश करें।",
        "Speech recognition failed. Please try again in a little while.",
        502,
    ),
    "llm_failed": (
        "अभी जवाब तैयार नहीं हो पा रहा। कृपया थोड़ी देर बाद कोशिश करें।",
        "The answer service failed. Please try again in a little while.",
        502,
    ),
    "tts_failed": (
        "आवाज़ बनाने में दिक्कत आई। आप लिखा हुआ जवाब पढ़ सकते हैं।",
        "Text-to-speech failed. You can read the written answer instead.",
        502,
    ),
    "bad_request": (
        "अनुरोध सही नहीं है। कृपया अपना सवाल बोलें या लिखें।",
        "Bad request. Please speak or type your question.",
        400,
    ),
    "rate_limited": (
        "अभी बहुत ज़्यादा इस्तेमाल हो रहा है। कृपया थोड़ी देर बाद कोशिश करें।",
        "Rate limit reached. Please try again in a little while.",
        429,
    ),
    "audio_too_long": (
        "रिकॉर्डिंग बहुत लंबी है। कृपया 30 सेकंड से छोटा सवाल बोलें।",
        "The recording is too long. Please keep the question under 30 seconds.",
        400,
    ),
    "no_speech": (
        "आवाज़ सुनाई नहीं दी। कृपया दोबारा बोलें।",
        "No speech was detected. Please speak again.",
        422,
    ),
}

# Used when Sarvam says the audio itself is unreadable (HTTP 400 that is not "too long").
AUDIO_UNREADABLE_HI = "यह रिकॉर्डिंग पढ़ी नहीं जा सकी। कृपया दोबारा बोलें।"
AUDIO_UNREADABLE_EN = "The recording could not be read. Please record again."


class AppError(Exception):
    def __init__(self, code: str, message_en: str | None = None, message_hi: str | None = None,
                 status: int | None = None):
        hi, en, st = MESSAGES[code]
        self.code = code
        self.message_hi = message_hi or hi
        self.message_en = message_en or en
        self.status = status or st
        super().__init__(f"{code}: {self.message_en}")

    def payload(self) -> dict:
        return {"error": {"code": self.code, "message_hi": self.message_hi, "message_en": self.message_en}}
