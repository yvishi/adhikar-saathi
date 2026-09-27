# Hindi strings written by the multilingual agent (please verify)

- `app/frontend/app.js` STRINGS `lang.label` (label on the new answer-language selector next to
  the mic button): जवाब की भाषा  (English: "Answer language")

New Hindi added while adding non-Hindi answer languages (Punjabi, Bengali, Marathi). None of
this is spoken to users in a normal answer flow except REFUSE-style fallback text; both lines
below are used only when a non-Hindi, non-English language is selected.

- `app/backend/prompts.py` `LANG_DISCLAIMER_HI` (secondary disclaimer line shown under every
  answer/clarify in a non-Hindi, non-English language; deliberately does NOT name the specific
  language, to avoid needing new per-language Hindi vocabulary):
  यह जवाब AI ने किसी दूसरी भाषा में बनाया है; इसकी जाँच किसी व्यक्ति ने नहीं की है। सिर्फ़ हिंदी और अंग्रेज़ी जवाब जाँचे गए हैं।
  (Intended meaning: "This answer was made by AI in another language; no person has checked
  it. Only the Hindi and English answers have been checked.")

- `app/backend/prompts.py` `LANG_VERIFY_FAIL_HI` (shown only when env `LANG_VERIFY=1` and the
  back-translation safety check fails, downgrading an answer/clarify to a refusal):
  इस भाषा में बना जवाब अपने-आप जाँचा नहीं जा सका, इसलिए ग़लत जवाब के खतरे से बचने के लिए इसे नहीं दिखाया जा रहा। कृपया हिंदी या अंग्रेज़ी में फिर से पूछें, वहाँ जवाब जाँचे गए हैं।
  (Intended meaning: "The answer generated in this language could not be automatically
  checked, so to avoid the risk of a wrong answer it is not being shown. Please ask again in
  Hindi or English, where answers are verified.")

Everything a user actually hears/reads in Punjabi, Bengali or Marathi is model-generated at
answer time and CANNOT be pre-listed here (it is not written by this agent, and this agent
cannot read those languages either). See `app/data/language_review/INDEX.md` for what a native
speaker of each new language still needs to check, and the sample outputs with English glosses
in this agent's final report for the live-verified examples.
