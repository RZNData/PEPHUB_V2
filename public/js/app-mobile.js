/**
 * PEP HUB Mobile & PWA Controller v2.6.0 — Regional Norte
 * Melhores Práticas PWA / Mobile:
 * 1. Registro e ciclo de vida do Service Worker (com detecção de atualização e skipWaiting)
 * 2. Detecção de modo Standalone / App Instalado
 * 3. Onboarding de Instalação (Android/Chrome nativo + iOS/Safari Share Sheet guidance)
 * 4. Monitor de Conectividade em tempo real (Online / Offline badge)
 * 5. Barra de Navegação Inferior Nativa (Bottom Nav) com rotas ativas dinâmicas e Safe Areas
 * 6. Suporte a Biometria WebAuthn (Touch ID, Face ID, Windows Hello)
 * 7. Feedback tátil (Haptic feedback) em dispositivos suportados
 */

(function() {
  'use strict';

  // 1. Registro e Ciclo de Vida do Service Worker
  let newWorkerWaiting = false;

  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => {
          console.log('[PEP HUB App] Service Worker registrado:', reg.scope);

          // Verifica se já existe um worker esperando
          if (reg.waiting) {
            notifyUpdateReady(reg.waiting);
          }

          // Listener para novas versões encontradas
          reg.addEventListener('updatefound', () => {
            const installingWorker = reg.installing;
            if (installingWorker) {
              installingWorker.addEventListener('statechange', () => {
                if (installingWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  notifyUpdateReady(installingWorker);
                }
              });
            }
          });

          // Checagem periódica e ao focar a aba
          if (reg.update) {
            setInterval(() => reg.update(), 1000 * 60 * 60);
            window.addEventListener('focus', () => reg.update());
          }
        })
        .catch(err => {
          console.warn('[PEP HUB App] Aviso no Service Worker:', err);
        });

      // Recarrega página quando o novo worker assume o controle
      let refreshing = false;
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (!refreshing) {
          refreshing = true;
          window.location.reload();
        }
      });
    });
  }

  function notifyUpdateReady(worker) {
    newWorkerWaiting = true;
    let toast = document.getElementById('pwaUpdateToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'pwaUpdateToast';
      toast.className = 'pwa-update-toast';
      toast.innerHTML = `
        <span>Nova versão do PEP HUB disponível!</span>
        <button id="btnPwaUpdateNow">Atualizar Agora</button>
      `;
      document.body.appendChild(toast);
      document.getElementById('btnPwaUpdateNow').addEventListener('click', () => {
        worker.postMessage({ type: 'SKIP_WAITING' });
        toast.classList.remove('visible');
      });
    }
    setTimeout(() => toast.classList.add('visible'), 1000);
  }

  // 2. Detecção de Modo Standalone (App Instalado na Home Screen)
  const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                       window.navigator.standalone === true ||
                       document.referrer.includes('android-app://');

  if (isStandalone) {
    document.documentElement.classList.add('is-pwa-standalone');
    console.log('[PEP HUB App] Rodando em modo Standalone (App Nativo)');
  }

  // 3. Detecção de Dispositivo iOS
  const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test(userAgent);
  };

  const isInStandaloneMode = () => ('standalone' in window.navigator) && (window.navigator.standalone);

  // 4. Captura do Evento de Instalação (beforeinstallprompt) para Android/Desktop
  let deferredPrompt = null;

  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredPrompt = e;

    // Exibe botões de instalação
    const installBtns = document.querySelectorAll('#btnPwaInstallHeader, .pwa-install-trigger');
    installBtns.forEach(btn => btn.style.display = 'inline-flex');

    if (!isStandalone && !sessionStorage.getItem('pephub_pwa_dismissed')) {
      showInstallBanner();
    }
  });

  window.addEventListener('appinstalled', () => {
    console.log('[PEP HUB App] Aplicativo instalado com sucesso no dispositivo!');
    deferredPrompt = null;
    hideInstallBanner();
    const installBtns = document.querySelectorAll('#btnPwaInstallHeader, .pwa-install-trigger');
    installBtns.forEach(btn => btn.style.display = 'none');
  });

  // Função global de disparo de instalação
  window.triggerPwaInstall = function() {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then(choiceResult => {
        if (choiceResult.outcome === 'accepted') {
          console.log('[PEP HUB App] Instalação aceita pelo usuário');
        }
        deferredPrompt = null;
        hideInstallBanner();
      });
    } else if (isIos() && !isInStandaloneMode()) {
      showIosInstallModal();
    } else {
      alert('Para instalar o PEP HUB:\n• No Android/Chrome: Toque no menu (⋮) e selecione "Instalar aplicativo".\n• No iPhone/Safari: Toque em Compartilhar e selecione "Adicionar à Tela de Início".');
    }
  };

  function showInstallBanner() {
    let banner = document.getElementById('pwaInstallBanner');
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'pwaInstallBanner';
      banner.className = 'pwa-install-banner';
      banner.innerHTML = `
        <div class="pwa-banner-content">
          <img src="/icons/icon-192.png" alt="PEP HUB App" class="pwa-banner-icon">
          <div class="pwa-banner-text">
            <strong>Instalar App do PEP HUB</strong>
            <span>Acesso instantâneo e offline na tela inicial</span>
          </div>
        </div>
        <div class="pwa-banner-actions">
          <button class="pwa-banner-dismiss" onclick="dismissPwaBanner()">Agora não</button>
          <button class="pwa-banner-btn" onclick="triggerPwaInstall()">Instalar</button>
        </div>
      `;
      document.body.appendChild(banner);
    }
    requestAnimationFrame(() => banner.classList.add('visible'));
  }

  function hideInstallBanner() {
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) banner.classList.remove('visible');
  }

  window.dismissPwaBanner = function() {
    hideInstallBanner();
    sessionStorage.setItem('pephub_pwa_dismissed', '1');
  };

  function showIosInstallModal() {
    let modal = document.getElementById('iosInstallModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'iosInstallModal';
      modal.className = 'pwa-ios-modal';
      modal.innerHTML = `
        <div class="pwa-ios-card">
          <div class="pwa-ios-header">
            <img src="/icons/icon-192.png" alt="PEP HUB" class="pwa-ios-logo">
            <h3>Instalar PEP HUB no iPhone</h3>
            <button class="pwa-ios-close" onclick="closeIosInstallModal()">✕</button>
          </div>
          <ol class="pwa-ios-steps">
            <li>Toque no botão de <strong>Compartilhar</strong> <span class="ios-share-ico">⎋</span> na barra inferior do Safari.</li>
            <li>Role as opções e selecione <strong>"Adicionar à Tela de Início"</strong>.</li>
            <li>Toque em <strong>"Adicionar"</strong> no canto superior direito.</li>
          </ol>
          <p class="pwa-ios-footer">O PEP HUB funcionará em tela cheia como um aplicativo nativo!</p>
          <button class="pwa-ios-done-btn" onclick="closeIosInstallModal()">Entendi</button>
        </div>
      `;
      document.body.appendChild(modal);
    }
    modal.classList.add('visible');
  }

  window.closeIosInstallModal = function() {
    const modal = document.getElementById('iosInstallModal');
    if (modal) modal.classList.remove('visible');
    sessionStorage.setItem('pephub_pwa_dismissed', '1');
  };

  // Se for iOS no Safari (não-standalone) e ainda não dispensou, oferece dica sutil
  if (isIos() && !isInStandaloneMode() && !sessionStorage.getItem('pephub_pwa_dismissed')) {
    window.addEventListener('load', () => {
      setTimeout(() => {
        const installBtns = document.querySelectorAll('#btnPwaInstallHeader, .pwa-install-trigger');
        installBtns.forEach(btn => btn.style.display = 'inline-flex');
      }, 1500);
    });
  }

  // 5. Monitor de Status Online / Offline
  function updateNetworkStatus() {
    const isOnline = navigator.onLine;
    let badge = document.getElementById('pwaNetworkStatus');
    if (!badge) {
      badge = document.createElement('div');
      badge.id = 'pwaNetworkStatus';
      badge.className = 'pwa-network-badge';
      document.body.appendChild(badge);
    }

    if (isOnline) {
      badge.innerHTML = '<span class="net-dot online"></span> Conectado';
      badge.classList.remove('offline');
      badge.classList.add('online');
      setTimeout(() => {
        badge.classList.add('faded');
      }, 3500);
    } else {
      badge.innerHTML = '<span class="net-dot offline"></span> Modo Offline (Cache Local)';
      badge.classList.remove('online', 'faded');
      badge.classList.add('offline');
    }
  }

  window.addEventListener('online', updateNetworkStatus);
  window.addEventListener('offline', updateNetworkStatus);
  window.addEventListener('DOMContentLoaded', updateNetworkStatus);

  // 6. Barra Inferior Mobile para Navegação Rápida (Bottom Nav) com rotas ativas
  function setupMobileBottomNav() {
    if (document.getElementById('pwaBottomNav')) return;

    // Rotas principais
    const currentPath = window.location.pathname;

    const nav = document.createElement('nav');
    nav.id = 'pwaBottomNav';
    nav.className = 'pwa-bottom-nav';
    nav.setAttribute('aria-label', 'Navegação Principal Mobile');

    nav.innerHTML = `
      <a href="/" class="pwa-nav-item" data-route="/">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>Início</span>
      </a>
      <a href="/churn/" class="pwa-nav-item" data-route="/churn/">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2">
          <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
          <polyline points="17 6 23 6 23 12"/>
        </svg>
        <span>Safra</span>
      </a>
      <a href="/fpd/" class="pwa-nav-item" data-route="/fpd/">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <span>FPD</span>
      </a>
      <a href="/panorama-market-share/" class="pwa-nav-item" data-route="/panorama-market-share/">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
          <path d="M22 12A10 10 0 0 0 12 2v10z"/>
        </svg>
        <span>Share</span>
      </a>
      <a href="/podcast/" class="pwa-nav-item" data-route="/podcast/">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
          <line x1="12" y1="19" x2="12" y2="23"/>
          <line x1="8" y1="23" x2="16" y2="23"/>
        </svg>
        <span>Podcast</span>
      </a>
    `;

    // Atualiza classe active dinamicamente
    const navItems = nav.querySelectorAll('.pwa-nav-item');
    navItems.forEach(item => {
      const route = item.getAttribute('data-route');
      if (route === '/' && (currentPath === '/' || currentPath === '/index.html')) {
        item.classList.add('active');
      } else if (route !== '/' && currentPath.startsWith(route)) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }

      // Haptic feedback se suportado
      item.addEventListener('click', () => {
        if ('vibrate' in navigator) {
          try { navigator.vibrate(15); } catch (_) {}
        }
      });
    });

    document.body.appendChild(nav);
  }

  window.addEventListener('DOMContentLoaded', setupMobileBottomNav);

  // 7. Módulo de Biometria / WebAuthn (TouchID / FaceID)
  window.pephubBiometrics = {
    isAvailable: function() {
      return !!(window.PublicKeyCredential && 
             PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable);
    },
    checkSupport: async function() {
      if (!this.isAvailable()) return false;
      try {
        return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
      } catch (e) {
        return false;
      }
    }
  };

})();
