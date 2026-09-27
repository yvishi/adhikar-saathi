# Hindi written by the integration agent (please verify)

Only one UI string was changed; everything else below is Hindi used in scripts or tests, copied from strings other agents already listed.

- app/frontend/app.js, STRINGS.hi['q.age.u18'] (schemes flow, first age option): 16 या 17 साल  ->  16 or 17 years.
  Why: the old label "18 साल से कम" (under 18) was sent as age 16, so a 10-year-old would be told "likely eligible" for e-Shram (minimum age 16 in the sources). The option now says exactly what age it stands for. Also listed in frontend.md line for [q.age.u18].
- scripts/prewarm_demo.py DEMO questions (copied from the eval set / earlier live tests, all typed as text): आज क्रिकेट मैच का स्कोर क्या है? · काम पर एक आदमी मुझे परेशान करता है। / वो मेरा सुपरवाइज़र है। शिकायत कहाँ करूँ? · मेरे ठेकेदार ने तीन महीने से मजदूरी नहीं दी, मैं क्या करूँ?
- app/backend/tests/test_pipeline.py test_strip_ids_removes_dangling_lead_in, sample sentence only: हाँ, आप रजिस्टर कर सकते हैं। S-01 के अनुसार, 16 साल या उससे अधिक उम्र वाले जुड़ सकते हैं।
- app/backend/pipeline.py `_ID_RE` now also deletes the phrase "के अनुसार" (= "according to") when it directly follows a removed card id, so the model's "S-01 के अनुसार," does not leave a dangling "के अनुसार,". The prompt in prompts.py stays English.
- app/backend/retrieval.py glossary: added Latin keys "fine", "fined", "penalty" -> "fine deduction" (no Hindi).
- Ad-hoc typed live test questions, not stored in the repo: मैं 45 साल का हूँ, क्या मैं पीएम श्रम योगी मानधन पेंशन में जुड़ सकता हूँ? · मैं 17 साल का हूँ, क्या मैं ई-श्रम में रजिस्टर कर सकता हूँ? · PM-SYM में हर महीने कितने रुपये जमा करने होंगे? · मेरी उम्र 30 साल है और मैं 12000 कमाता हूँ, क्या मुझे पीएम-एसवाईएम मिल सकता है · और अगर वो मना कर दे तो? · मजदूरी नहीं मिली तो क्या करें? (the last one was also spoken by Sarvam TTS as the synthetic-voice test question)
