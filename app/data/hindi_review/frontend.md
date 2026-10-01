# Hindi strings to verify: frontend agent

Source of truth: the `STRINGS` object in `app/frontend/app.js` (edit `hi` values there). English subtitle is the `en` value under the same key.
All Hindi is unreviewed; simple wording was chosen on purpose. Please check spelling, tone and whether a worker would understand each line.

## UI strings (shown to every user)

| Where used [key] | Hindi | English |
|---|---|---|
| Skip link (accessibility) [skip] | मुख्य भाग पर जाएँ | Skip to main content |
| Header brand + page title [brand] | अधिकार साथी | Adhikar Saathi |
| Helpline button in header [helpline.sub] | हेल्पलाइन | Helpline |
| Helpline button in header [helpline.aria] | हेल्पलाइन 14434 पर फ़ोन करें | Call helpline 14434 |
| Bottom tab bar [nav.ask] | पूछें | Ask |
| Bottom tab bar [nav.schemes] | योजनाएँ | Schemes |
| Bottom tab bar [nav.complaint] | शिकायत | Complaint |
| Ask screen [home.title] | अपना सवाल पूछिए | Ask your question |
| Ask screen [home.tapStart] | बोलने के लिए माइक दबाइए | Tap the mic to speak |
| Ask screen [home.orType] | या यहाँ लिखकर पूछिए | Or type your question |
| Ask screen [home.placeholder] | जैसे: मज़दूरी नहीं मिली | e.g. my wages are not paid |
| Ask screen [home.send] | भेजिए | Send |
| Ask screen [home.voiceReply] | जवाब आवाज़ में सुनाइए | Speak the answer aloud |
| Ask screen, mic status while recording [rec.requesting] | माइक की अनुमति दीजिए… | Please allow the microphone… |
| Ask screen, mic status while recording [rec.recording] | बोलिए… पूरा होने पर माइक फिर दबाइए | Speak now. Tap the mic again when done. |
| Ask screen, mic status while recording [rec.startA11y] | बोलना शुरू कीजिए | Start speaking |
| Ask screen, mic status while recording [rec.stopA11y] | रिकॉर्डिंग रोकिए | Stop recording |
| Ask screen, mic status while recording [rec.left] | सेकंड बाकी | seconds left |
| Ask screen, mic status while recording [rec.thinking] | सोच रहा हूँ… थोड़ा रुकिए | Thinking… please wait |
| Answer view [ans.youSaid] | आपने कहा | You said |
| Answer view [ans.answer] | जवाब | Answer |
| Answer view [ans.clarifyLabel] | मुझे एक बात पूछनी है | I need to ask one thing |
| Answer view [ans.clarifyNext] | जवाब देने के लिए माइक दबाइए | Tap the mic to reply |
| Answer view [ans.refuseLabel] | इसका जवाब मेरे पास नहीं है | I do not have an answer for this |
| Answer view [ans.refuseHelp] | 14434 सिर्फ़ ई-श्रम हेल्पडेस्क है। | 14434 is the e-Shram helpdesk only. |
| Answer view [ans.play] | सुनिए | Play |
| Answer view [ans.pause] | रोकिए | Pause |
| Answer view [ans.replay] | फिर से सुनिए | Play again |
| Answer view [ans.tapToListen] | सुनने के लिए बटन दबाइए | Tap the button to listen |
| Answer view [ans.sources] | जानकारी कहाँ से है | Where this comes from |
| Answer view [ans.openSource] | स्रोत खोलिए | Open source |
| Answer view [ans.showEn] | अंग्रेज़ी में देखिए | English (for verification) |
| Answer view [ans.hideEn] | अंग्रेज़ी छिपाइए | Hide English |
| Answer view [ans.newQuestion] | नया सवाल पूछिए | Ask a new question |
| Footer judge toggle (English-only label) [judge.label] | Judge view | Judge view |
| Error card [err.title] | कुछ गड़बड़ हुई | Something went wrong |
| Error card [err.retry] | फिर से कोशिश कीजिए | Try again |
| Error card [err.typeInstead] | लिखकर पूछिए | Type instead |
| Error card [err.micDenied] | माइक की अनुमति नहीं मिली। फ़ोन की सेटिंग में माइक चालू कीजिए, या नीचे लिखकर पूछिए। | Microphone permission was denied. Turn it on in the browser settings, or type your question below. |
| Error card [err.noMic] | इस फ़ोन में माइक नहीं चल रहा। नीचे लिखकर पूछिए। | No working microphone was found. Type your question below. |
| Error card [err.unsupported] | इस ब्राउज़र में रिकॉर्डिंग नहीं चलती। नीचे लिखकर पूछिए। | This browser cannot record audio. Type your question below. |
| Error card [err.tooShort] | आवाज़ बहुत छोटी थी। फिर से बोलिए। | The recording was too short. Please speak again. |
| Error card [err.noNetwork] | इंटरनेट नहीं चल रहा। थोड़ी देर बाद फिर कोशिश कीजिए। | No internet connection. Please try again in a while. |
| Error card [err.rateLimited] | अभी बहुत लोग पूछ रहे हैं। थोड़ी देर रुककर फिर कोशिश कीजिए। | Too many people are asking right now. Please wait a little and try again. |
| Error card [err.noSpeech] | आवाज़ सुनाई नहीं दी। माइक के पास बोलिए और फिर कोशिश कीजिए। | No speech was heard. Speak close to the microphone and try again. |
| Error card [err.tooLong] | रिकॉर्डिंग बहुत लंबी थी। 30 सेकंड से छोटा सवाल पूछिए। | The recording was too long. Ask a question shorter than 30 seconds. |
| Error card [err.generic] | कुछ गड़बड़ हो गई। फिर से कोशिश कीजिए। | Something went wrong. Please try again. |
| Error card [err.emptyText] | पहले अपना सवाल लिखिए। | Please write your question first. |
| Fixed footer notice [notice.legal] | यह जानकारी है, कानूनी सलाह नहीं। | This is information, not legal advice. |
| Fixed footer notice [notice.privacy] | आपका सवाल Sarvam AI से प्रोसेस होता है। अपना नाम, आधार या फ़ोन नंबर न बोलिए। | Your question is processed by Sarvam AI. Do not say your name, Aadhaar or phone number. |
| Check my schemes flow [sch.title] | अपनी योजनाएँ जाँचिए | Check my schemes |
| Check my schemes flow [sch.intro] | कुछ सवालों के जवाब दीजिए। नाम या नंबर नहीं पूछा जाएगा। | Answer a few questions. No name or number is asked. |
| Check my schemes flow [sch.progress] | सवाल {n} / {total} | Question {n} of {total} |
| Check my schemes flow [sch.back] | पीछे | Back |
| Check my schemes flow [sch.restart] | फिर से जाँचिए | Check again |
| Check my schemes flow [sch.checking] | जाँच रहा हूँ… | Checking… |
| Check my schemes flow [sch.results] | आपके लिए नतीजे | Your results |
| Check my schemes flow [sch.eligYes] | पात्र हो सकते हैं | Likely eligible |
| Check my schemes flow [sch.eligNo] | पात्र नहीं | Not eligible |
| Check my schemes flow [sch.eligUnknown] | पक्का नहीं | Not sure |
| Check my schemes flow [sch.missing] | और जानकारी चाहिए | More information needed |
| Check my schemes flow [sch.askAbout] | इस योजना के बारे में पूछिए | Ask about this scheme |
| Check my schemes flow [sch.askQuery] | मुझे {scheme} के बारे में बताइए | Tell me about {scheme} |
| Check my schemes flow [sch.disclaimer] | यह अंदाज़ा है। पक्का फ़ैसला सरकारी दफ़्तर करता है। | This is an estimate. The final decision is made by the government office. |
| Check my schemes flow [sch.noMatches] | अभी कोई योजना नहीं मिली। | No schemes found right now. |
| Check my schemes flow, question/options [q.age] | आपकी उम्र कितनी है? | How old are you? |
| Check my schemes flow, question/options [q.age.u18] | 16 या 17 साल (changed by the integration agent, was "18 साल से कम") | 16 or 17 years |
| Check my schemes flow, question/options [q.age.18_40] | 18 से 40 साल | 18 to 40 years |
| Check my schemes flow, question/options [q.age.41_59] | 41 से 59 साल | 41 to 59 years |
| Check my schemes flow, question/options [q.age.60] | 60 साल या ज़्यादा | 60 years or older |
| Check my schemes flow, question/options [q.income] | हर महीने की कमाई कितनी है? | What is your monthly income? |
| Check my schemes flow, question/options [q.income.low] | ₹8,000 तक | Up to Rs 8,000 |
| Check my schemes flow, question/options [q.income.mid] | ₹8,001 से ₹15,000 | Rs 8,001 to Rs 15,000 |
| Check my schemes flow, question/options [q.income.high] | ₹15,000 से ज़्यादा | More than Rs 15,000 |
| Check my schemes flow, question/options [q.work] | आप क्या काम करते हैं? | What work do you do? |
| Check my schemes flow, question/options [q.work.daily] | दिहाड़ी मज़दूर | Daily-wage worker |
| Check my schemes flow, question/options [q.work.construction] | निर्माण (बिल्डिंग) मज़दूर | Construction worker |
| Check my schemes flow, question/options [q.work.domestic] | घरेलू कामगार | Domestic worker |
| Check my schemes flow, question/options [q.work.other] | कोई और काम | Other work |
| Check my schemes flow, question/options [q.epfo] | क्या आप EPFO या ESIC के सदस्य हैं? | Are you an EPFO or ESIC member? |
| Check my schemes flow, question/options [q.tax] | क्या आप इनकम टैक्स भरते हैं? | Do you pay income tax? |
| Check my schemes flow, question/options [q.yes] | हाँ | Yes |
| Check my schemes flow, question/options [q.no] | नहीं | No |
| Check my schemes flow, question/options [q.unsure] | पता नहीं | Not sure |
| Check my schemes flow, question/options [q.preg] | क्या आप गर्भवती हैं? | Are you pregnant? |
| Check my schemes flow, question/options [q.preg.yes] | हाँ | Yes |
| Check my schemes flow, question/options [q.preg.no] | नहीं / लागू नहीं | No / not applicable |
| Write a complaint flow [cmp.title] | शिकायत का मसौदा बनाइए | Write a complaint |
| Write a complaint flow [cmp.intro] | जानकारी भरिए। हम शिकायत का मसौदा बनाएँगे। यह कहीं भेजा नहीं जाएगा। | Fill in the details. We prepare a draft. Nothing is sent anywhere. |
| Write a complaint flow [cmp.worker_name] | आपका नाम (खाली छोड़ सकते हैं) | Your name (optional) |
| Write a complaint flow [cmp.worker_name.hint] | नाम खाली छोड़ सकते हैं। छापने के बाद हाथ से लिख लीजिए। | You may leave the name empty and write it by hand after printing. |
| Write a complaint flow [cmp.state] | राज्य | State |
| Write a complaint flow [cmp.employer_name] | मालिक या ठेकेदार का नाम | Employer or contractor name |
| Write a complaint flow [cmp.work_type] | काम का प्रकार | Type of work |
| Write a complaint flow [cmp.wage_owed_inr] | बकाया मज़दूरी (₹) | Wages owed (Rs) |
| Write a complaint flow [cmp.period_from] | कब से | From date |
| Write a complaint flow [cmp.period_to] | कब तक | To date |
| Write a complaint flow [cmp.details] | पूरी बात लिखिए | Tell us what happened |
| Write a complaint flow [cmp.make] | मसौदा बनाइए | Create draft |
| Write a complaint flow [cmp.making] | बना रहा हूँ… | Creating… |
| Write a complaint flow [cmp.needOne] | कम से कम बकाया राशि या पूरी बात लिखिए। | Enter at least the wages owed or what happened. |
| Write a complaint flow [cmp.reviewBanner] | हर लाइन ध्यान से पढ़िए, फिर इस्तेमाल कीजिए। | Review every line before you use this. |
| Write a complaint flow [cmp.notSent] | यह कहीं भेजा नहीं गया है। | Nothing has been sent or filed. |
| Write a complaint flow [cmp.hindiDraft] | हिंदी मसौदा | Hindi draft |
| Write a complaint flow [cmp.englishDraft] | अंग्रेज़ी मसौदा | English draft |
| Write a complaint flow [cmp.checklist] | इस्तेमाल से पहले जाँचिए | Check before you use it |
| Write a complaint flow [cmp.print] | छापिए | Print |
| Write a complaint flow [cmp.copy] | कॉपी कीजिए | Copy |
| Write a complaint flow [cmp.copied] | कॉपी हो गया | Copied |
| Write a complaint flow [cmp.edit] | जानकारी बदलिए | Change details |

## Query text sent to the assistant when the user taps "Ask about this scheme"

- `sch.askQuery` above: `मुझे {scheme} के बारे में बताइए` (scheme name is inserted, e.g. e-Shram)

## Mock-mode-only Hindi (used only with `?mock=1`, never shown with the real backend)

| Where used | Hindi |
|---|---|
| mock transcript | मेरे मालिक ने तीन महीने से मज़दूरी नहीं दी। मैं क्या करूँ? |
| mock answer_hi (type answer) | तय न्यूनतम मज़दूरी से कम देना कानून के खिलाफ़ है। आपको समय पर पूरी मज़दूरी पाने का हक़ है। बकाया मज़दूरी का दावा तीन साल के अंदर करना होता है। |
| mock answer_hi (type clarify) | आप कहाँ काम करते हैं: निर्माण साइट पर या किसी के घर में? |
| mock answer_hi (type refuse) | माफ़ कीजिए, इस बारे में मेरे पास पक्की जानकारी नहीं है। ई-श्रम हेल्पडेस्क 14434 से आप ई-श्रम के बारे में पूछ सकते हैं। |
| mock error no_speech message_hi | आवाज़ सुनाई नहीं दी। माइक के पास बोलिए और फिर कोशिश कीजिए। |
| mock error audio_too_long message_hi | रिकॉर्डिंग बहुत लंबी थी। 30 सेकंड से छोटा सवाल पूछिए। |
| mock error rate_limited message_hi | अभी बहुत लोग पूछ रहे हैं। थोड़ी देर रुककर फिर कोशिश कीजिए। |
| mock error stt_failed message_hi | आपकी आवाज़ समझ नहीं आई। फिर से कोशिश कीजिए। |
| mock complaint draft_hi (template line 1) | सेवा में, श्रम अधिकारी |
| mock complaint draft_hi (subject) | विषय: बकाया मज़दूरी के भुगतान के लिए प्रार्थना |
| mock complaint draft_hi (body, name/state/employer inserted) | मैं …, … में … के यहाँ … का काम करता/करती हूँ। … से … तक की मेरी … मज़दूरी बाकी है। |
| mock complaint draft_hi (closing) | कृपया मेरी बकाया मज़दूरी दिलवाइए। |
| mock complaint draft_hi (signature) | हस्ताक्षर: ________ |
| mock complaint sample details (demo state only) | तीन महीने से मज़दूरी नहीं मिली। |
| mock sample question (demo state only) | मज़दूरी नहीं मिली |

## HTML

- `index.html` page title: `अधिकार साथी | Adhikar Saathi`

## Added in the UI redesign (2026-10-01): please review
| Where used | Hindi |
|---|---|
| Welcome title | नमस्ते! मैं अधिकार साथी हूँ। |
| Welcome line | मज़दूरी, सरकारी योजनाओं या काम पर अपने हक़ के बारे में पूछिए। |
| Above example questions | ऐसे पूछ सकते हैं |
| Example question 1 | ठेकेदार ने मज़दूरी नहीं दी, मैं क्या करूँ? |
| Example question 2 | ई-श्रम कार्ड क्या है? |
| Example question 3 | ओवरटाइम का पैसा कितना मिलता है? |
| Input placeholder (changed) | लिखिए या माइक दबाइए |
| Recording hint (changed: "माइक" -> "बटन") | बोलिए… पूरा होने पर बटन फिर दबाइए |
| Thinking (shortened) | सोच रहा हूँ… |
