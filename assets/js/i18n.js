(() => {
  const I18N_URL = '/assets/i18n/translations.json';
  let payloadPromise = null;

  const normalizeLocale = (value) => {
    if (!value || typeof value !== 'string') return '';
    return value.replace('_', '-').trim();
  };

  const localeCandidates = (locale) => {
    const normalized = normalizeLocale(locale);
    if (!normalized) return [];

    const [lang, region] = normalized.split('-');
    const candidates = [normalized];

    if (lang && region) {
      candidates.push(`${lang}-${region.toUpperCase()}`);
      candidates.push(lang);
    }
    if (lang === 'zh' && region) {
      if (/hans/i.test(region)) candidates.push('zh-Hans');
      if (/hant|tw|hk/i.test(region)) candidates.push('zh-Hant');
    }

    if (lang === 'es') {
      candidates.push('es-ES', 'es-419');
    }
    if (lang === 'en') {
      candidates.push('en-US', 'en-GB', 'en-CA', 'en-AU', 'en');
    }

    return [...new Set(candidates.filter(Boolean))];
  };

  const resolveLocale = (preferred, available, fallback) => {
    const set = new Set(available || []);

    for (const cand of localeCandidates(preferred)) {
      if (set.has(cand)) return cand;
    }

    if (Array.isArray(navigator.languages)) {
      for (const browserLocale of navigator.languages) {
        for (const cand of localeCandidates(browserLocale)) {
          if (set.has(cand)) return cand;
        }
      }
    }

    const nav = normalizeLocale(navigator.language || '');
    for (const cand of localeCandidates(nav)) {
      if (set.has(cand)) return cand;
    }

    return set.has(fallback) ? fallback : (available && available[0]) || 'en-US';
  };

  const loadTranslations = async () => {
    if (!payloadPromise) {
      payloadPromise = fetch(I18N_URL, { cache: 'no-cache' }).then((res) => {
        if (!res.ok) throw new Error(`i18n fetch failed: ${res.status}`);
        return res.json();
      });
    }
    return payloadPromise;
  };

  const getDisplayName = (targetLocale, inLocale) => {
    try {
      const display = new Intl.DisplayNames([inLocale || targetLocale || 'en-US'], { type: 'language' });
      const base = targetLocale.split('-')[0];
      const label = display.of(base) || targetLocale;
      if (targetLocale.includes('-') && !/^zh-(Hans|Hant)$/i.test(targetLocale)) {
        return `${label} (${targetLocale})`;
      }
      return label;
    } catch (_) {
      return targetLocale;
    }
  };

  window.MIWI18N = {
    loadTranslations,
    resolveLocale,
    getDisplayName,
    normalizeLocale,
  };
})();
