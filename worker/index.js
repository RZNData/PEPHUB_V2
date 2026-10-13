/**
 * Cloudflare Worker — Pephub Plataforma Regional
 * Arquitetura Modularizada (Rotas de Autenticação, Administração, TV e Proteção de Assets)
 */

import {
  SECURITY_HEADERS,
  json,
  getSessionUser,
  logAccess,
  checkReportAccess,
  getSystemControl,
  isModuleSuspended,
  renderMaintenanceResponse,
  ensureAppSchema,
  canManageUploads,
  parseCookies,
  deleteSession,
} from './utils/security.js';
import { handleAuthRoutes } from './routes/auth.js';
import { handleAdminRoutes } from './routes/admin.js';
import { handleAccessRoutes } from './routes/access.js';
import { handleTvRoutes, ensureTvSchema } from './routes/tv.js';
import { handleBotRoutes } from './routes/bot.js';
import { handleUploadRoutes } from './routes/uploads.js';
import { handleNotificationRoutes } from './routes/notifications.js';
import { handleProfileRoutes } from './routes/profile.js';

function isStaticAssetPath(path) {
  return /\.(css|js|png|jpg|jpeg|webp|svg|ico|woff|woff2|ttf|mp3|webmanifest|json|map)$/i.test(path);
}

async function enforceAuthRedirect(request, env, url, targetPath = null) {
  const cookies = parseCookies(request);
  const clearCookie = await deleteSession(cookies['pephub_session'], env);
  const redirectTarget = targetPath ? `/login/?redirect=${encodeURIComponent(targetPath)}` : '/login/';
  return new Response(null, {
    status: 302,
    headers: {
      'Location': `${url.origin}${redirectTarget}`,
      'Set-Cookie': clearCookie,
      'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
}

function recordAccess(ctx, env, request, user, recurso) {
  if (!user) return;
  if (ctx && typeof ctx.waitUntil === 'function') {
    ctx.waitUntil(logAccess(env, request, user, recurso));
  } else {
    logAccess(env, request, user, recurso).catch(() => {});
  }
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const pathname = url.pathname;
    const ip = request.headers.get('cf-connecting-ip') || request.headers.get('x-forwarded-for') || '127.0.0.1';

    // 0. Fast Bypass para arquivos estáticos (CSS, JS, Imagens, Fontes) — 0.1ms de CPU
    if (isStaticAssetPath(pathname)) {
      const res = await env.ASSETS.fetch(request);
      const headers = new Headers(res.headers);
      for (const [key, val] of Object.entries(SECURITY_HEADERS)) {
        headers.set(key, val);
      }
      if (pathname === '/sw.js') {
        headers.set('Content-Type', 'application/javascript; charset=utf-8');
        headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
        headers.set('Pragma', 'no-cache');
        headers.set('Expires', '0');
      } else if (/\.(png|jpg|jpeg|webp|svg|ico|mp3|woff|woff2|ttf)$/i.test(pathname)) {
        headers.set('Cache-Control', 'public, max-age=604800, stale-while-revalidate=86400');
      } else if (/\.(css|js)$/i.test(pathname)) {
        headers.set('Cache-Control', 'public, max-age=0, must-revalidate');
      }
      return new Response(res.body, { status: res.status, headers });
    }

    // 1. Healthcheck imediato (0ms)
    if (pathname === '/health') {
      return json({ status: 'ok', service: 'pephub-regional', timestamp: new Date().toISOString() });
    }

    // 2. Roteamento amigável e direto para o Player TV (100% público sem login para Smart TVs)
    const isTvPath = pathname === '/tv' || pathname === '/tv/' || pathname.startsWith('/tv/') ||
      pathname === '/pep-tools/divulgacao/tv' || pathname === '/pep-tools/divulgacao/tv/' ||
      pathname.endsWith('/tv.html') || pathname.endsWith('/tv.html/');
    if (isTvPath) {
      const assetUrl = new URL('/tv/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      for (const [k, v] of Object.entries(SECURITY_HEADERS)) {
        headers.set(k, v);
      }
      return new Response(res.body, { status: 200, headers });
    }
    if (pathname === '/divulgacao' || pathname === '/divulgacao/' || pathname === '/pep-tools/divulgacao') {
      return Response.redirect(`${url.origin}/pep-tools/divulgacao/`, 301);
    }
    if (pathname === '/churn') {
      return Response.redirect(`${url.origin}/churn/`, 301);
    }
    if (pathname === '/evolucao-carteira') {
      return Response.redirect(`${url.origin}/evolucao-carteira/`, 301);
    }

    // 3. Bot WhatsApp Fast-Router (Atende consultas instantaneamente em 20ms sem overhead de schema)
    if (pathname.startsWith('/api/bot/')) {
      const botRes = await handleBotRoutes(request, env, url, pathname);
      if (botRes) return botRes;
    }

    // 4. Executa schema apenas sob demanda em rotas administrativas de escrita/configuração
    if (pathname.startsWith('/api/admin/')) {
      await ensureAppSchema(env);
    }

    // 5. Sub-roteadores Modulares
    // Presença (heartbeat) e solicitações de acesso a relatórios
    if (pathname === '/api/auth/heartbeat' || pathname.startsWith('/api/access-requests') || pathname.startsWith('/api/admin/access-requests')) {
      const accessRes = await handleAccessRoutes(request, env, url, pathname);
      if (accessRes) return accessRes;
    }

    const authRes = await handleAuthRoutes(request, env, url, pathname, ip);
    if (authRes) return authRes;

    const adminRes = await handleAdminRoutes(request, env, url, pathname);
    if (adminRes) return adminRes;

    const tvRes = await handleTvRoutes(request, env, url, pathname);
    if (tvRes) return tvRes;

    const uploadRes = await handleUploadRoutes(request, env, url, pathname);
    if (uploadRes) return uploadRes;

    const notifRes = await handleNotificationRoutes(request, env, url, pathname);
    if (notifRes) return notifRes;

    const profileRes = await handleProfileRoutes(request, env, url, pathname, ctx);
    if (profileRes) return profileRes;

    // 6. Log e proteção do Portal Home (Redirecionamento para Login se não autenticado)
    if (pathname === '/' || pathname === '/index.html') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/');
      }
      recordAccess(ctx, env, request, user, 'PORTAL_HOME');
      if (await getSystemControl(env, 'suspend_portal_access')) {
        if (!user.is_admin) {
          return renderMaintenanceResponse('Portal Regional');
        }
      }
    }

    // 7. Proteção de Rotas & Permissões Granulares (ignora assets estáticos subjacentes)
    if (pathname.startsWith('/churn') && !pathname.startsWith('/churn-bl-') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'churn'))) {
        return renderMaintenanceResponse('Painel Churn Safra');
      }
      if (!checkReportAccess(user, 'churn')) {
        return Response.redirect(`${url.origin}/?denied=churn`, 302);
      }
      recordAccess(ctx, env, request, user, 'CHURN_SAFRA');
    }

    // Proteção de rotas do painel /churn-bl-total/*
    if (pathname.startsWith('/churn-bl-total') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'churn-bl-total'))) {
        return renderMaintenanceResponse('Painel Churn Banda Larga Total');
      }
      if (!checkReportAccess(user, 'churn-bl-total')) {
        return Response.redirect(`${url.origin}/?denied=churn-bl-total`, 302);
      }
      recordAccess(ctx, env, request, user, 'CHURN_BL_TOTAL');
    }

    // Proteção de rotas do painel /churn-bl-pme/*
    if (pathname.startsWith('/churn-bl-pme') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'churn-bl-pme'))) {
        return renderMaintenanceResponse('Painel Churn Banda Larga PME');
      }
      if (!checkReportAccess(user, 'churn-bl-pme')) {
        return Response.redirect(`${url.origin}/?denied=churn-bl-pme`, 302);
      }
      recordAccess(ctx, env, request, user, 'CHURN_BL_PME');
    }

    // Proteção de rotas do painel /fpd/*
    if ((pathname === '/fpd' || pathname.startsWith('/fpd/')) && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'fpd'))) {
        return renderMaintenanceResponse('Painel FPD Regional Norte');
      }
      if (!checkReportAccess(user, 'fpd')) {
        return Response.redirect(`${url.origin}/?denied=fpd`, 302);
      }
      recordAccess(ctx, env, request, user, 'FPD_REGIONAL_NORTE');
    }

    // Proteção de rotas do painel /fpd-residencial/*
    if (pathname.startsWith('/fpd-residencial') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'fpd-residencial'))) {
        return renderMaintenanceResponse('FPD Residencial Executivo');
      }
      if (!checkReportAccess(user, 'fpd-residencial')) {
        return Response.redirect(`${url.origin}/?denied=fpd-residencial`, 302);
      }
      recordAccess(ctx, env, request, user, 'FPD_RESIDENCIAL');
    }

    // Proteção de rotas do painel /panorama-market-share/*
    if (pathname.startsWith('/panorama-market-share') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'panorama-market-share'))) {
        return renderMaintenanceResponse('Panorama Market Share');
      }
      if (!checkReportAccess(user, 'panorama-market-share')) {
        return Response.redirect(`${url.origin}/?denied=panorama-market-share`, 302);
      }
      recordAccess(ctx, env, request, user, 'PANORAMA_MARKET_SHARE');
    }

    // Proteção de rotas do painel /market-share-residencial/*
    if (pathname.startsWith('/market-share-residencial') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'market-share-residencial'))) {
        return renderMaintenanceResponse('Market Share Residencial');
      }
      if (!checkReportAccess(user, 'market-share-residencial')) {
        return Response.redirect(`${url.origin}/?denied=market-share-residencial`, 302);
      }
      recordAccess(ctx, env, request, user, 'MARKET_SHARE_RESIDENCIAL');
    }

    // Proteção de rotas do painel /market-share-movel/*
    if (pathname.startsWith('/market-share-movel') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'market-share-movel'))) {
        return renderMaintenanceResponse('Market Share Móvel');
      }
      if (!checkReportAccess(user, 'market-share-movel')) {
        return Response.redirect(`${url.origin}/?denied=market-share-movel`, 302);
      }
      recordAccess(ctx, env, request, user, 'MARKET_SHARE_MOVEL');
    }

    // Proteção de rotas do painel /aprovacao-credito/*
    if (pathname.startsWith('/aprovacao-credito') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'aprovacao-credito'))) {
        return renderMaintenanceResponse('Taxa de Aprovação de Crédito');
      }
      if (!checkReportAccess(user, 'aprovacao-credito')) {
        return Response.redirect(`${url.origin}/?denied=aprovacao-credito`, 302);
      }
      recordAccess(ctx, env, request, user, 'APROVACAO_CREDITO');
    }

    // Proteção de rotas do painel /evolucao-carteira/*
    if (pathname.startsWith('/evolucao-carteira') && !pathname.includes('/download') && !pathname.includes('/export') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, 'evolucao-carteira'))) {
        return renderMaintenanceResponse('Painel Evolução de Carteira');
      }
      if (!checkReportAccess(user, 'evolucao-carteira')) {
        return Response.redirect(`${url.origin}/?denied=evolucao-carteira`, 302);
      }
      recordAccess(ctx, env, request, user, 'EVOLUCAO_CARTEIRA');
    }

    // Proteção de rotas de PeP Tools (Divulgação Corporativa, Aniversário e Market Share)
    const isPublicTvPlayer = pathname === '/tv' || pathname === '/tv/' || pathname.startsWith('/tv/') ||
      pathname.includes('/divulgacao/tv') || pathname.endsWith('/tv.html') || pathname.endsWith('/tv.html/');
    if (pathname.startsWith('/pep-tools') && !isStaticAssetPath(pathname) && !isPublicTvPlayer) {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, pathname + url.search);
      }
      const isDivulgacao = pathname.startsWith('/pep-tools/divulgacao');
      const moduleKey = isDivulgacao ? 'divulgacao' : 'pep-tools';
      const moduleName = isDivulgacao ? 'Divulgação Corporativa' : 'PeP Tools';

      if (!user.is_admin && (await getSystemControl(env, 'suspend_portal_access') || await isModuleSuspended(env, moduleKey))) {
        return renderMaintenanceResponse(moduleName);
      }
      if (!checkReportAccess(user, moduleKey)) {
        return Response.redirect(`${url.origin}/?denied=${moduleKey}`, 302);
      }
      recordAccess(ctx, env, request, user, `PEP_TOOLS:${moduleKey.toUpperCase()}`);
    }

    // Proteção da rota /admin/
    if (pathname.startsWith('/admin') && !isStaticAssetPath(pathname)) {
      const user = await getSessionUser(request, env);
      const isDelegatedUpload = user ? await canManageUploads(user, env) : false;
      if (!user || user.status !== 'aprovado' || (!user.is_admin && !isDelegatedUpload)) {
        return await enforceAuthRedirect(request, env, url, '/admin/');
      }
      recordAccess(ctx, env, request, user, user.is_admin ? 'ADMIN_PANEL' : 'ADMIN_PANEL_DELEGATED_UPLOADS');
    }

    // ==========================================
    // DOWNLOAD DIRETO DOS HTMLs ANEXOS (COM TELEMETRIA DE EXPORTAÇÃO)
    // ==========================================

    // Download /churn/download
    if (pathname === '/churn/download' || pathname === '/churn/download/' || pathname === '/churn/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/churn/download');
      }
      if (!checkReportAccess(user, 'churn')) {
        return Response.redirect(`${url.origin}/?denied=churn`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:CHURN_SAFRA');
      const assetUrl = new URL('/churn/Painel_Churn_Safra.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Painel_Churn_Safra_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /churn-bl-total/download
    if (pathname === '/churn-bl-total/download' || pathname === '/churn-bl-total/download/' || pathname === '/churn-bl-total/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/churn-bl-total/download');
      }
      if (!checkReportAccess(user, 'churn-bl-total')) {
        return Response.redirect(`${url.origin}/?denied=churn-bl-total`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:CHURN_BL_TOTAL');
      const assetUrl = new URL('/churn-bl-total/Painel_Churn_Banda_Larga_Total.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Painel_Churn_Banda_Larga_Total.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /churn-bl-pme/download
    if (pathname === '/churn-bl-pme/download' || pathname === '/churn-bl-pme/download/' || pathname === '/churn-bl-pme/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/churn-bl-pme/download');
      }
      if (!checkReportAccess(user, 'churn-bl-pme')) {
        return Response.redirect(`${url.origin}/?denied=churn-bl-pme`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:CHURN_BL_PME');
      const assetUrl = new URL('/churn-bl-pme/Painel_Churn_Banda_Larga_PME.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Painel_Churn_Banda_Larga_PME.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /fpd/download
    if (pathname === '/fpd/download' || pathname === '/fpd/download/' || pathname === '/fpd/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/fpd/download');
      }
      if (!checkReportAccess(user, 'fpd')) {
        return Response.redirect(`${url.origin}/?denied=fpd`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:FPD');
      const assetUrl = new URL('/fpd/Painel_FPD_Regional_Norte.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Painel_FPD_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /fpd-residencial/download
    if (pathname === '/fpd-residencial/download' || pathname === '/fpd-residencial/download/' || pathname === '/fpd-residencial/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/fpd-residencial/download');
      }
      if (!checkReportAccess(user, 'fpd-residencial')) {
        return Response.redirect(`${url.origin}/?denied=fpd-residencial`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:FPD_RESIDENCIAL');
      const assetUrl = new URL('/fpd-residencial/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="FPD_Residencial_Executivo_Fixa.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /market-share-residencial/download
    if (pathname === '/market-share-residencial/download' || pathname === '/market-share-residencial/download/' || pathname === '/market-share-residencial/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/market-share-residencial/download');
      }
      if (!checkReportAccess(user, 'market-share-residencial')) {
        return Response.redirect(`${url.origin}/?denied=market-share-residencial`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:MKT_SHARE_RESIDENCIAL');
      const assetUrl = new URL('/market-share-residencial/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Market_Share_Residencial_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /market-share-movel/download
    if (pathname === '/market-share-movel/download' || pathname === '/market-share-movel/download/' || pathname === '/market-share-movel/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/market-share-movel/download');
      }
      if (!checkReportAccess(user, 'market-share-movel')) {
        return Response.redirect(`${url.origin}/?denied=market-share-movel`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:MKT_SHARE_MOVEL');
      const assetUrl = new URL('/market-share-movel/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Market_Share_Movel_5G_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /panorama-market-share/download
    if (pathname === '/panorama-market-share/download' || pathname === '/panorama-market-share/download/' || pathname === '/panorama-market-share/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/panorama-market-share/download');
      }
      if (!checkReportAccess(user, 'panorama-market-share')) {
        return Response.redirect(`${url.origin}/?denied=panorama-market-share`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:PANORAMA_MARKET_SHARE');
      const assetUrl = new URL('/panorama-market-share/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Panorama_Market_Share_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /aprovacao-credito/download
    if (pathname === '/aprovacao-credito/download' || pathname === '/aprovacao-credito/download/' || pathname === '/aprovacao-credito/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/aprovacao-credito/download');
      }
      if (!checkReportAccess(user, 'aprovacao-credito')) {
        return Response.redirect(`${url.origin}/?denied=aprovacao-credito`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:APROVACAO_CREDITO');
      const assetUrl = new URL('/aprovacao-credito/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Aprovacao_Credito_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Download /evolucao-carteira/download
    if (pathname === '/evolucao-carteira/download' || pathname === '/evolucao-carteira/download/' || pathname === '/evolucao-carteira/export') {
      const user = await getSessionUser(request, env);
      if (!user || user.status !== 'aprovado') {
        return await enforceAuthRedirect(request, env, url, '/evolucao-carteira/download');
      }
      if (!checkReportAccess(user, 'evolucao-carteira')) {
        return Response.redirect(`${url.origin}/?denied=evolucao-carteira`, 302);
      }
      recordAccess(ctx, env, request, user, 'EXPORT_HTML:EVOLUCAO_CARTEIRA');
      const assetUrl = new URL('/evolucao-carteira/index.html', request.url);
      const res = await env.ASSETS.fetch(assetUrl);
      const headers = new Headers(res.headers);
      headers.set('Content-Disposition', 'attachment; filename="Evolucao_Carteira_Regional_Norte.html"');
      headers.set('Content-Type', 'text/html; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      return new Response(res.body, { status: 200, headers });
    }

    // Otimização de entrega de Service Worker e Web Manifest PWA
    if (pathname === '/sw.js') {
      const res = await env.ASSETS.fetch(request);
      const headers = new Headers(res.headers);
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      headers.set('Service-Worker-Allowed', '/');
      headers.set('Content-Type', 'application/javascript; charset=utf-8');
      return new Response(res.body, { status: res.status, headers });
    }
    if (pathname === '/manifest.webmanifest') {
      const res = await env.ASSETS.fetch(request);
      const headers = new Headers(res.headers);
      headers.set('Content-Type', 'application/manifest+json; charset=utf-8');
      headers.set('Cache-Control', 'public, max-age=3600');
      return new Response(res.body, { status: res.status, headers });
    }

    // 8. Fallback Padrão (Workers Static Assets) com Headers de Segurança e Cache Otimizado
    const res = await env.ASSETS.fetch(request);
    const headers = new Headers(res.headers);

    // Anexa cabeçalhos de segurança corporativa em todos os responses de assets
    for (const [key, val] of Object.entries(SECURITY_HEADERS)) {
      headers.set(key, val);
    }

    // Aplica estratégia de cache: estáticos imutáveis com cache longo, scripts com revalidação imediata
    if (pathname === '/sw.js') {
      headers.set('Content-Type', 'application/javascript; charset=utf-8');
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      headers.set('Pragma', 'no-cache');
      headers.set('Expires', '0');
    } else if (/\.(png|jpg|jpeg|webp|svg|ico|mp3|woff|woff2|ttf)$/i.test(pathname)) {
      headers.set('Cache-Control', 'public, max-age=604800, stale-while-revalidate=86400');
    } else if (/\.(css|js)$/i.test(pathname)) {
      headers.set('Cache-Control', 'public, max-age=0, must-revalidate');
    } else {
      // Documentos HTML e páginas de navegação NUNCA são armazenados em cache local
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
      headers.set('Pragma', 'no-cache');
      headers.set('Expires', '0');
    }

    return new Response(res.body, { status: res.status, headers });
  },
};
