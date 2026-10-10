/**
 * Helper de Validação e Autorização de Telefones (WhatsApp Bot)
 */

let authorizedPhonesCache = {
  lastFetch: 0,
  bot_suspended: false,
  phonesSet: new Set(),
  usersList: [],
};
const CACHE_TTL_MS = 30 * 1000; // 30 segundos

function getPhoneVariations(phone) {
  if (!phone) return [];
  const digits = String(phone).replace(/\D/g, '');
  const set = new Set();
  set.add(digits);

  let local = digits;
  if (digits.startsWith('55') && digits.length > 10) {
    local = digits.slice(2);
    set.add(local);
  }

  if (local.length === 11 && local[2] === '9') {
    const without9 = local.slice(0, 2) + local.slice(3);
    set.add(without9);
    set.add('55' + without9);
  } else if (local.length === 10) {
    const with9 = local.slice(0, 2) + '9' + local.slice(2);
    set.add(with9);
    set.add('55' + with9);
  }
  return Array.from(set);
}

async function fetchAuthorizedPhones(apiUrl = 'https://pephub.cloud') {
  const now = Date.now();
  if (now - authorizedPhonesCache.lastFetch < CACHE_TTL_MS && authorizedPhonesCache.lastFetch > 0) {
    return authorizedPhonesCache;
  }

  const base = apiUrl.replace(/\/+$/, '');
  try {
    const res = await fetch(`${base}/api/auth/authorized-phones`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      signal: AbortSignal.timeout(6000),
    });

    if (res.ok) {
      const data = await res.json();
      const phoneSet = new Set();
      const rawPhones = data.phones || [];
      for (const p of rawPhones) {
        const tel = typeof p === 'object' ? p.telefone : p;
        getPhoneVariations(tel).forEach(v => phoneSet.add(v));
      }

      authorizedPhonesCache = {
        lastFetch: now,
        bot_suspended: Boolean(data.bot_suspended),
        phonesSet: phoneSet,
        usersList: rawPhones,
      };
      return authorizedPhonesCache;
    }
  } catch (err) {
    console.error('[Auth Cache] Falha ao consultar telefones autorizados:', err.message);
  }

  return authorizedPhonesCache;
}

async function verifySenderAccess(senderJid, isFromMe, apiUrl) {
  const auth = await fetchAuthorizedPhones(apiUrl);
  const digits = String(senderJid || '').split('@')[0].split(':')[0].replace(/\D/g, '');

  if (auth.bot_suspended) {
    return { allowed: false, reason: 'suspended', phone: digits };
  }

  const variations = getPhoneVariations(digits);
  const isMatch = variations.some(v => auth.phonesSet.has(v));

  if (isMatch) {
    const userObj = auth.usersList.find(u => {
      const uVars = getPhoneVariations(u.telefone);
      return variations.some(v => uVars.includes(v));
    });
    return { allowed: true, phone: digits, user: userObj || null };
  }

  return { allowed: false, reason: 'unregistered', phone: digits };
}

module.exports = {
  getPhoneVariations,
  fetchAuthorizedPhones,
  verifySenderAccess,
};
