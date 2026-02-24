(() => {
  const STORAGE_KEY = 'miw_site_locale';

  const withLocaleQuery = (href, locale) => {
    try {
      const url = new URL(href, window.location.origin);
      if (url.origin !== window.location.origin) return href;
      url.searchParams.set('lang', locale);
      const normalized = `${url.pathname}${url.search}${url.hash}`;
      return normalized;
    } catch (_) {
      return href;
    }
  };

  const updateHreflang = (locales, locale) => {
    document.querySelectorAll('link[data-generated-hreflang="1"]').forEach((node) => node.remove());
    const head = document.head;

    for (const code of locales) {
      const link = document.createElement('link');
      link.rel = 'alternate';
      link.hreflang = code;
      link.href = `${window.location.origin}${withLocaleQuery(window.location.pathname, code)}`;
      link.setAttribute('data-generated-hreflang', '1');
      head.appendChild(link);
    }

    const xDefault = document.createElement('link');
    xDefault.rel = 'alternate';
    xDefault.hreflang = 'x-default';
    xDefault.href = `${window.location.origin}${withLocaleQuery(window.location.pathname, locale)}`;
    xDefault.setAttribute('data-generated-hreflang', '1');
    head.appendChild(xDefault);
  };

  const pageMetaKeys = (page) => {
    if (page === 'support') {
      return { title: 'supportPageTitle', description: 'supportPageDescription' };
    }
    if (page === 'privacy') {
      return { title: 'privacyPageTitle', description: 'privacyPageDescription' };
    }
    return { title: 'pageTitle', description: 'pageDescription' };
  };

  const applyBundle = (bundle, payload, locale) => {
    const page = document.body?.dataset?.page || 'home';
    const metaKeys = pageMetaKeys(page);

    document.documentElement.lang = locale;
    document.documentElement.dir = (payload.rtlLocales || []).includes(locale.split('-')[0]) ? 'rtl' : 'ltr';

    document.title = bundle[metaKeys.title] || bundle.pageTitle || document.title;
    const metaDesc = document.querySelector('meta[name="description"]');
    if (metaDesc) {
      const description = bundle[metaKeys.description] || bundle.pageDescription || '';
      if (description) metaDesc.setAttribute('content', description);
    }

    for (const node of document.querySelectorAll('[data-i18n]')) {
      const key = node.getAttribute('data-i18n');
      if (!key) continue;
      const value = bundle[key];
      if (typeof value === 'string' && value.length > 0) {
        node.textContent = value;
      }
    }

    for (const node of document.querySelectorAll('[data-i18n-placeholder]')) {
      const key = node.getAttribute('data-i18n-placeholder');
      if (!key) continue;
      const value = bundle[key];
      if (typeof value === 'string' && value.length > 0) {
        node.setAttribute('placeholder', value);
      }
    }

    for (const node of document.querySelectorAll('[data-updated-at]')) {
      node.textContent = payload.updatedAt || '';
    }

    for (const node of document.querySelectorAll('a[data-appstore-link]')) {
      node.setAttribute('href', payload.appStoreUrl || 'https://apps.apple.com/app/id6758521973');
    }

    for (const node of document.querySelectorAll('a[data-keep-locale]')) {
      const raw = node.getAttribute('href') || '/';
      node.setAttribute('href', withLocaleQuery(raw, locale));
    }

    updateHreflang(payload.availableLocales || [], locale);
  };

  const initLocaleSelect = (select, locales, selected, inLocale, onChange) => {
    if (!select) return;
    select.innerHTML = '';

    for (const locale of locales) {
      const option = document.createElement('option');
      option.value = locale;
      option.textContent = window.MIWI18N.getDisplayName(locale, inLocale);
      if (locale === selected) option.selected = true;
      select.appendChild(option);
    }

    select.onchange = (event) => {
      const nextLocale = event.target.value;
      onChange(nextLocale);
    };
  };

  const persistLocale = (locale) => {
    try {
      window.localStorage.setItem(STORAGE_KEY, locale);
    } catch (_) {
      // ignore
    }
  };

  const loadPersistedLocale = () => {
    try {
      return window.localStorage.getItem(STORAGE_KEY) || '';
    } catch (_) {
      return '';
    }
  };

  const currentLangFromURL = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('lang') || '';
  };

  const replaceURLLocale = (locale) => {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', locale);
    window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
  };

  document.addEventListener('DOMContentLoaded', async () => {
    const payload = await window.MIWI18N.loadTranslations();
    const available = payload.availableLocales || [];

    const requested = currentLangFromURL() || loadPersistedLocale();
    const locale = window.MIWI18N.resolveLocale(requested, available, payload.defaultLocale || 'en-US');

    const applyLocale = (target) => {
      const resolved = window.MIWI18N.resolveLocale(target, available, payload.defaultLocale || 'en-US');
      const bundle = payload.labels?.[resolved] || payload.labels?.[payload.defaultLocale] || {};
      applyBundle(bundle, payload, resolved);
      persistLocale(resolved);
      replaceURLLocale(resolved);
      initLocaleSelect(document.querySelector('#locale-select'), available, resolved, resolved, applyLocale);
    };

    applyLocale(locale);
  });
})();
