/* Adhikar Saathi frontend. Vanilla JS, no build step.
   API contract: app/CONTRACT.md section 8. Add ?mock=1 to run with no backend.
   Extra dev params (mock only): &state=recording|thinking|answer|clarify|refuse|error|schemes|complaint  &err=<error code> */
(function () {
  'use strict';

  /* ================================================================
     1. STRINGS: every UI string, Hindi (primary) + English (subtitle).
     Edit here. Use {name} for placeholders.
     ================================================================ */
  // <STRINGS>
  const STRINGS = {
    hi: {
      'skip': 'मुख्य भाग पर जाएँ',
      'brand': 'अधिकार साथी',
      'helpline.sub': 'हेल्पलाइन',
      'helpline.aria': 'हेल्पलाइन 14434 पर फ़ोन करें',
      'nav.ask': 'पूछें',
      'nav.schemes': 'योजनाएँ',
      'nav.complaint': 'शिकायत',
      'home.title': 'अपना सवाल पूछिए',
      'home.tapStart': 'बोलने के लिए माइक दबाइए',
      'home.orType': 'या यहाँ लिखकर पूछिए',
      'home.placeholder': 'जैसे: मज़दूरी नहीं मिली',
      'home.send': 'भेजिए',
      'home.voiceReply': 'जवाब आवाज़ में सुनाइए',
      'lang.label': 'जवाब की भाषा',
      'rec.requesting': 'माइक की अनुमति दीजिए…',
      'rec.recording': 'बोलिए… पूरा होने पर माइक फिर दबाइए',
      'rec.startA11y': 'बोलना शुरू कीजिए',
      'rec.stopA11y': 'रिकॉर्डिंग रोकिए',
      'rec.left': 'सेकंड बाकी',
      'rec.thinking': 'सोच रहा हूँ… थोड़ा रुकिए',
      'ans.youSaid': 'आपने कहा',
      'ans.answer': 'जवाब',
      'ans.clarifyLabel': 'मुझे एक बात पूछनी है',
      'ans.clarifyNext': 'जवाब देने के लिए माइक दबाइए',
      'ans.refuseLabel': 'इसका जवाब मेरे पास नहीं है',
      'ans.refuseHelp': '14434 सिर्फ़ ई-श्रम हेल्पडेस्क है।',
      'ans.play': 'सुनिए',
      'ans.pause': 'रोकिए',
      'ans.replay': 'फिर से सुनिए',
      'ans.tapToListen': 'सुनने के लिए बटन दबाइए',
      'ans.sources': 'जानकारी कहाँ से है',
      'ans.openSource': 'स्रोत खोलिए',
      'ans.showEn': 'अंग्रेज़ी में देखिए',
      'ans.hideEn': 'अंग्रेज़ी छिपाइए',
      'ans.newQuestion': 'नया सवाल पूछिए',
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
      'err.emptyText': 'पहले अपना सवाल लिखिए।',
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
      'helpline.sub': 'Helpline',
      'helpline.aria': 'Call helpline 14434',
      'nav.ask': 'Ask',
      'nav.schemes': 'Schemes',
      'nav.complaint': 'Complaint',
      'home.title': 'Ask your question',
      'home.tapStart': 'Tap the mic to speak',
      'home.orType': 'Or type your question',
      'home.placeholder': 'e.g. my wages are not paid',
      'home.send': 'Send',
      'home.voiceReply': 'Speak the answer aloud',
      'lang.label': 'Answer language',
      'rec.requesting': 'Please allow the microphone…',
      'rec.recording': 'Speak now. Tap the mic again when done.',
      'rec.startA11y': 'Start speaking',
      'rec.stopA11y': 'Stop recording',
      'rec.left': 'seconds left',
      'rec.thinking': 'Thinking… please wait',
      'ans.youSaid': 'You said',
      'ans.answer': 'Answer',
      'ans.clarifyLabel': 'I need to ask one thing',
      'ans.clarifyNext': 'Tap the mic to reply',
      'ans.refuseLabel': 'I do not have an answer for this',
      'ans.refuseHelp': '14434 is the e-Shram helpdesk only.',
      'ans.play': 'Play',
      'ans.pause': 'Pause',
      'ans.replay': 'Play again',
      'ans.tapToListen': 'Tap the button to listen',
      'ans.sources': 'Where this comes from',
      'ans.openSource': 'Open source',
      'ans.showEn': 'English (for verification)',
      'ans.hideEn': 'Hide English',
      'ans.newQuestion': 'Ask a new question',
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
      'err.emptyText': 'Please write your question first.',
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

  /* ================================================================
     1b. Answer languages. Hindi is the only one the owner has reviewed
     (app/data/hindi_review/); the rest are a genuine but unverified capability
     (see app/data/language_review/INDEX.md). Mirrors app/backend/languages.py.
     ================================================================ */
  const LANGUAGES = [
    { code: 'hi-IN', native: 'हिन्दी', en: 'Hindi' },
    { code: 'pa-IN', native: 'ਪੰਜਾਬੀ', en: 'Punjabi' },
    { code: 'bn-IN', native: 'বাংলা', en: 'Bengali' },
    { code: 'mr-IN', native: 'मराठी', en: 'Marathi' }
  ];
  const DEFAULT_LANGUAGE = 'hi-IN';

  /* ================================================================
     2. Small helpers
     ================================================================ */
  const $ = (s, r) => (r || document).querySelector(s);
  const isMock = new URLSearchParams(location.search).get('mock') === '1';
  const params = new URLSearchParams(location.search);
  const reduceMotion = () => window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  function tr(key, vars) {
    const fill = (s) => (vars ? s.replace(/\{(\w+)\}/g, (m, k) => (k in vars ? vars[k] : m)) : s);
    const hi = STRINGS.hi[key], en = STRINGS.en[key];
    if (hi === undefined || en === undefined) console.warn('Missing string', key);
    return { hi: fill(hi || key), en: fill(en || key) };
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
  // Hindi line + small English line. Text is always set via textContent (API data is never HTML).
  function bi(key, vars, tag) {
    const s = typeof key === 'string' ? tr(key, vars) : key;
    return h(tag || 'span', { class: 'bi' }, h('span', { class: 'hi', lang: 'hi' }, s.hi), h('span', { class: 'en', lang: 'en' }, s.en));
  }
  const plain = (key, vars) => { const s = tr(key, vars); return s.hi + ' / ' + s.en; };
  function fillStatic() {
    document.querySelectorAll('[data-s]').forEach((el) => { el.replaceChildren(...bi(el.dataset.s).childNodes); });
  }
  const ICONS = {
    play: '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>',
    pause: '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path fill="currentColor" d="M7 5h4v14H7zm6 0h4v14h-4z"/></svg>',
    replay: '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 5V2L7 6.5 12 11V8a5 5 0 1 1-5 5H5a7 7 0 1 0 7-8z"/></svg>',
    mic: '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 15a4 4 0 0 0 4-4V6a4 4 0 0 0-8 0v5a4 4 0 0 0 4 4zm6-4a1 1 0 0 1 2 0 8 8 0 0 1-7 7.94V21h3a1 1 0 0 1 0 2H8a1 1 0 0 1 0-2h3v-2.06A8 8 0 0 1 4 11a1 1 0 0 1 2 0 6 6 0 0 0 12 0z"/></svg>',
    check: '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>',
    doc: '<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M6 2h9l5 5v15H6zm8 1.5V8h4.5zM8 12h9v2H8zm0 4h9v2H8z"/></svg>',
    warn: '<svg viewBox="0 0 24 24" width="30" height="30" aria-hidden="true" focusable="false"><path fill="currentColor" d="M12 2 1 21h22zm-1 7h2v6h-2zm0 8h2v2h-2z"/></svg>',
    arrowDown: '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true" focusable="false"><path fill="currentColor" d="M11 4h2v12l5-5 1.4 1.4L12 20l-7.4-7.6L6 11l5 5z"/></svg>',
    ext: '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path fill="currentColor" d="M14 3h7v7h-2V6.4l-9.3 9.3-1.4-1.4L17.6 5H14zM5 5h6v2H7v10h10v-4h2v6H5z"/></svg>',
    phone: '<svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true" focusable="false"><path fill="currentColor" d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>'
  };
  const icon = (name) => { const t = document.createElement('template'); t.innerHTML = ICONS[name]; return t.content.firstChild; };
  const safeUrl = (u) => (typeof u === 'string' && /^https?:\/\//i.test(u) ? u : null);
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode: ignore */ } }
  };
  function sessionId() {
    let id = store.get('as_session');
    if (!id) {
      id = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : 's' + Date.now().toString(36) + Math.random().toString(36).slice(2, 10);
      store.set('as_session', id);
    }
    return id;
  }
  let currentLanguage = LANGUAGES.some((l) => l.code === store.get('as_lang')) ? store.get('as_lang') : DEFAULT_LANGUAGE;
  function setLanguage(code) { currentLanguage = code; store.set('as_lang', code); }
  function scrollToEl(el) {
    if (el && el.scrollIntoView) el.scrollIntoView({ behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' });
  }

  /* ================================================================
     3. API layer (real fetch, or in-browser mock when ?mock=1)
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

  /* ================================================================
     4. Mock API (contract-shaped canned responses, no network)
     ================================================================ */
  // <MOCK>
  const MOCK = {
    transcriptHi: 'मेरे मालिक ने तीन महीने से मज़दूरी नहीं दी। मैं क्या करूँ?',
    answer: {
      answer_hi: 'तय न्यूनतम मज़दूरी से कम देना कानून के खिलाफ़ है। आपको समय पर पूरी मज़दूरी पाने का हक़ है। बकाया मज़दूरी का दावा तीन साल के अंदर करना होता है।',
      answer_en: 'Paying less than the notified minimum wage is against the law. You have the right to be paid in full and on time. A claim for unpaid wages must be made within three years.',
      sources: [
        { card_id: 'W-01', title: 'Minimum wage is a legal right', source_name: 'Code on Wages, 2019', section: 's.5', url: 'https://labour.gov.in/' },
        { card_id: 'W-03', title: 'Claim unpaid wages within 3 years', source_name: 'Code on Wages, 2019', section: 'claims section (mock)', url: 'https://labour.gov.in/' }
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
    const rate = 8000, n = 2400; // 0.3 s of silence
    const b = new Uint8Array(44 + n);
    const w = (o, s) => { for (let i = 0; i < s.length; i++) b[o + i] = s.charCodeAt(i); };
    const u32 = (o, v) => { b[o] = v & 255; b[o + 1] = (v >> 8) & 255; b[o + 2] = (v >> 16) & 255; b[o + 3] = (v >> 24) & 255; };
    const u16 = (o, v) => { b[o] = v & 255; b[o + 1] = (v >> 8) & 255; };
    w(0, 'RIFF'); u32(4, 36 + n); w(8, 'WAVE'); w(12, 'fmt '); u32(16, 16); u16(20, 1); u16(22, 1); u32(24, rate); u32(28, rate); u16(32, 1); u16(34, 8);
    w(36, 'data'); u32(40, n); b.fill(128, 44); // 8-bit PCM silence = 128
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
      if (/\berr(or)?\b|nospeech|ratelimit/.test(low)) throw new ApiError(/nospeech/.test(low) ? 'no_speech' : 'rate_limited', ...errMsg(/nospeech/.test(low) ? 'no_speech' : 'rate_limited'), 429);
      if (/clarify|pension|पेंशन/.test(low)) kind = 'clarify';
      else if (/refuse|weather|cricket|मौसम/.test(low)) kind = 'refuse';
      else if (hasAudio) kind = ['answer', 'clarify', 'refuse'][mockTurn++ % 3];
      const src = MOCK[kind];
      const wantAudio = f.get('want_audio') !== 'false';
      return {
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
  function errMsg(code) { const e = MOCK.errors[code]; return [e.message_hi, e.message_en]; }

  /* ================================================================
     5. Tabs / views / static UI
     ================================================================ */
  const VIEWS = ['ask', 'schemes', 'complaint'];
  const TAB_ICONS = { ask: 'mic', schemes: 'check', complaint: 'doc' };
  let currentView = 'ask';

  function buildChrome() {
    document.documentElement.lang = 'hi';
    $('#skip-link').replaceChildren(...bi('skip').childNodes);
    $('#brand-hi').textContent = STRINGS.hi.brand;
    $('#brand-en').textContent = STRINGS.en.brand;
    $('#helpline').setAttribute('aria-label', plain('helpline.aria'));
    $('#send-btn').replaceChildren(...bi('home.send').childNodes);
    $('#text-input').placeholder = STRINGS.hi['home.placeholder'];
    $('#text-input').setAttribute('aria-describedby', 'text-ph-en');
    const phEn = h('span', { id: 'text-ph-en', class: 'en', hidden: true }, STRINGS.en['home.placeholder']);
    $('#text-form').append(phEn);
    $('#notice-legal').replaceChildren(...bi('notice.legal').childNodes);
    $('#notice-privacy').replaceChildren(...bi('notice.privacy').childNodes);
    $('#judge-label').textContent = plain('judge.label').split(' / ')[0];
    buildLanguageSelector();
    const tabs = $('#tabs');
    const inner = h('div', { class: 'tabs-inner' });
    VIEWS.forEach((v) => {
      inner.append(h('button', { type: 'button', class: 'tab', 'data-view': v, 'aria-label': plain('nav.' + v), onclick: () => showView(v) }, icon(TAB_ICONS[v]), bi('nav.' + v)));
    });
    tabs.append(inner);
    fillStatic();
  }
  // Answer-language selector: inserted next to the mic button (index.html itself is not owned
  // by this change; see this agent's final report). Only Hindi is owner-verified; picking
  // another language shows a disclaimer on the answer (renderAnswer below), driven by the
  // server response's own `language` field so the UI never claims a language the backend did
  // not actually answer in.
  function buildLanguageSelector() {
    const sel = h('select', { id: 'lang-select', 'aria-label': plain('lang.label'), onchange: (ev) => setLanguage(ev.target.value) },
      LANGUAGES.map((l) => h('option', { value: l.code, selected: l.code === currentLanguage || null }, l.native + ' / ' + l.en)));
    const wrap = h('div', { class: 'lang-select' }, h('label', { for: 'lang-select' }, bi('lang.label')), sel);
    const micWrap = $('.mic-wrap', $('#stage'));
    if (micWrap) micWrap.before(wrap); else $('#stage').append(wrap);
  }

  function showView(name, opts) {
    if (!VIEWS.includes(name)) name = 'ask';
    if (name !== 'ask') stopAudio();
    currentView = name;
    VIEWS.forEach((v) => { $('#view-' + v).hidden = v !== name; });
    document.querySelectorAll('.tab').forEach((t) => { if (t.dataset.view === name) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current'); });
    try { history.replaceState(null, '', location.pathname + location.search + '#' + name); } catch (e) { /* file:// or sandbox */ }
    if (!(opts && opts.keepScroll)) window.scrollTo(0, 0);
    if (name === 'schemes' && !schemesStarted) startSchemes();
  }

  /* ================================================================
     6. ASK: recording, sending, rendering
     ================================================================ */
  const stage = $('#stage'), micBtn = $('#mic'), statusEl = $('#mic-status'), timerEl = $('#mic-timer'), resultEl = $('#result'), viewAsk = $('#view-ask'), dial = $('#dial');
  const MAX_SECONDS = 30, TICKS = 30;
  const S = { phase: 'idle', recorder: null, stream: null, chunks: [], startedAt: 0, ticker: null, autoStopped: false, lastReq: null, audio: null };

  // dial: 30 ticks, one per second of the 30 s limit
  (function buildDial() {
    const ns = 'http://www.w3.org/2000/svg';
    for (let i = 0; i < TICKS; i++) {
      const l = document.createElementNS(ns, 'line');
      l.setAttribute('x1', 120); l.setAttribute('y1', 6); l.setAttribute('x2', 120); l.setAttribute('y2', 20);
      l.setAttribute('transform', 'rotate(' + (i * 360 / TICKS) + ' 120 120)');
      l.style.setProperty('--i', i);
      dial.append(l);
    }
  })();
  function setTicks(elapsedSec) {
    const gone = Math.min(TICKS, Math.floor(elapsedSec));
    dial.childNodes.forEach((l, i) => l.classList.toggle('gone', i < gone));
  }

  function setPhase(phase) {
    S.phase = phase;
    stage.dataset.state = phase;
    const busy = phase === 'requesting' || phase === 'thinking';
    micBtn.setAttribute('aria-busy', busy ? 'true' : 'false');
    micBtn.setAttribute('aria-label', phase === 'recording' ? plain('rec.stopA11y') : plain('rec.startA11y'));
    dial.classList.toggle('sweep', phase === 'thinking' && !reduceMotion());
    $('#send-btn').disabled = busy || phase === 'recording';
    const msg = { requesting: 'rec.requesting', recording: 'rec.recording', thinking: 'rec.thinking' }[phase] || (viewAsk.dataset.result ? 'ans.newQuestion' : 'home.tapStart');
    statusEl.replaceChildren(msg ? bi(msg) : '');
    if (phase !== 'recording') { timerEl.textContent = ''; setTicks(0); }
  }
  function setResultMode(mode) {
    if (mode) viewAsk.dataset.result = mode; else delete viewAsk.dataset.result;
    viewAsk.classList.toggle('has-result', !!mode);
  }
  function stopAudio() { if (S.audio) { try { S.audio.pause(); } catch (e) { /* ignore */ } S.audio = null; } }

  function pickMime() {
    if (typeof MediaRecorder === 'undefined' || !MediaRecorder.isTypeSupported) return '';
    const c = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];
    for (const m of c) { try { if (MediaRecorder.isTypeSupported(m)) return m; } catch (e) { /* next */ } }
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
    else if (S.phase === 'idle') startRecording();
  });

  async function startRecording() {
    stopAudio();
    setPhase('requesting');
    if (isMock && !(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) return fakeRecording();
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof MediaRecorder === 'undefined') {
      return showLocalError('unsupported', 'err.unsupported', 'type');
    }
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    } catch (e) {
      const denied = e && (e.name === 'NotAllowedError' || e.name === 'SecurityError' || e.name === 'PermissionDeniedError');
      return showLocalError(denied ? 'mic_denied' : 'no_mic', denied ? 'err.micDenied' : 'err.noMic', denied ? 'record' : 'type');
    }
    const mime = pickMime();
    let rec;
    try { rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream); }
    catch (e) { stream.getTracks().forEach((t) => t.stop()); return showLocalError('unsupported', 'err.unsupported', 'type'); }
    S.stream = stream; S.recorder = rec; S.chunks = []; S.autoStopped = false;
    rec.ondataavailable = (ev) => { if (ev.data && ev.data.size) S.chunks.push(ev.data); };
    rec.onstop = onRecorderStop;
    rec.start();
    beginTicker();
  }
  function fakeRecording() { // mock mode on a device without a microphone
    S.recorder = { state: 'recording', stop() { this.state = 'inactive'; setTimeout(() => finishRecording(new Blob([new Uint8Array(3000)], { type: 'audio/webm' }), Date.now() - S.startedAt), 0); } };
    beginTicker();
  }
  function beginTicker() {
    S.startedAt = performance.now();
    setPhase('recording');
    const tick = () => {
      const el = (performance.now() - S.startedAt) / 1000;
      setTicks(el);
      const left = Math.max(0, Math.ceil(MAX_SECONDS - el));
      timerEl.textContent = left + ' ' + STRINGS.hi['rec.left'] + ' · ' + STRINGS.en['rec.left'];
      if (el >= MAX_SECONDS) { S.autoStopped = true; stopRecording(); }
    };
    tick();
    S.ticker = setInterval(tick, 100);
  }
  function stopRecording() {
    clearInterval(S.ticker); S.ticker = null;
    const r = S.recorder;
    if (r && r.state !== 'inactive') { try { r.stop(); } catch (e) { releaseStream(); } }
  }
  function releaseStream() { if (S.stream) { S.stream.getTracks().forEach((t) => t.stop()); S.stream = null; } }
  function onRecorderStop() {
    const dur = performance.now() - S.startedAt;
    const type = (S.recorder && S.recorder.mimeType) || (S.chunks[0] && S.chunks[0].type) || 'audio/webm';
    releaseStream();
    finishRecording(new Blob(S.chunks, { type }), dur);
  }
  function finishRecording(blob, durMs) {
    if (durMs < 700 || blob.size < 500) return showLocalError('too_short', 'err.tooShort', 'record');
    sendAsk({ audio: blob });
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden && S.phase === 'recording') stopRecording(); });

  $('#text-form').addEventListener('submit', (ev) => {
    ev.preventDefault();
    if (S.phase !== 'idle') return;
    const v = $('#text-input').value.trim();
    if (!v) { showLocalError('empty', 'err.emptyText', 'type'); return; }
    $('#text-input').value = '';
    sendAsk({ text: v });
  });

  function buildAskForm(req) {
    const f = new FormData();
    f.append('session_id', sessionId());
    if (req.audio) f.append('audio', req.audio, 'speech.' + extFor(req.audio.type));
    else f.append('text', req.text);
    f.append('want_audio', req.wantAudio === false || !$('#want-audio').checked ? 'false' : 'true');
    f.append('language', currentLanguage);
    return f;
  }
  async function sendAsk(req) {
    S.lastReq = req;
    setPhase('thinking');
    try {
      const data = await callApi('/api/ask', { form: buildAskForm(req) });
      setPhase('idle');
      renderAnswer(data);
    } catch (e) {
      setPhase('idle');
      showApiError(e, req);
    }
  }

  function showLocalError(code, key, action) {
    setPhase('idle');
    const s = tr(key);
    renderError({ code, message_hi: s.hi, message_en: s.en }, action);
  }
  function showApiError(e, req) {
    const code = e.code || 'unknown';
    const fallbackKey = { network: 'err.noNetwork', rate_limited: 'err.rateLimited', no_speech: 'err.noSpeech', audio_too_long: 'err.tooLong' }[code] || 'err.generic';
    const fb = tr(fallbackKey);
    const err = { code, message_hi: e.message_hi || fb.hi, message_en: e.message_en || fb.en };
    let action = 'resend';
    if (code === 'no_speech' || code === 'audio_too_long') action = 'record';
    else if (code === 'bad_request') action = 'type';
    if (code === 'tts_failed') req = Object.assign({}, req, { wantAudio: false });
    renderError(err, action, req);
  }
  function renderError(err, action, req) {
    stopAudio();
    setResultMode('error');
    const retry = () => {
      if (action === 'resend' && req) sendAsk(req);
      else if (action === 'record') startRecording();
      else { const i = $('#text-input'); i.focus(); scrollToEl($('#text-form')); }
    };
    const retryKey = action === 'type' ? 'err.typeInstead' : 'err.retry';
    resultEl.replaceChildren(
      h('section', { class: 'card err-card', role: 'alert' },
        h('div', { class: 'err-title' }, bi('err.title')),
        h('p', { class: 'err-msg', lang: 'hi' }, err.message_hi),
        h('p', { class: 'err-msg-en', lang: 'en' }, err.message_en),
        h('button', { type: 'button', class: 'btn btn-primary btn-block', onclick: retry }, bi(retryKey))
      )
    );
    setPhase('idle');
    scrollToEl(resultEl);
  }

  function renderAnswer(d) {
    stopAudio();
    const type = ['answer', 'clarify', 'refuse'].includes(d.type) ? d.type : 'answer';
    setResultMode(type);
    setPhase('idle');
    const kids = [];
    // Only shown when the SERVER says it actually answered in another language (d.language),
    // never just because that language is selected in the UI: keeps the label honest even
    // before/without full backend wiring for this parameter (see final report).
    if (d.language && d.language !== 'hi-IN' && (d.disclaimer_en || d.disclaimer_hi)) {
      kids.push(h('section', { class: 'card lang-disclaimer', role: 'note' }, icon('warn'),
        h('div', null,
          d.disclaimer_en ? h('p', { class: 'lang-disclaimer-en', lang: 'en' }, d.disclaimer_en) : null,
          d.disclaimer_hi ? h('p', { class: 'lang-disclaimer-hi', lang: 'hi' }, d.disclaimer_hi) : null)));
    }
    if (d.transcript) {
      kids.push(h('section', { class: 'card transcript' }, h('h2', null, bi('ans.youSaid')), h('p', { lang: 'hi' }, d.transcript)));
    }
    // player
    const playBtn = h('button', { type: 'button', class: 'btn btn-hat play-btn', 'aria-label': plain('ans.play') });
    const playHint = h('span', { class: 'play-hint', hidden: true }, STRINGS.hi['ans.tapToListen'] + ' / ' + STRINGS.en['ans.tapToListen']);
    const setPlayUi = (mode) => { // 'play' | 'pause' | 'replay'
      const k = { play: 'ans.play', pause: 'ans.pause', replay: 'ans.replay' }[mode];
      playBtn.replaceChildren(icon(mode), h('span', { class: 'lbl' }, bi(k)));
      playBtn.setAttribute('aria-label', plain(k));
    };
    let playRow = null;
    if (d.audio_b64) {
      const audio = new Audio('data:' + (d.audio_mime || 'audio/wav') + ';base64,' + d.audio_b64);
      S.audio = audio;
      setPlayUi('play');
      audio.addEventListener('playing', () => { setPlayUi('pause'); playHint.hidden = true; });
      audio.addEventListener('pause', () => { if (!audio.ended) setPlayUi('play'); });
      audio.addEventListener('ended', () => setPlayUi('replay'));
      playBtn.addEventListener('click', () => {
        if (!audio.paused) { audio.pause(); return; }
        if (audio.ended) audio.currentTime = 0;
        audio.play().catch(() => { playHint.hidden = false; });
      });
      playRow = h('div', { class: 'play-row' }, playBtn, playHint);
      const p = audio.play();
      if (p && p.catch) p.catch(() => { playHint.hidden = false; }); // autoplay blocked: big button + hint
    }

    // answer card
    const card = h('section', { class: 'card answer-card ' + type });
    const kickerKey = { answer: 'ans.answer', clarify: 'ans.clarifyLabel', refuse: 'ans.refuseLabel' }[type];
    card.append(h('div', { class: 'kicker' }, bi(kickerKey)));
    if (playRow) card.append(playRow);
    card.append(h('p', { class: 'answer-hi', lang: 'hi' }, d.answer_hi || ''));
    if (type === 'clarify') {
      card.append(h('div', { class: 'next-cue' }, icon('arrowDown'), bi('ans.clarifyNext')));
    }
    if (type === 'refuse') {
      card.append(h('div', { class: 'helpline-note' }, bi('ans.refuseHelp'),
        h('a', { class: 'btn btn-hat btn-block', href: 'tel:14434' }, h('span', { class: 'hi' }, '14434'), h('span', { class: 'en' }, STRINGS.hi['helpline.sub'] + ' / ' + STRINGS.en['helpline.sub']))));
    }
    // English verification
    const enPanel = h('div', { class: 'en-panel', id: 'en-panel', hidden: true }, h('span', { class: 'tag' }, 'English gloss'), h('p', { lang: 'en' }, d.answer_en || ''));
    const enBtn = h('button', { type: 'button', class: 'btn btn-block en-toggle', 'aria-expanded': 'false', 'aria-controls': 'en-panel' }, bi('ans.showEn'));
    enBtn.addEventListener('click', () => {
      const open = enPanel.hidden;
      enPanel.hidden = !open;
      enBtn.setAttribute('aria-expanded', String(open));
      enBtn.replaceChildren(bi(open ? 'ans.hideEn' : 'ans.showEn'));
    });
    card.append(enBtn, enPanel);
    kids.push(card);

    // sources
    if (Array.isArray(d.sources) && d.sources.length) {
      const list = h('ul', { class: 'sources' });
      d.sources.forEach((s) => {
        const url = safeUrl(s.url);
        list.append(h('li', { class: 'source' },
          h('span', { class: 's-title', lang: 'en' }, s.title || s.card_id || ''),
          h('span', { class: 's-meta', lang: 'en' }, [s.source_name, s.section].filter(Boolean).join(' · ')),
          url ? h('a', { class: 'btn s-link', href: url, target: '_blank', rel: 'noopener noreferrer' }, h('span', { class: 'lbl' }, bi('ans.openSource')), icon('ext')) : null));
      });
      kids.push(h('section', { class: 'card' }, h('h2', null, bi('ans.sources')), list));
    }

    // judge view
    if (d.latency_ms || d.cost_inr_est != null || d.debug) {
      const box = h('div', { class: 'judge-box judge-only' }, h('b', null, 'Judge view'));
      const lines = [];
      if (d.latency_ms) lines.push('latency_ms: ' + Object.keys(d.latency_ms).map((k) => k + '=' + d.latency_ms[k]).join('  '));
      if (d.cost_inr_est != null) lines.push('cost_inr_est: Rs ' + d.cost_inr_est);
      if (d.debug) lines.push('debug: ' + JSON.stringify(d.debug, null, 2));
      box.append(h('pre', null, lines.join('\n')));
      kids.push(box);
    }
    resultEl.replaceChildren(...kids);
    scrollToEl(resultEl);
  }

  /* ================================================================
     7. SCHEMES flow
     ================================================================ */
  const yn = (k) => [{ k: 'q.yes', v: true }, { k: 'q.no', v: false }, { k: 'q.unsure', v: undefined }];
  const QUESTIONS = [
    { id: 'age', q: 'q.age', opts: [{ k: 'q.age.u18', v: 16 }, { k: 'q.age.18_40', v: 30 }, { k: 'q.age.41_59', v: 50 }, { k: 'q.age.60', v: 62 }] },
    { id: 'monthly_income_inr', q: 'q.income', opts: [{ k: 'q.income.low', v: 6000 }, { k: 'q.income.mid', v: 12000 }, { k: 'q.income.high', v: 20000 }] },
    { id: 'occupation', q: 'q.work', opts: [{ k: 'q.work.daily', v: 'daily_wage' }, { k: 'q.work.construction', v: 'construction' }, { k: 'q.work.domestic', v: 'domestic' }, { k: 'q.work.other', v: 'other' }] },
    { id: 'is_epfo_esic_member', q: 'q.epfo', opts: yn() },
    { id: 'is_income_tax_payer', q: 'q.tax', opts: yn() },
    { id: 'is_pregnant', q: 'q.preg', opts: [{ k: 'q.preg.yes', v: true }, { k: 'q.preg.no', v: false }] }
  ];
  let schemesStarted = false, qIndex = 0, qAnswers = {}, qLabels = [];
  const schBody = $('#sch-body');

  function startSchemes() { schemesStarted = true; qIndex = 0; qAnswers = {}; qLabels = []; renderQuestion(); }
  function renderQuestion() {
    const q = QUESTIONS[qIndex];
    const bar = h('div', { class: 'progress', 'aria-hidden': 'true' }, QUESTIONS.map((_, i) => h('i', { class: i < qIndex ? 'done' : i === qIndex ? 'now' : '' })));
    const opts = h('div', { class: 'opts', role: 'group', 'aria-labelledby': 'q-text' });
    q.opts.forEach((o) => {
      opts.append(h('button', { type: 'button', class: 'btn opt', 'aria-pressed': 'false', onclick: () => answerQ(q, o) }, bi(o.k)));
    });
    const kids = [
      qIndex === 0 ? h('p', { class: 'lead' }, bi('sch.intro')) : null,
      bar,
      h('p', { class: 'q-count' }, plain('sch.progress', { n: qIndex + 1, total: QUESTIONS.length })),
      h('h2', { class: 'q-text', id: 'q-text' }, bi(q.q)),
      opts
    ];
    if (qIndex > 0) kids.push(h('div', { class: 'q-nav' }, h('button', { type: 'button', class: 'btn', onclick: () => { qIndex--; qLabels.pop(); delete qAnswers[QUESTIONS[qIndex].id]; renderQuestion(); } }, bi('sch.back'))));
    schBody.replaceChildren(...kids.filter(Boolean));
    const first = $('.opt', schBody); if (first && qIndex > 0) first.focus({ preventScroll: true });
  }
  function answerQ(q, o) {
    if (o.v !== undefined) qAnswers[q.id] = o.v; // "not sure" = field omitted -> backend returns "unknown"
    qLabels.push(o.k);
    if (qIndex < QUESTIONS.length - 1) { qIndex++; renderQuestion(); window.scrollTo(0, 0); } else submitSchemes();
  }
  async function submitSchemes() {
    schBody.replaceChildren(h('p', { class: 'spinner-note', role: 'status' }, bi('sch.checking')));
    try {
      const data = await callApi('/api/schemes', { json: qAnswers });
      renderSchemeResults(data.matches || []);
    } catch (e) {
      const fb = tr(e.code === 'network' ? 'err.noNetwork' : 'err.generic');
      schBody.replaceChildren(h('section', { class: 'card err-card', role: 'alert' },
        h('div', { class: 'err-title' }, bi('err.title')),
        h('p', { class: 'err-msg', lang: 'hi' }, e.message_hi || fb.hi), h('p', { class: 'err-msg-en', lang: 'en' }, e.message_en || fb.en),
        h('button', { type: 'button', class: 'btn btn-primary btn-block', onclick: submitSchemes }, bi('err.retry'))));
    }
    window.scrollTo(0, 0);
  }
  // The backend text quotes the representative numbers we send (16/30/50/62, Rs 6000/12000/20000).
  // The user only picked a band, so show the band instead of a made-up exact value.
  const AGE_BAND = { 16: '16-17', 30: '18-40', 50: '41-59', 62: '60 or above' };
  const INC_BAND = { 6000: 'up to Rs 8000', 12000: 'Rs 8001-15000', 20000: 'above Rs 15000' };
  function bandify(t) {
    return (t || '')
      .replace(/\bage (16|30|50|62)\b/g, (m, a) => 'age ' + AGE_BAND[a])
      .replace(/\b(?:monthly )?income Rs (6000|12000|20000)\b/g, (m, a) => m.replace(/Rs \d+/, 'in the band ' + INC_BAND[a]));
  }
  function renderSchemeResults(matches) {
    const kids = [
      h('h2', { class: 'q-text' }, bi('sch.results'))
    ];
    if (!matches.length) kids.push(h('p', { class: 'lead' }, bi('sch.noMatches')));
    matches.forEach((m) => {
      const cls = m.eligible === true ? 'yes' : m.eligible === false ? 'no' : 'unk';
      const badgeKey = { yes: 'sch.eligYes', no: 'sch.eligNo', unk: 'sch.eligUnknown' }[cls];
      const mark = { yes: '✓', no: '✕', unk: '?' }[cls]; // shape as well as colour
      kids.push(h('article', { class: 'card match ' + cls },
        h('div', { class: 'match-head' },
          h('h3', { class: 'match-name' }, m.scheme),
          h('span', { class: 'badge ' + cls }, h('span', { 'aria-hidden': 'true' }, mark), bi(badgeKey))),
        m.why_hi ? h('p', { class: 'why', lang: 'hi' }, m.why_hi) : null,
        h('p', { class: 'why', lang: 'en' }, h('span', { class: 'why-tag' }, 'English'), bandify(m.why_en)),
        (m.missing_info && m.missing_info.length) ? h('p', { class: 'missing' }, plain('sch.missing') + ': ' + m.missing_info.join(', ').replace(/_/g, ' ')) : null,
        h('button', { type: 'button', class: 'btn btn-block', onclick: () => askAbout(m.scheme) }, bi('sch.askAbout'))));
    });
    kids.push(h('p', { class: 'fine-print' }, plain('sch.disclaimer')));
    kids.push(h('button', { type: 'button', class: 'btn btn-primary btn-block', onclick: () => { startSchemes(); window.scrollTo(0, 0); } }, bi('sch.restart')));
    schBody.replaceChildren(...kids);
  }
  function askAbout(name) {
    showView('ask');
    if (S.phase === 'idle') sendAsk({ text: STRINGS.hi['sch.askQuery'].replace('{scheme}', name) });
  }

  /* ================================================================
     8. COMPLAINT flow
     ================================================================ */
  const CMP_FIELDS = [
    { id: 'worker_name', type: 'text', hint: true, autocomplete: 'off' },
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
    let input;
    if (f.type === 'textarea') input = h('textarea', { id, name: f.id, rows: 5, maxlength: 2000, lang: 'hi' });
    else input = h('input', { id, name: f.id, type: f.type, inputmode: f.type === 'number' ? 'numeric' : null, min: f.type === 'number' ? 0 : null, autocomplete: f.autocomplete || 'off', lang: 'hi' });
    return h('div', { class: 'field' }, h('label', { for: id }, bi('cmp.' + f.id)),
      f.hint ? h('p', { class: 'fine-print', style: 'margin:0 0 6px' }, plain('cmp.worker_name.hint')) : null, input);
  }
  CMP_FIELDS.forEach((f) => cmpForm.append(f.row ? h('div', { class: 'field-row' }, f.row.map(fieldEl)) : fieldEl(f)));
  const cmpMsg = h('p', { class: 'missing', role: 'alert', hidden: true });
  const cmpSubmit = h('button', { type: 'submit', class: 'btn btn-primary btn-block' }, bi('cmp.make'));
  cmpForm.append(cmpMsg, cmpSubmit);

  cmpForm.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    const fd = new FormData(cmpForm);
    const j = {};
    ['worker_name', 'state', 'employer_name', 'work_type', 'period_from', 'period_to', 'details'].forEach((k) => { j[k] = (fd.get(k) || '').toString().trim(); });
    j.wage_owed_inr = Number(fd.get('wage_owed_inr')) || 0;
    if (!j.details && !j.wage_owed_inr) { cmpMsg.textContent = plain('cmp.needOne'); cmpMsg.hidden = false; return; }
    cmpMsg.hidden = true;
    cmpSubmit.disabled = true; cmpSubmit.replaceChildren(bi('cmp.making'));
    try {
      const data = await callApi('/api/complaint-draft', { json: j });
      renderDraft(data);
    } catch (e) {
      const fb = tr(e.code === 'network' ? 'err.noNetwork' : 'err.generic');
      cmpMsg.textContent = (e.message_hi || fb.hi) + ' / ' + (e.message_en || fb.en); cmpMsg.hidden = false;
    } finally { cmpSubmit.disabled = false; cmpSubmit.replaceChildren(bi('cmp.make')); }
  });

  function renderDraft(d) {
    const toast = h('p', { class: 'toast', role: 'status' });
    const full = (d.draft_hi || '') + '\n\n----------\n\n' + (d.draft_en || '');
    const copy = () => {
      const done = () => { toast.textContent = plain('cmp.copied'); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(full).then(done, () => legacyCopy(full, done));
      else legacyCopy(full, done);
    };
    const kids = [
      d.requires_human_review !== false ? h('div', { class: 'review-banner', role: 'note' }, icon('warn'),
        h('div', null, bi('cmp.reviewBanner'), h('div', { class: 'sub' }, plain('cmp.notSent')))) : h('p', { class: 'fine-print' }, plain('cmp.notSent')),
      h('div', { class: 'btn-row no-print' },
        h('button', { type: 'button', class: 'btn btn-primary', onclick: () => window.print() }, bi('cmp.print')),
        h('button', { type: 'button', class: 'btn', onclick: copy }, bi('cmp.copy'))),
      toast,
      h('section', { class: 'card' }, h('h2', null, bi('cmp.hindiDraft')), h('pre', { class: 'draft', lang: 'hi' }, d.draft_hi || '')),
      h('section', { class: 'card' }, h('h2', null, bi('cmp.englishDraft')), h('pre', { class: 'draft en-draft', lang: 'en' }, d.draft_en || ''))
    ];
    if (Array.isArray(d.notes_en) && d.notes_en.length) {
      kids.push(h('section', { class: 'card' }, h('h2', null, bi('cmp.checklist')), h('ul', { class: 'checklist', lang: 'en' }, d.notes_en.map((n) => h('li', null, n)))));
    }
    kids.push(h('button', { type: 'button', class: 'btn btn-block no-print', onclick: () => { cmpResult.replaceChildren(); $('#cmp-form-wrap').hidden = false; window.scrollTo(0, 0); } }, bi('cmp.edit')));
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
     9. Judge toggle + boot + demo states
     ================================================================ */
  function setJudge(on) {
    document.body.classList.toggle('judge', on);
    $('#judge-toggle').setAttribute('aria-checked', String(on));
    store.set('as_judge', on ? '1' : '0');
  }
  $('#judge-toggle').addEventListener('click', () => setJudge(!document.body.classList.contains('judge')));

  async function demo(state) {
    const askText = { answer: 'मज़दूरी नहीं मिली', clarify: 'clarify', refuse: 'refuse' };
    if (state === 'recording') {
      setPhase('recording'); setTicks(12);
      timerEl.textContent = '18 ' + STRINGS.hi['rec.left'] + ' · ' + STRINGS.en['rec.left'];
    } else if (state === 'thinking') {
      setPhase('thinking');
    } else if (askText[state]) {
      const f = new FormData(); f.append('text', askText[state]); f.append('want_audio', 'true');
      renderAnswer(await mockApi('/api/ask', { form: f }));
    } else if (state === 'error') {
      const code = params.get('err') || 'no_speech';
      const e = MOCK.errors[code] || MOCK.errors.no_speech;
      renderError({ code, message_hi: e.message_hi, message_en: e.message_en }, code === 'rate_limited' ? 'resend' : 'record', S.lastReq);
    } else if (state === 'schemes') {
      showView('schemes');
      qAnswers = { age: 30, monthly_income_inr: 12000, occupation: 'construction', is_pregnant: false };
      qLabels = ['q.age.18_40', 'q.income.mid', 'q.work.construction', 'q.unsure', 'q.no', 'q.preg.no'];
      renderSchemeResults((await mockApi('/api/schemes', { json: qAnswers })).matches);
    } else if (state === 'schemes-q') {
      showView('schemes'); qIndex = 2; qLabels = ['q.age.18_40', 'q.income.mid']; renderQuestion();
    } else if (state === 'complaint-form') {
      showView('complaint');
    } else if (state === 'complaint') {
      showView('complaint');
      const j = { worker_name: '', state: 'Bihar', employer_name: 'Sharma Constructions', work_type: 'Mason helper', wage_owed_inr: 18000, period_from: '2026-06-01', period_to: '2026-08-31', details: 'तीन महीने से मज़दूरी नहीं मिली।' };
      renderDraft(await mockApi('/api/complaint-draft', { json: j }));
    }
  }

  buildChrome();
  setJudge(store.get('as_judge') === '1');
  setPhase('idle');
  const hashView = (location.hash || '').slice(1);
  showView(VIEWS.includes(hashView) ? hashView : 'ask', { keepScroll: true });
  if (isMock) {
    const st = params.get('state');
    if (st) demo(st);
    if (params.get('judge') === '1') setJudge(true);
  }
})();
