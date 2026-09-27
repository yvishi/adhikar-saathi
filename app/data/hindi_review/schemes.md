# Hindi strings written by the schemes agent (NEEDS-REVIEW)

All are in `app/backend/complaint.py`, in `draft_hi` (the Hindi wage-claim letter). `{...}` are filled from the worker's form; missing ones show as `[ ____ ]`. `schemes.py` contains no Hindi (`why_hi` is always null).

Please check: wording is simple and polite, "मजदूरी संहिता, 2019" is the right Hindi name for the Code on Wages, 2019, and the gender-neutral "करता/करती" reads acceptably.

| # | Where used (line in letter) | String |
|---|---|---|
| 1 | Salutation line 1 | सेवा में, |
| 2 | Addressee (authority under the Code, no named office) | प्राधिकारी (मजदूरी संहिता, 2019 के अंतर्गत नियुक्त) |
| 3 | State line | राज्य: {state} |
| 4 | Subject line | विषय: बकाया मजदूरी के भुगतान के लिए आवेदन |
| 5 | Greeting | महोदय/महोदया, |
| 6 | Body 1 (who, employer, work, period) | मैं {worker_name}, {employer_name} के यहाँ {work_type} का काम करता/करती थी। मैंने {period_from} से {period_to} तक काम किया। |
| 7 | Body 2 (amount) | इस अवधि की मेरी ₹{amount} की मजदूरी मुझे अभी तक नहीं मिली है। |
| 8 | Optional details line (only if the worker wrote details) | विवरण: {details} |
| 9 | Request | मेरा निवेदन है कि मेरे नियोक्ता से मेरी बकाया मजदूरी दिलवाई जाए। मैं ज़रूरी कागज़ात देने को तैयार हूँ। |
| 10 | Sign-off | भवदीय, |
| 11 | Sign-off name | {worker_name} |
| 12 | Date placeholder line | तारीख: [ ____ ] |
| 13 | Address placeholder line | पता और फ़ोन नंबर: [ ____ ] |

English gloss of the whole letter: see `draft_en` in the same function (same structure, line for line).
