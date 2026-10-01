/* Adhikar Saathi frontend. Vanilla JS, no build step.
   API contract: app/CONTRACT.md section 8. Add ?mock=1 to run with no backend.
   Dev params (mock only): &state=recording|thinking|answer|clarify|refuse|error|schemes|schemes-q|complaint-form|complaint  &err=<code>  &judge=1  &ui=en */
(function () {
  'use strict';

  /* ================================================================
     1. STRINGS. The UI shows ONE language at a time (Hindi by default,
     English via the header switch). Edit here; {name} = placeholder.
     ================================================================ */
  // <STRINGS>
  const STRINGS = {
    hi: {
      'skip': 'मुख्य भाग पर जाएँ',
      'brand': 'अधिकार साथी',
      'helpline.aria': 'हेल्पलाइन 14434 पर फ़ोन करें',
      'nav.ask': 'पूछें',
      'nav.schemes': 'योजनाएँ',
      'nav.complaint': 'शिकायत',
      'home.title': 'अपना सवाल पूछिए',
      'home.orType': 'या यहाँ लिखकर पूछिए',
      'home.placeholder': 'लिखिए या माइक दबाइए',
      'home.send': 'भेजिए',
      'home.voiceReply': 'जवाब आवाज़ में सुनाइए',
      'lang.label': 'जवाब की भाषा',
      'welcome.title': 'नमस्ते! मैं अधिकार साथी हूँ।',
      'welcome.body': 'मज़दूरी, सरकारी योजनाओं या काम पर अपने हक़ के बारे में पूछिए।',
      'welcome.try': 'ऐसे पूछ सकते हैं',
      'ex.1': 'ठेकेदार ने मज़दूरी नहीं दी, मैं क्या करूँ?',
      'ex.2': 'ई-श्रम कार्ड क्या है?',
      'ex.3': 'ओवरटाइम का पैसा कितना मिलता है?',
      'rec.requesting': 'माइक की अनुमति दीजिए…',
      'rec.recording': 'बोलिए… पूरा होने पर बटन फिर दबाइए',
      'rec.startA11y': 'बोलना शुरू कीजिए',
      'rec.stopA11y': 'रिकॉर्डिंग रोकिए',
      'rec.thinking': 'सोच रहा हूँ…',
      'ans.clarifyLabel': 'मुझे एक बात पूछनी है',
      'ans.clarifyNext': 'जवाब देने के लिए माइक दबाइए',
      'ans.refuseLabel': 'इसका जवाब मेरे पास नहीं है',
      'ans.refuseHelp': '14434 सिर्फ़ ई-श्रम हेल्पडेस्क है।',
      'ans.play': 'सुनिए',
      'ans.pause': 'रोकिए',
      'ans.replay': 'फिर से सुनिए',
      'ans.tapToListen': 'सुनने के लिए बटन दबाइए',
      'ans.sources': 'जानकारी कहाँ से है',
      'ans.showEn': 'अंग्रेज़ी में देखिए',
      'ans.hideEn': 'अंग्रेज़ी छिपाइए',
      'judge.label': 'Judge view',
      'err.title': 'कुछ गड़बड़ हुई',
      'err.retry': 'फिर से कोशिश कीजिए',
      'err.typeInstead': 'लिखकर पूछिए',
      'err.micDenied': 'माइक की अनुमति नहीं मिली। फ़ोन की सेटिंग में माइक चालू कीजिए, या नीचे लिखकर पूछिए।',
      'err.noMic': 'इस फ़ोन में माइक नहीं चल रहा। नीचे लिखकर पूछिए।',
      'err.unsupported': 'इस ब्राउज़र में रिकॉर्डिंग नहीं चलती। नीचे लिखकर पूछिए।',
      'err.tooShort': 'आवाज़ बहुत छोटी थी। फिर से बोलिए।',
      'err.noNetwork': 'इंटरनेट नहीं चल रहा। थोड़ी देर बाद फिर कोशिश कीजिए।',
      'err.rateLimited': 'अभी बहुत लोग पूछ रहे हैं। थोड़ी देर रुककर फिर कोशिश कीजिए।',
      'err.noSpeech': 'आवाज़ सुनाई नहीं दी। माइक के पास बोलिए और फिर कोशिश कीजिए।',
      'err.tooLong': 'रिकॉर्डिंग बहुत लंबी थी। 30 सेकंड से छोटा सवाल पूछिए।',
      'err.generic': 'कुछ गड़बड़ हो गई। फिर से कोशिश कीजिए।',
      'notice.legal': 'यह जानकारी है, कानूनी सलाह नहीं।',
      'notice.privacy': 'आपका सवाल Sarvam AI से प्रोसेस होता है। अपना नाम, आधार या फ़ोन नंबर न बोलिए।',
      'sch.title': 'अपनी योजनाएँ जाँचिए',
      'sch.intro': 'कुछ सवालों के जवाब दीजिए। नाम या नंबर नहीं पूछा जाएगा।',
      'sch.progress': 'सवाल {n} / {total}',
      'sch.back': 'पीछे',
      'sch.restart': 'फिर से जाँचिए',
      'sch.checking': 'जाँच रहा हूँ…',
      'sch.results': 'आपके लिए नतीजे',
      'sch.eligYes': 'पात्र हो सकते हैं',
      'sch.eligNo': 'पात्र नहीं',
      'sch.eligUnknown': 'पक्का नहीं',
      'sch.missing': 'और जानकारी चाहिए',
      'sch.askAbout': 'इस योजना के बारे में पूछिए',
      'sch.askQuery': 'मुझे {scheme} के बारे में बताइए',
      'sch.disclaimer': 'यह अंदाज़ा है। पक्का फ़ैसला सरकारी दफ़्तर करता है।',
      'sch.noMatches': 'अभी कोई योजना नहीं मिली।',
      'q.age': 'आपकी उम्र कितनी है?',
      'q.age.u18': '16 या 17 साल',
      'q.age.18_40': '18 से 40 साल',
      'q.age.41_59': '41 से 59 साल',
      'q.age.60': '60 साल या ज़्यादा',
      'q.income': 'हर महीने की कमाई कितनी है?',
      'q.income.low': '₹8,000 तक',
      'q.income.mid': '₹8,001 से ₹15,000',
      'q.income.high': '₹15,000 से ज़्यादा',
      'q.work': 'आप क्या काम करते हैं?',
      'q.work.daily': 'दिहाड़ी मज़दूर',
      'q.work.construction': 'निर्माण (बिल्डिंग) मज़दूर',
      'q.work.domestic': 'घरेलू कामगार',
      'q.work.other': 'कोई और काम',
      'q.epfo': 'क्या आप EPFO या ESIC के सदस्य हैं?',
      'q.tax': 'क्या आप इनकम टैक्स भरते हैं?',
      'q.yes': 'हाँ',
      'q.no': 'नहीं',
      'q.unsure': 'पता नहीं',
      'q.preg': 'क्या आप गर्भवती हैं?',
      'q.preg.yes': 'हाँ',
      'q.preg.no': 'नहीं / लागू नहीं',
      'cmp.title': 'शिकायत का मसौदा बनाइए',
      'cmp.intro': 'जानकारी भरिए। हम शिकायत का मसौदा बनाएँगे। यह कहीं भेजा नहीं जाएगा।',
      'cmp.worker_name': 'आपका नाम (खाली छोड़ सकते हैं)',
      'cmp.worker_name.hint': 'नाम खाली छोड़ सकते हैं। छापने के बाद हाथ से लिख लीजिए।',
      'cmp.state': 'राज्य',
      'cmp.employer_name': 'मालिक या ठेकेदार का नाम',
      'cmp.work_type': 'काम का प्रकार',
      'cmp.wage_owed_inr': 'बकाया मज़दूरी (₹)',
      'cmp.period_from': 'कब से',
      'cmp.period_to': 'कब तक',
      'cmp.details': 'पूरी बात लिखिए',
      'cmp.make': 'मसौदा बनाइए',
      'cmp.making': 'बना रहा हूँ…',
      'cmp.needOne': 'कम से कम बकाया राशि या पूरी बात लिखिए।',
      'cmp.reviewBanner': 'हर लाइन ध्यान से पढ़िए, फिर इस्तेमाल कीजिए।',
      'cmp.notSent': 'यह कहीं भेजा नहीं गया है।',
      'cmp.hindiDraft': 'हिंदी मसौदा',
      'cmp.englishDraft': 'अंग्रेज़ी मसौदा',
      'cmp.checklist': 'इस्तेमाल से पहले जाँचिए',
      'cmp.print': 'छापिए',
      'cmp.copy': 'कॉपी कीजिए',
      'cmp.copied': 'कॉपी हो गया',
      'cmp.edit': 'जानकारी बदलिए'
    },
    en: {
      'skip': 'Skip to main content',
      'brand': 'Adhikar Saathi',
      'helpline.aria': 'Call helpline 14434',
      'nav.ask': 'Ask',
      'nav.schemes': 'Schemes',
      'nav.complaint': 'Complaint',
      'home.title': 'Ask your question',
      'home.orType': 'Or type your question',
      'home.placeholder': 'Type, or tap the mic',
      'home.send': 'Send',
      'home.voiceReply': 'Speak the answer aloud',
      'lang.label': 'Answer language',
      'welcome.title': 'Hello! I am Adhikar Saathi.',
      'welcome.body': 'Ask about wages, government schemes or your rights at work.',
      'welcome.try': 'You can ask',
      'ex.1': 'My contractor did not pay my wages. What do I do?',
      'ex.2': 'What is the e-Shram card?',
      'ex.3': 'How much is overtime pay?',
      'rec.requesting': 'Please allow the microphone…',
      'rec.recording': 'Speak now. Tap the button again when done.',
      'rec.startA11y': 'Start speaking',
      'rec.stopA11y': 'Stop recording',
      'rec.thinking': 'Thinking…',
      'ans.clarifyLabel': 'I need to ask one thing',
      'ans.clarifyNext': 'Tap the mic to reply',
      'ans.refuseLabel': 'I do not have an answer for this',
      'ans.refuseHelp': '14434 is the e-Shram helpdesk only.',
      'ans.play': 'Listen',
      'ans.pause': 'Pause',
      'ans.replay': 'Listen again',
      'ans.tapToListen': 'Tap the button to listen',
      'ans.sources': 'Where this comes from',
      'ans.showEn': 'Show in English',
      'ans.hideEn': 'Hide English',
      'judge.label': 'Judge view',
      'err.title': 'Something went wrong',
      'err.retry': 'Try again',
      'err.typeInstead': 'Type instead',
      'err.micDenied': 'Microphone permission was denied. Turn it on in the browser settings, or type your question below.',
      'err.noMic': 'No working microphone was found. Type your question below.',
      'err.unsupported': 'This browser cannot record audio. Type your question below.',
      'err.tooShort': 'The recording was too short. Please speak again.',
      'err.noNetwork': 'No internet connection. Please try again in a while.',
      'err.rateLimited': 'Too many people are asking right now. Please wait a little and try again.',
      'err.noSpeech': 'No speech was heard. Speak close to the microphone and try again.',
      'err.tooLong': 'The recording was too long. Ask a question shorter than 30 seconds.',
      'err.generic': 'Something went wrong. Please try again.',
      'notice.legal': 'This is information, not legal advice.',
      'notice.privacy': 'Your question is processed by Sarvam AI. Do not say your name, Aadhaar or phone number.',
      'sch.title': 'Check my schemes',
      'sch.intro': 'Answer a few questions. No name or number is asked.',
      'sch.progress': 'Question {n} of {total}',
      'sch.back': 'Back',
      'sch.restart': 'Check again',
      'sch.checking': 'Checking…',
      'sch.results': 'Your results',
      'sch.eligYes': 'Likely eligible',
      'sch.eligNo': 'Not eligible',
      'sch.eligUnknown': 'Not sure',
      'sch.missing': 'More information needed',
      'sch.askAbout': 'Ask about this scheme',
      'sch.askQuery': 'Tell me about {scheme}',
      'sch.disclaimer': 'This is an estimate. The final decision is made by the government office.',
      'sch.noMatches': 'No schemes found right now.',
      'q.age': 'How old are you?',
      'q.age.u18': '16 or 17 years',
      'q.age.18_40': '18 to 40 years',
      'q.age.41_59': '41 to 59 years',
      'q.age.60': '60 years or older',
      'q.income': 'What is your monthly income?',
      'q.income.low': 'Up to Rs 8,000',
      'q.income.mid': 'Rs 8,001 to Rs 15,000',
      'q.income.high': 'More than Rs 15,000',
      'q.work': 'What work do you do?',
      'q.work.daily': 'Daily-wage worker',
      'q.work.construction': 'Construction worker',
      'q.work.domestic': 'Domestic worker',
      'q.work.other': 'Other work',
      'q.epfo': 'Are you an EPFO or ESIC member?',
      'q.tax': 'Do you pay income tax?',
      'q.yes': 'Yes',
      'q.no': 'No',
      'q.unsure': 'Not sure',
      'q.preg': 'Are you pregnant?',
      'q.preg.yes': 'Yes',
      'q.preg.no': 'No / not applicable',
      'cmp.title': 'Write a complaint',
      'cmp.intro': 'Fill in the details. We prepare a draft. Nothing is sent anywhere.',
      'cmp.worker_name': 'Your name (optional)',
      'cmp.worker_name.hint': 'You may leave the name empty and write it by hand after printing.',
      'cmp.state': 'State',
      'cmp.employer_name': 'Employer or contractor name',
      'cmp.work_type': 'Type of work',
      'cmp.wage_owed_inr': 'Wages owed (Rs)',
      'cmp.period_from': 'From date',
      'cmp.period_to': 'To date',
      'cmp.details': 'Tell us what happened',
      'cmp.make': 'Create draft',
      'cmp.making': 'Creating…',
      'cmp.needOne': 'Enter at least the wages owed or what happened.',
      'cmp.reviewBanner': 'Review every line before you use this.',
      'cmp.notSent': 'Nothing has been sent or filed.',
      'cmp.hindiDraft': 'Hindi draft',
      'cmp.englishDraft': 'English draft',
      'cmp.checklist': 'Check before you use it',
      'cmp.print': 'Print',
      'cmp.copy': 'Copy',
      'cmp.copied': 'Copied',
      'cmp.edit': 'Change details'
    }
  };
  // </STRINGS>

  /* Answer languages. Only Hindi is owner-reviewed; the rest show a disclaimer
     (driven by the server's own `language` field). Mirrors app/backend/languages.py. */
  const LANGUAGES = [
    { code: 'hi-IN', native: 'हिन्दी' },
    { code: 'pa-IN', native: 'ਪੰਜਾਬੀ' },
    { code: 'bn-IN', native: 'বাংলা' },
    { code: 'mr-IN', native: 'मराठी' }
  ];
  const DEFAULT_LANGUAGE = 'hi-IN';

  /* ================================================================
     2. Helpers
     ================================================================ */
  const $ = (s, r) => (r || document).querySelector(s);
  const params = new URLSearchParams(location.search);
  const isMock = params.get('mock') === '1';
  const reduceMotion = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };
  let uiLang = params.get('ui') === 'en' || store.get('as_ui') === 'en' ? 'en' : 'hi';

  function t(key, vars) {
    let s = STRINGS[uiLang][key];
    if (s === undefined) { console.warn('Missing string', key); s = STRINGS.hi[key] || key; }
    return vars ? s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m)) : s;
  }
  function h(tag, attrs) {
    const el = document.createElement(tag);
    for (const k in (attrs || {})) {
      const v = attrs[k];
      if (v == null || v === false) continue;
      if (k === 'class') el.className = v;
      else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v === true ? '' : v);
    }
    for (let i = 2; i < arguments.length; i++) append(el, arguments[i]);
    return el;
  }
  function append(el, kid) {
    if (kid == null || kid === false) return;
    if (Array.isArray(kid)) kid.forEach((k) => append(el, k));
    else el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  // A translatable label: re-rendered in place when the UI language switches.
  function L(key, tag, attrs, vars) {
    const el = h(tag || 'span', Object.assign({ 'data-s': key, 'data-s-vars': vars ? JSON.stringify(vars) : null }, attrs || {}));
    el.textContent = t(key, vars); el.lang = uiLang;
    return el;
  }
  function fillStatic(root) {
    const r = root || document;
    r.querySelectorAll('[data-s]').forEach((el) => {
      const v = el.dataset.sVars ? JSON.parse(el.dataset.sVars) : null;
      el.textContent = t(el.dataset.s, v); el.lang = uiLang;
    });
    r.querySelectorAll('[data-s-ph]').forEach((el) => { el.placeholder = t(el.dataset.sPh); el.lang = uiLang; });
    r.querySelectorAll('[data-s-aria]').forEach((el) => el.setAttribute('aria-label', t(el.dataset.sAria)));
  }
  const ICONS = {
    play: '<path fill="currentColor" d="M8 5v14l11-7z"/>',
    pause: '<path fill="currentColor" d="M7 5h4v14H7zm6 0h4v14h-4z"/>',
    replay: '<path fill="currentColor" d="M12 5V2L7 6.5 12 11V8a5 5 0 1 1-5 5H5a7 7 0 1 0 7-8z"/>',
    mic: '<path fill="currentColor" d="M12 15a4 4 0 0 0 4-4V6a4 4 0 0 0-8 0v5a4 4 0 0 0 4 4zm6-4a1 1 0 0 1 2 0 8 8 0 0 1-7 7.94V21h3a1 1 0 0 1 0 2H8a1 1 0 0 1 0-2h3v-2.06A8 8 0 0 1 4 11a1 1 0 0 1 2 0 6 6 0 0 0 12 0z"/>',
    check: '<path fill="currentColor" d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/>',
    doc: '<path fill="currentColor" d="M6 2h9l5 5v15H6zm8 1.5V8h4.5zM8 12h9v2H8zm0 4h9v2H8z"/>',
    warn: '<path fill="currentColor" d="M12 2 1 21h22zm-1 7h2v6h-2zm0 8h2v2h-2z"/>',
    phone: '<path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/>',
    ask: '<path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2zm1 2v11.2L7.2 15H20V6z"/>'
  };
  function icon(name, size) {
    const s = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    s.setAttribute('viewBox', '0 0 24 24'); s.setAttribute('aria-hidden', 'true'); s.setAttribute('focusable', 'false');
    if (size) { s.setAttribute('width', size); s.setAttribute('height', size); }
    s.innerHTML = ICONS[name];
    return s;
  }
  const safeUrl = (u) => (typeof u === 'string' && /^https?:\/\//i.test(u) ? u : null);
  function sessionId() {
    let id = store.get('as_session');
    if (!id) {
      id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : 's' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
      store.set('as_session', id);
    }
    return id;
  }
  let currentLanguage = LANGUAGES.some((l) => l.code === store.get('as_lang')) ? store.get('as_lang') : DEFAULT_LANGUAGE;
  const behavior = () => (reduceMotion() ? 'auto' : 'smooth');

  /* ================================================================
     3. API (real fetch, or in-browser mock with ?mock=1)
     ================================================================ */
  class ApiError extends Error {
    constructor(code, message_hi, message_en, status) { super(code); this.code = code; this.message_hi = message_hi; this.message_en = message_en; this.status = status; }
  }
  async function callApi(path, opts) {
    if (isMock) return mockApi(path, opts);
    const ctl = new AbortController();
    const timer = setTimeout(() => ctl.abort(), 90000);
    let res;
    try {
      res = await fetch(path, {
        method: 'POST', signal: ctl.signal,
        headers: opts.json ? { 'Content-Type': 'application/json' } : undefined,
        body: opts.json ? JSON.stringify(opts.json) : opts.form
      });
    } catch (e) {
      throw new ApiError('network', null, null, 0);
    } finally { clearTimeout(timer); }
    let body = null;
    try { body = await res.json(); } catch (e) { /* non-JSON error page */ }
    if (!res.ok) {
      const er = (body && body.error) || {};
      throw new ApiError(er.code || (res.status === 429 ? 'rate_limited' : 'http_' + res.status), er.message_hi, er.message_en, res.status);
    }
    return body;
  }

  // <MOCK>
  const MOCK = {
    transcriptHi: 'मेरे मालिक ने तीन महीने से मज़दूरी नहीं दी। मैं क्या करूँ?',
    answer: {
      answer_hi: 'तय न्यूनतम मज़दूरी से कम देना कानून के खिलाफ़ है। आपको समय पर पूरी मज़दूरी पाने का हक़ है। बकाया मज़दूरी का दावा तीन साल के अंदर करना होता है।',
      answer_en: 'Paying less than the notified minimum wage is against the law. You have the right to be paid in full and on time. A claim for unpaid wages must be made within three years.',
      sources: [
        { card_id: 'W-01', title: 'Minimum wage is a legal right', source_name: 'Code on Wages, 2019', section: 's.5', url: 'https://labour.gov.in/' },
        { card_id: 'W-03', title: 'Claim unpaid wages within 3 years', source_name: 'Code on Wages, 2019', section: 's.45(6)', url: 'https://labour.gov.in/' }
      ]
    },
    clarify: {
      answer_hi: 'आप कहाँ काम करते हैं: निर्माण साइट पर या किसी के घर में?',
      answer_en: 'Where do you work: on a construction site or in someone\'s home?'
    },
    refuse: {
      answer_hi: 'माफ़ कीजिए, इस बारे में मेरे पास पक्की जानकारी नहीं है। ई-श्रम हेल्पडेस्क 14434 से आप ई-श्रम के बारे में पूछ सकते हैं।',
      answer_en: 'Sorry, I do not have reliable information on this. You can ask the e-Shram helpdesk on 14434 about e-Shram.'
    },
    errors: {
      no_speech: { message_hi: 'आवाज़ सुनाई नहीं दी। माइक के पास बोलिए और फिर कोशिश कीजिए।', message_en: 'No speech was heard. Speak close to the microphone and try again.' },
      audio_too_long: { message_hi: 'रिकॉर्डिंग बहुत लंबी थी। 30 सेकंड से छोटा सवाल पूछिए।', message_en: 'The recording was too long. Ask a question shorter than 30 seconds.' },
      rate_limited: { message_hi: 'अभी बहुत लोग पूछ रहे हैं। थोड़ी देर रुककर फिर कोशिश कीजिए।', message_en: 'Too many people are asking right now. Please wait a little and try again.' },
      stt_failed: { message_hi: 'आपकी आवाज़ समझ नहीं आई। फिर से कोशिश कीजिए।', message_en: 'Your voice could not be understood. Please try again.' }
    },
    schemes: [
      { scheme: 'e-Shram', eligible: true, why_en: 'Registration is free and open to unorganised workers such as daily-wage and construction workers.', why_hi: null, card_id: 'S-01', missing_info: [] },
      { scheme: 'PM-SYM pension', eligible: 'unknown', why_en: 'Entry age is 18 to 40 with monthly income up to Rs 15,000. Your EPFO/ESIC membership status was not given.', why_hi: null, card_id: 'S-02', missing_info: ['is_epfo_esic_member'] },
      { scheme: 'Maternity Benefit', eligible: false, why_en: 'You said you are not pregnant, so this does not apply now.', why_hi: null, card_id: 'M-01', missing_info: [] }
    ]
  };
  // </MOCK>

  function silentWavB64() {
    const rate = 8000, n = 2400;
    const b = new Uint8Array(44 + n);
    const w = (o, s) => { for (let i = 0; i < s.length; i++) b[o + i] = s.charCodeAt(i); };
    const u32 = (o, v) => { b[o] = v & 255; b[o + 1] = (v >> 8) & 255; b[o + 2] = (v >> 16) & 255; b[o + 3] = (v >> 24) & 255; };
    const u16 = (o, v) => { b[o] = v & 255; b[o + 1] = (v >> 8) & 255; };
    w(0, 'RIFF'); u32(4, 36 + n); w(8, 'WAVE'); w(12, 'fmt '); u32(16, 16); u16(20, 1); u16(22, 1); u32(24, rate); u32(28, rate); u16(32, 1); u16(34, 8);
    w(36, 'data'); u32(40, n); b.fill(128, 44);
    let s = ''; b.forEach((v) => { s += String.fromCharCode(v); });
    return btoa(s);
  }
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  let mockTurn = 0;
  async function mockApi(path, opts) {
    await sleep(reduceMotion() ? 50 : 900);
    if (path === '/api/ask') {
      const f = opts.form;
      const text = (f.get('text') || '').toString();
      const hasAudio = f.get('audio') instanceof Blob;
      const low = text.toLowerCase();
      let kind = 'answer';
      if (/\berr(or)?\b|nospeech|ratelimit/.test(low)) { const c = /nospeech/.test(low) ? 'no_speech' : 'rate_limited'; throw new ApiError(c, MOCK.errors[c].message_hi, MOCK.errors[c].message_en, 429); }
      if (/clarify|pension|पेंशन/.test(low)) kind = 'clarify';
      else if (/refuse|weather|cricket|मौसम/.test(low)) kind = 'refuse';
      else if (hasAudio) kind = ['answer', 'clarify', 'refuse'][mockTurn++ % 3];
      const src = MOCK[kind];
      const wantAudio = f.get('want_audio') !== 'false';
      const lang = (f.get('language') || DEFAULT_LANGUAGE).toString();
      const out = {
        session_id: f.get('session_id') || 'mock',
        transcript: text || MOCK.transcriptHi,
        answer_hi: src.answer_hi, answer_en: src.answer_en,
        type: kind,
        sources: kind === 'answer' ? MOCK.answer.sources : [],
        audio_b64: wantAudio ? silentWavB64() : null, audio_mime: 'audio/wav',
        latency_ms: { stt: hasAudio ? 640 : 0, retrieve: 12, llm: 780, tts: wantAudio ? 910 : 0, total: hasAudio ? 2342 : 1702 },
        cost_inr_est: wantAudio ? 0.81 : 0.05,
        debug: { retrieved_ids: ['W-01', 'W-03', 'S-01'], used_ids: kind === 'answer' ? ['W-01', 'W-03'] : [], provider: 'mock', rewritten_query: null }
      };
      if (lang !== DEFAULT_LANGUAGE) Object.assign(out, { language: lang, disclaimer_en: 'This answer was translated by AI and has not been checked by a speaker of this language. The Hindi and English versions are verified.', disclaimer_hi: null });
      return out;
    }
    if (path === '/api/schemes') return { matches: MOCK.schemes };
    if (path === '/api/complaint-draft') {
      const j = opts.json || {};
      const amt = j.wage_owed_inr ? '₹' + j.wage_owed_inr : '____';
      return {
        draft_hi: 'सेवा में,\nश्रम अधिकारी\n\nविषय: बकाया मज़दूरी के भुगतान के लिए प्रार्थना\n\nमैं ' + (j.worker_name || '________') + ', ' + (j.state || '________') + ' में ' + (j.employer_name || '________') + ' के यहाँ ' + (j.work_type || 'मज़दूरी') + ' का काम करता/करती हूँ। ' + (j.period_from || '____') + ' से ' + (j.period_to || '____') + ' तक की मेरी ' + amt + ' मज़दूरी बाकी है।\n\n' + (j.details || '') + '\n\nकृपया मेरी बकाया मज़दूरी दिलवाइए।\n\nहस्ताक्षर: ________',
        draft_en: 'To,\nThe Labour Officer\n\nSubject: Request for payment of unpaid wages\n\nI, ' + (j.worker_name || '________') + ', work for ' + (j.employer_name || '________') + ' in ' + (j.state || '________') + ' as ' + (j.work_type || 'a worker') + '. My wages of ' + amt + ' for ' + (j.period_from || '____') + ' to ' + (j.period_to || '____') + ' are unpaid.\n\n' + (j.details || '') + '\n\nPlease help me recover my unpaid wages.\n\nSignature: ________',
        notes_en: ['Check that the name, dates and amount are correct.', 'Fill every blank (____) by hand.', 'Ask a trusted person or a worker help centre to read it before you submit.', 'This draft has not been sent or filed anywhere.'],
        requires_human_review: true
      };
    }
    throw new ApiError('bad_request', null, null, 400);
  }

  /* ================================================================
     4. Chrome: header switch, tabs, language picker, views
     ================================================================ */
  const VIEWS = ['ask', 'schemes', 'complaint'];
  const TAB_ICONS = { ask: 'ask', schemes: 'check', complaint: 'doc' };
  const composer = $('#composer'), thread = $('#thread'), input = $('#text-input'), micBtn = $('#mic');
  let currentView = 'ask';

  function buildChrome() {
    const tabs = $('#tabs');
    VIEWS.forEach((v) => {
      tabs.append(h('button', { type: 'button', class: 'tab', 'data-view': v, onclick: () => showView(v) }, icon(TAB_ICONS[v]), L('nav.' + v)));
    });
    const sel = $('#lang-select');
    LANGUAGES.forEach((l) => sel.append(h('option', { value: l.code, selected: l.code === currentLanguage || null, lang: l.code.slice(0, 2) }, l.native)));
    sel.addEventListener('change', () => { currentLanguage = sel.value; store.set('as_lang', sel.value); });
    $('#ui-lang').addEventListener('click', () => setUiLang(uiLang === 'hi' ? 'en' : 'hi'));
    // keep the thread clear of the fixed composer, whatever its height
    const fit = () => document.documentElement.style.setProperty('--composer-h', composer.offsetHeight + 'px');
    if (window.ResizeObserver) new ResizeObserver(fit).observe(composer); else fit();
  }
  function setUiLang(lang) {
    uiLang = lang; store.set('as_ui', lang);
    document.documentElement.lang = lang;
    const btn = $('#ui-lang');
    btn.textContent = lang === 'hi' ? 'English' : 'हिंदी';
    btn.lang = lang === 'hi' ? 'en' : 'hi';
    btn.setAttribute('aria-label', lang === 'hi' ? 'Switch to English' : 'हिंदी में देखिए');
    fillStatic();
    setPhase(S.phase); // refresh dynamic aria labels
  }

  function showView(name, opts) {
    if (!VIEWS.includes(name)) name = 'ask';
    if (name !== 'ask') stopAudio();
    currentView = name;
    VIEWS.forEach((v) => { $('#view-' + v).hidden = v !== name; });
    composer.hidden = name !== 'ask';
    document.body.classList.toggle('on-ask', name === 'ask');
    document.querySelectorAll('.tab').forEach((tb) => { if (tb.dataset.view === name) tb.setAttribute('aria-current', 'page'); else tb.removeAttribute('aria-current'); });
    try { history.replaceState(null, '', location.pathname + location.search + '#' + name); } catch (e) { /* file:// */ }
    if (!(opts && opts.keepScroll)) window.scrollTo(0, 0);
    if (name === 'schemes' && !schemesStarted) startSchemes();
  }

  /* ================================================================
     5. ASK: thread, composer, recording
     ================================================================ */
  const MAX_SECONDS = 30;
  const S = { phase: 'idle', recorder: null, stream: null, chunks: [], startedAt: 0, ticker: null, audio: null };

  function msg(side, cls) {
    const m = h('div', { class: 'msg ' + side + (cls ? ' ' + cls : '') });
    thread.append(m);
    return m;
  }
  function reveal(el, where) {
    requestAnimationFrame(() => {
      if (where === 'start') {
        const top = el.getBoundingClientRect().top + window.scrollY - ($('.top').offsetHeight + 12);
        window.scrollTo({ top, behavior: behavior() });
      } else {
        window.scrollTo({ top: document.documentElement.scrollHeight, behavior: behavior() });
      }
    });
  }

  function buildWelcome() {
    const m = msg('them', 'welcome');
    const chips = h('div', { class: 'chips' });
    ['ex.1', 'ex.2', 'ex.3'].forEach((k) => {
      chips.append(h('button', { type: 'button', class: 'chip', onclick: () => { if (S.phase === 'idle') sendAsk({ text: t(k) }); } }, icon('ask'), L(k)));
    });
    const judge = h('button', { type: 'button', class: 'judge-toggle', id: 'judge-toggle', role: 'switch', 'aria-checked': 'false', onclick: () => setJudge(!document.body.classList.contains('judge')) },
      h('span', { class: 'switch', 'aria-hidden': 'true' }), L('judge.label'));
    m.append(h('div', { class: 'bubble' },
      L('welcome.title', 'p', { class: 'welcome-title' }),
      L('welcome.body', 'p', { class: 'welcome-body' }),
      L('welcome.try', 'span', { class: 'eyebrow' }),
      chips,
      h('div', { class: 'welcome-foot' }, L('notice.privacy', 'p'), judge)));
  }

  function setMode() {
    composer.dataset.mode = input.value.trim() ? 'send' : 'mic';
    micBtn.setAttribute('aria-label', S.phase === 'recording' ? t('rec.stopA11y') : composer.dataset.mode === 'send' ? t('home.send') : t('rec.startA11y'));
  }
  input.addEventListener('input', setMode);

  function setPhase(phase) {
    S.phase = phase;
    composer.dataset.state = phase;
    const busy = phase === 'requesting' || phase === 'thinking';
    micBtn.setAttribute('aria-busy', busy ? 'true' : 'false');
    input.disabled = busy;
    if (phase !== 'recording') { $('#rec-time').textContent = ''; setRing(0); }
    setMode();
  }
  function setRing(frac) {
    $('.ring circle', micBtn).style.strokeDashoffset = String(100 - Math.min(1, frac) * 100);
  }
  function stopAudio() { if (S.audio) { try { S.audio.pause(); } catch (e) { /* ignore */ } S.audio = null; } }

  function pickMime() {
    if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return '';
    for (const m of ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus']) {
      try { if (MediaRecorder.isTypeSupported(m)) return m; } catch (e) { /* next */ }
    }
    return '';
  }
  function extFor(type) {
    type = (type || '').toLowerCase();
    if (type.includes('mp4') || type.includes('aac')) return 'mp4';
    if (type.includes('ogg')) return 'ogg';
    if (type.includes('wav')) return 'wav';
    return 'webm';
  }

  micBtn.addEventListener('click', () => {
    if (S.phase === 'recording') stopRecording();
    else if (S.phase === 'idle') {
      if (input.value.trim()) submitText();
      else startRecording();
    }
  });
  $('#text-form').addEventListener('submit', (ev) => { ev.preventDefault(); submitText(); });
  function submitText() {
    if (S.phase !== 'idle') return;
    const v = input.value.trim();
    if (!v) { input.focus(); return; }
    input.value = ''; setMode();
    sendAsk({ text: v });
  }

  async function startRecording() {
    stopAudio();
    setPhase('requesting');
    if (isMock && !(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) return fakeRecording();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof MediaRecorder === 'undefined') {
      return showLocalError('err.unsupported', 'type');
    }
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    } catch (e) {
      const denied = e && (e.name === 'NotAllowedError' || e.name === 'SecurityError' || e.name === 'PermissionDeniedError');
      return showLocalError(denied ? 'err.micDenied' : 'err.noMic', denied ? 'record' : 'type');
    }
    const mime = pickMime();
    let rec;
    try { rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream); }
    catch (e) { stream.getTracks().forEach((tr) => tr.stop()); return showLocalError('err.unsupported', 'type'); }
    S.stream = stream; S.recorder = rec; S.chunks = [];
    rec.ondataavailable = (ev) => { if (ev.data && ev.data.size) S.chunks.push(ev.data); };
    rec.onstop = onRecorderStop;
    rec.start();
    beginTicker();
  }
  function fakeRecording() { // mock mode on a device without a microphone
    S.recorder = { state: 'recording', stop() { this.state = 'inactive'; setTimeout(() => finishRecording(new Blob([new Uint8Array(3000)], { type: 'audio/webm' }), performance.now() - S.startedAt), 0); } };
    beginTicker();
  }
  function beginTicker() {
    S.startedAt = performance.now();
    setPhase('recording');
    const tick = () => {
      const el = (performance.now() - S.startedAt) / 1000;
      setRing(el / MAX_SECONDS);
      $('#rec-time').textContent = '0:' + String(Math.min(MAX_SECONDS, Math.floor(el))).padStart(2, '0') + ' / 0:30';
      if (el >= MAX_SECONDS) stopRecording();
    };
    tick();
    S.ticker = setInterval(tick, 100);
  }
  function stopRecording() {
    clearInterval(S.ticker); S.ticker = null;
    const r = S.recorder;
    if (r && r.state !== 'inactive') { try { r.stop(); } catch (e) { releaseStream(); } }
  }
  function releaseStream() { if (S.stream) { S.stream.getTracks().forEach((tr) => tr.stop()); S.stream = null; } }
  function onRecorderStop() {
    const dur = performance.now() - S.startedAt;
    const type = (S.recorder && S.recorder.mimeType) || (S.chunks[0] && S.chunks[0].type) || 'audio/webm';
    releaseStream();
    finishRecording(new Blob(S.chunks, { type }), dur);
  }
  function finishRecording(blob, durMs) {
    if (durMs < 700 || blob.size < 500) return showLocalError('err.tooShort', 'record');
    sendAsk({ audio: blob });
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden && S.phase === 'recording') stopRecording(); });

  function buildAskForm(req) {
    const f = new FormData();
    f.append('session_id', sessionId());
    if (req.audio) f.append('audio', req.audio, 'speech.' + extFor(req.audio.type));
    else f.append('text', req.text);
    f.append('want_audio', req.wantAudio === false || !$('#want-audio').checked ? 'false' : 'true');
    f.append('language', currentLanguage);
    return f;
  }

  function addUser(text) {
    const m = msg('me');
    const b = text
      ? h('div', { class: 'bubble' }, h('p', null, text))
      : h('div', { class: 'bubble pending' }, icon('mic'), h('span', { 'aria-hidden': 'true' }, '…'));
    m.append(b);
    reveal(m, 'end');
    return m;
  }
  function addThinking() {
    const m = msg('them', 'thinking');
    m.append(h('div', { class: 'bubble', role: 'status' }, h('span', { class: 'dots', 'aria-hidden': 'true' }, h('i'), h('i'), h('i')), L('rec.thinking', 'span', { class: 'dots-label' })));
    reveal(m, 'end');
    return m;
  }

  async function sendAsk(req, opts) {
    if (currentView !== 'ask') showView('ask');
    stopAudio();
    composer.classList.remove('nudge');
    const userMsg = opts && opts.retry ? null : addUser(req.text || null);
    setPhase('thinking');
    const thinking = addThinking();
    try {
      const data = await callApi('/api/ask', { form: buildAskForm(req) });
      thinking.remove();
      if (userMsg && req.audio) {
        if (data.transcript) userMsg.replaceChildren(h('div', { class: 'bubble' }, h('p', null, data.transcript)));
        else userMsg.remove();
      }
      setPhase('idle');
      renderAnswer(data);
    } catch (e) {
      thinking.remove();
      if (userMsg && req.audio) userMsg.remove();
      setPhase('idle');
      showApiError(e, req);
    }
  }

  function showLocalError(key, action) {
    setPhase('idle');
    renderError({ message_hi: STRINGS.hi[key], message_en: STRINGS.en[key] }, action);
  }
  function showApiError(e, req) {
    const code = e.code || 'unknown';
    const fb = { network: 'err.noNetwork', rate_limited: 'err.rateLimited', no_speech: 'err.noSpeech', audio_too_long: 'err.tooLong' }[code] || 'err.generic';
    const err = { message_hi: e.message_hi || STRINGS.hi[fb], message_en: e.message_en || STRINGS.en[fb] };
    let action = 'resend';
    if (code === 'no_speech' || code === 'audio_too_long') action = 'record';
    else if (code === 'bad_request') action = 'type';
    if (code === 'tts_failed') req = Object.assign({}, req, { wantAudio: false });
    renderError(err, action, req);
  }
  function renderError(err, action, req) {
    stopAudio();
    const retry = () => {
      if (action === 'resend' && req) sendAsk(req, { retry: true });
      else if (action === 'record') startRecording();
      else input.focus();
    };
    const m = msg('them');
    m.append(h('div', { class: 'bubble error', role: 'alert' },
      L('err.title', 'span', { class: 'tag error' }),
      h('p', { lang: uiLang }, uiLang === 'en' ? err.message_en : err.message_hi),
      h('button', { type: 'button', class: 'btn retry', onclick: retry }, L(action === 'type' ? 'err.typeInstead' : 'err.retry'))));
    reveal(m, 'end');
  }

  function renderAnswer(d) {
    stopAudio();
    const type = ['answer', 'clarify', 'refuse'].includes(d.type) ? d.type : 'answer';
    const ansLang = (d.language || DEFAULT_LANGUAGE).slice(0, 2);
    const m = msg('them');
    const b = h('div', { class: 'bubble ' + type });
    if (type !== 'answer') b.append(L(type === 'clarify' ? 'ans.clarifyLabel' : 'ans.refuseLabel', 'span', { class: 'tag ' + type }));
    b.append(h('p', { class: 'answer-text', lang: ansLang }, d.answer_hi || ''));

    if (d.audio_b64) {
      const audio = new Audio('data:' + (d.audio_mime || 'audio/wav') + ';base64,' + d.audio_b64);
      S.audio = audio;
      const btn = h('button', { type: 'button', class: 'listen' });
      const hint = L('ans.tapToListen', 'span', { class: 'listen-hint', hidden: true });
      const setListen = (mode) => btn.replaceChildren(icon(mode), L({ play: 'ans.play', pause: 'ans.pause', replay: 'ans.replay' }[mode]));
      setListen('play');
      audio.addEventListener('playing', () => { setListen('pause'); hint.hidden = true; });
      audio.addEventListener('pause', () => { if (!audio.ended) setListen('play'); });
      audio.addEventListener('ended', () => setListen('replay'));
      btn.addEventListener('click', () => {
        if (!audio.paused) { audio.pause(); return; }
        if (audio.ended) audio.currentTime = 0;
        audio.play().catch(() => { hint.hidden = false; });
      });
      b.append(h('div', null, btn, hint));
      const p = audio.play();
      if (p && p.catch) p.catch(() => { hint.hidden = false; }); // autoplay blocked: show the hint
    }

    if (type === 'refuse') {
      b.append(h('div', { class: 'note help' }, L('ans.refuseHelp'), h('a', { class: 'call', href: 'tel:14434' }, icon('phone', 16), '14434')));
    }

    if (Array.isArray(d.sources) && d.sources.length) {
      const stamps = h('div', { class: 'stamps' });
      d.sources.forEach((s) => {
        const url = safeUrl(s.url);
        const inner = [h('span', { class: 'stamp-law' }, s.source_name || s.title || s.card_id || ''), s.section ? h('span', { class: 'stamp-sec' }, s.section) : null];
        stamps.append(url
          ? h('a', { class: 'stamp', href: url, target: '_blank', rel: 'noopener noreferrer', title: s.title || '', lang: 'en' }, inner)
          : h('span', { class: 'stamp', title: s.title || '', lang: 'en' }, inner));
      });
      b.append(h('div', { class: 'sources' }, L('ans.sources', 'span', { class: 'eyebrow' }), stamps));
    }

    if (d.answer_en) {
      const gloss = h('p', { class: 'gloss', lang: 'en', hidden: uiLang !== 'en' || null }, d.answer_en);
      const tog = h('button', { type: 'button', class: 'linkish', 'aria-expanded': String(!gloss.hidden) });
      const label = () => tog.replaceChildren(L(gloss.hidden ? 'ans.showEn' : 'ans.hideEn'));
      label();
      tog.addEventListener('click', () => { gloss.hidden = !gloss.hidden; tog.setAttribute('aria-expanded', String(!gloss.hidden)); label(); });
      b.append(h('div', null, tog, gloss));
    }
    m.append(b);

    if (type === 'clarify') {
      m.append(L('ans.clarifyNext', 'p', { class: 'after' }));
      composer.classList.add('nudge');
    }
    if (d.latency_ms || d.cost_inr_est != null || d.debug) {
      const lines = [];
      if (d.latency_ms) lines.push('latency_ms: ' + Object.keys(d.latency_ms).map((k) => k + '=' + d.latency_ms[k]).join('  '));
      if (d.cost_inr_est != null) lines.push('cost_inr_est: Rs ' + d.cost_inr_est);
      if (d.language) lines.push('language: ' + d.language);
      if (d.debug) lines.push('debug: ' + JSON.stringify(d.debug, null, 2));
      m.append(h('div', { class: 'judge-box judge-only' }, h('pre', null, lines.join('\n'))));
    }
    reveal(m, 'start');
  }

  /* ================================================================
     6. SCHEMES
     ================================================================ */
  const yn = () => [{ k: 'q.yes', v: true }, { k: 'q.no', v: false }, { k: 'q.unsure', v: undefined }];
  const QUESTIONS = [
    { id: 'age', q: 'q.age', opts: [{ k: 'q.age.u18', v: 16 }, { k: 'q.age.18_40', v: 30 }, { k: 'q.age.41_59', v: 50 }, { k: 'q.age.60', v: 62 }] },
    { id: 'monthly_income_inr', q: 'q.income', opts: [{ k: 'q.income.low', v: 6000 }, { k: 'q.income.mid', v: 12000 }, { k: 'q.income.high', v: 20000 }] },
    { id: 'occupation', q: 'q.work', opts: [{ k: 'q.work.daily', v: 'daily_wage' }, { k: 'q.work.construction', v: 'construction' }, { k: 'q.work.domestic', v: 'domestic' }, { k: 'q.work.other', v: 'other' }] },
    { id: 'is_epfo_esic_member', q: 'q.epfo', opts: yn() },
    { id: 'is_income_tax_payer', q: 'q.tax', opts: yn() },
    { id: 'is_pregnant', q: 'q.preg', opts: [{ k: 'q.preg.yes', v: true }, { k: 'q.preg.no', v: false }] }
  ];
  let schemesStarted = false, qIndex = 0, qAnswers = {};
  const schBody = $('#sch-body');

  function startSchemes() { schemesStarted = true; qIndex = 0; qAnswers = {}; renderQuestion(); }
  function renderQuestion() {
    const q = QUESTIONS[qIndex];
    const opts = h('div', { class: 'opts', role: 'group', 'aria-labelledby': 'q-text' });
    q.opts.forEach((o) => opts.append(h('button', { type: 'button', class: 'btn opt', onclick: () => answerQ(q, o) }, L(o.k))));
    const pct = Math.round((qIndex / QUESTIONS.length) * 100);
    schBody.replaceChildren(
      qIndex === 0 ? L('sch.intro', 'p', { class: 'lead' }) : h('span'),
      h('div', { class: 'q-card' },
        h('div', { class: 'q-head' }, L('sch.progress', 'span', null, { n: qIndex + 1, total: QUESTIONS.length }),
          h('span', { class: 'bar', 'aria-hidden': 'true' }, h('i', { style: 'width:' + pct + '%' }))),
        L(q.q, 'h2', { class: 'q-text', id: 'q-text', tabindex: '-1' }),
        opts,
        qIndex > 0 ? h('button', { type: 'button', class: 'linkish q-back', onclick: () => { qIndex--; delete qAnswers[QUESTIONS[qIndex].id]; renderQuestion(); } }, L('sch.back')) : null));
    if (qIndex > 0) $('#q-text').focus({ preventScroll: true }); // screen readers hear the new question
  }
  function answerQ(q, o) {
    if (o.v !== undefined) qAnswers[q.id] = o.v; // "not sure" = omitted -> backend says "unknown"
    if (qIndex < QUESTIONS.length - 1) { qIndex++; renderQuestion(); window.scrollTo(0, 0); } else submitSchemes();
  }
  async function submitSchemes() {
    schBody.replaceChildren(L('sch.checking', 'p', { class: 'loading', role: 'status' }));
    try {
      const data = await callApi('/api/schemes', { json: qAnswers });
      renderSchemeResults(data.matches || []);
    } catch (e) {
      const fb = e.code === 'network' ? 'err.noNetwork' : 'err.generic';
      schBody.replaceChildren(h('div', { class: 'bubble error', role: 'alert' },
        L('err.title', 'span', { class: 'tag error' }),
        h('p', null, (uiLang === 'en' ? e.message_en : e.message_hi) || t(fb)),
        h('button', { type: 'button', class: 'btn retry', onclick: submitSchemes }, L('err.retry'))));
    }
    window.scrollTo(0, 0);
  }
  // The backend quotes the representative numbers we send; show the band the user picked instead.
  const AGE_BAND = { 16: '16-17', 30: '18-40', 50: '41-59', 62: '60 or above' };
  const INC_BAND = { 6000: 'up to Rs 8000', 12000: 'Rs 8001-15000', 20000: 'above Rs 15000' };
  function bandify(s) {
    return (s || '')
      .replace(/\bage (16|30|50|62)\b/g, (m, a) => 'age ' + AGE_BAND[a])
      .replace(/\b(?:monthly )?income Rs (6000|12000|20000)\b/g, (m, a) => m.replace(/Rs \d+/, 'in the band ' + INC_BAND[a]));
  }
  function renderSchemeResults(matches) {
    const kids = [L('sch.results', 'h2', { class: 'results-title' })];
    if (!matches.length) kids.push(L('sch.noMatches', 'p', { class: 'lead' }));
    matches.forEach((m) => {
      const cls = m.eligible === true ? 'yes' : m.eligible === false ? 'no' : 'unk';
      const mark = { yes: '✓', no: '✕', unk: '?' }[cls];
      kids.push(h('article', { class: 'match' },
        h('div', { class: 'match-head' },
          h('h3', { class: 'match-name', lang: 'en' }, m.scheme),
          h('span', { class: 'pill ' + cls }, h('span', { 'aria-hidden': 'true' }, mark), L({ yes: 'sch.eligYes', no: 'sch.eligNo', unk: 'sch.eligUnknown' }[cls]))),
        m.why_hi ? h('p', { class: 'why', lang: 'hi' }, m.why_hi) : null,
        h('p', { class: 'why', lang: 'en' }, bandify(m.why_en)),
        (m.missing_info && m.missing_info.length) ? h('p', { class: 'missing' }, L('sch.missing'), ': ' + m.missing_info.join(', ').replace(/_/g, ' ')) : null,
        h('button', { type: 'button', class: 'linkish', onclick: () => askAbout(m.scheme) }, L('sch.askAbout'))));
    });
    kids.push(L('sch.disclaimer', 'p', { class: 'fine-print' }));
    kids.push(h('button', { type: 'button', class: 'btn btn-primary btn-block', onclick: () => { startSchemes(); window.scrollTo(0, 0); } }, L('sch.restart')));
    schBody.replaceChildren(...kids);
  }
  function askAbout(name) {
    showView('ask');
    if (S.phase === 'idle') sendAsk({ text: t('sch.askQuery', { scheme: name }) });
  }

  /* ================================================================
     7. COMPLAINT
     ================================================================ */
  const CMP_FIELDS = [
    { id: 'worker_name', type: 'text', hint: true },
    { id: 'state', type: 'text' },
    { id: 'employer_name', type: 'text' },
    { id: 'work_type', type: 'text' },
    { id: 'wage_owed_inr', type: 'number' },
    { row: [{ id: 'period_from', type: 'date' }, { id: 'period_to', type: 'date' }] },
    { id: 'details', type: 'textarea' }
  ];
  const cmpForm = $('#cmp-form'), cmpResult = $('#cmp-result');
  function fieldEl(f) {
    const id = 'f-' + f.id;
    const ctl = f.type === 'textarea'
      ? h('textarea', { id, name: f.id, rows: 5, maxlength: 2000 })
      : h('input', { id, name: f.id, type: f.type, inputmode: f.type === 'number' ? 'numeric' : null, min: f.type === 'number' ? 0 : null, autocomplete: 'off' });
    return h('div', { class: 'field' }, L('cmp.' + f.id, 'label', { for: id }), f.hint ? L('cmp.worker_name.hint', 'p', { class: 'hint' }) : null, ctl);
  }
  CMP_FIELDS.forEach((f) => cmpForm.append(f.row ? h('div', { class: 'field-row' }, f.row.map(fieldEl)) : fieldEl(f)));
  const cmpMsg = h('p', { class: 'form-msg', role: 'alert', hidden: true });
  const cmpSubmit = h('button', { type: 'submit', class: 'btn btn-primary btn-block' }, L('cmp.make'));
  cmpForm.append(cmpMsg, cmpSubmit);

  cmpForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const fd = new FormData(cmpForm);
    const j = {};
    ['worker_name', 'state', 'employer_name', 'work_type', 'period_from', 'period_to', 'details'].forEach((k) => { j[k] = (fd.get(k) || '').toString().trim(); });
    j.wage_owed_inr = Number(fd.get('wage_owed_inr')) || 0;
    if (!j.details && !j.wage_owed_inr) { cmpMsg.textContent = t('cmp.needOne'); cmpMsg.hidden = false; return; }
    cmpMsg.hidden = true;
    cmpSubmit.disabled = true; cmpSubmit.replaceChildren(L('cmp.making'));
    try {
      renderDraft(await callApi('/api/complaint-draft', { json: j }));
    } catch (e) {
      const fb = e.code === 'network' ? 'err.noNetwork' : 'err.generic';
      cmpMsg.textContent = (uiLang === 'en' ? e.message_en : e.message_hi) || t(fb); cmpMsg.hidden = false;
    } finally { cmpSubmit.disabled = false; cmpSubmit.replaceChildren(L('cmp.make')); }
  });

  function renderDraft(d) {
    const toast = h('p', { class: 'toast', role: 'status' });
    const full = (d.draft_hi || '') + '\n\n----------\n\n' + (d.draft_en || '');
    const copy = () => {
      const done = () => { toast.replaceChildren(L('cmp.copied')); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(full).then(done, () => legacyCopy(full, done));
      else legacyCopy(full, done);
    };
    const kids = [
      h('div', { class: 'review', role: 'note' }, icon('warn'), h('div', null, L('cmp.reviewBanner', 'strong'), L('cmp.notSent'))),
      h('div', { class: 'btn-row no-print' },
        h('button', { type: 'button', class: 'btn btn-primary', onclick: () => window.print() }, L('cmp.print')),
        h('button', { type: 'button', class: 'btn', onclick: copy }, L('cmp.copy'))),
      toast,
      h('section', { class: 'paper' }, L('cmp.hindiDraft', 'h2'), h('pre', { class: 'draft', lang: 'hi' }, d.draft_hi || '')),
      h('section', { class: 'paper' }, L('cmp.englishDraft', 'h2'), h('pre', { class: 'draft', lang: 'en' }, d.draft_en || ''))
    ];
    if (Array.isArray(d.notes_en) && d.notes_en.length) {
      kids.push(h('section', { class: 'paper' }, L('cmp.checklist', 'h2'), h('ul', { class: 'checklist', lang: 'en' }, d.notes_en.map((n) => h('li', null, n)))));
    }
    kids.push(h('button', { type: 'button', class: 'btn btn-block no-print', onclick: () => { cmpResult.replaceChildren(); $('#cmp-form-wrap').hidden = false; window.scrollTo(0, 0); } }, L('cmp.edit')));
    cmpResult.replaceChildren(...kids);
    $('#cmp-form-wrap').hidden = true;
    window.scrollTo(0, 0);
  }
  function legacyCopy(text, done) {
    const ta = h('textarea', { style: 'position:fixed;opacity:0', 'aria-hidden': 'true' });
    ta.value = text; document.body.append(ta); ta.select();
    try { document.execCommand('copy'); done(); } catch (e) { /* user can select manually */ }
    ta.remove();
  }

  /* ================================================================
     8. Judge view, boot, demo states
     ================================================================ */
  function setJudge(on) {
    document.body.classList.toggle('judge', on);
    const tg = $('#judge-toggle'); if (tg) tg.setAttribute('aria-checked', String(on));
    store.set('as_judge', on ? '1' : '0');
  }

  async function demo(state) {
    const askText = { answer: 'मज़दूरी नहीं मिली', clarify: 'clarify', refuse: 'refuse' };
    if (state === 'recording') {
      setPhase('recording'); setRing(12 / 30); $('#rec-time').textContent = '0:12 / 0:30';
    } else if (state === 'thinking') {
      addUser('ठेकेदार ने मज़दूरी नहीं दी, मैं क्या करूँ?'); setPhase('thinking'); addThinking();
    } else if (askText[state]) {
      sendAsk({ text: askText[state] === 'मज़दूरी नहीं मिली' ? t('ex.1') : askText[state] });
    } else if (state === 'error') {
      const code = params.get('err') || 'no_speech';
      const e = MOCK.errors[code] || MOCK.errors.no_speech;
      addUser(t('ex.2'));
      renderError(e, code === 'rate_limited' ? 'resend' : 'record');
    } else if (state === 'schemes') {
      showView('schemes');
      qAnswers = { age: 30, monthly_income_inr: 12000, occupation: 'construction', is_pregnant: false };
      renderSchemeResults((await mockApi('/api/schemes', { json: qAnswers })).matches);
    } else if (state === 'schemes-q') {
      showView('schemes'); qIndex = 2; renderQuestion();
    } else if (state === 'complaint-form') {
      showView('complaint');
    } else if (state === 'complaint') {
      showView('complaint');
      const j = { worker_name: '', state: 'Bihar', employer_name: 'Sharma Constructions', work_type: 'Mason helper', wage_owed_inr: 18000, period_from: '2026-06-01', period_to: '2026-08-31', details: 'तीन महीने से मज़दूरी नहीं मिली।' };
      renderDraft(await mockApi('/api/complaint-draft', { json: j }));
    }
  }

  buildChrome();
  buildWelcome();
  setUiLang(uiLang);
  setJudge(store.get('as_judge') === '1' || (isMock && params.get('judge') === '1'));
  setPhase('idle');
  const hashView = (location.hash || '').slice(1);
  showView(VIEWS.includes(hashView) ? hashView : 'ask', { keepScroll: true });
  if (isMock && params.get('state')) demo(params.get('state'));
})();
