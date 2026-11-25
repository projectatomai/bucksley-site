// Cloudflare Pages Function. _routes.json limits it to the paths below, so every other
// request is served straight from static assets.
//  - /analytics-consent.gif?choice=granted|denied sets the first-party consent cookie.
//  - /downloads/<file> streams installers from the R2 bucket bound as DOWNLOADS (when bound),
//    so installers over Pages' 25 MiB file limit keep their URLs on the site.
//  - LEGACY_APPCAST sends old app builds to the feed they can still verify.
// Set to { path: "/appcast.xml", userAgent: /^App\/1\.0\.[0-3] Sparkle\//, to: "/appcast-legacy.xml" } only if old builds need a legacy feed.
const LEGACY_APPCAST = null;

export async function onRequest(context) {
  const { request, env, next } = context;
  const url = new URL(request.url);
  const path = url.pathname;

  if (path === '/analytics-consent.gif') {
    const choice = url.searchParams.get('choice');
    const response = await next();
    if (choice !== 'granted' && choice !== 'denied') return response;
    const out = new Response(response.body, response);
    out.headers.append('Set-Cookie', `analytics_consent=${choice}; Path=/; Max-Age=34560000; Secure; SameSite=Lax`);
    out.headers.set('Cache-Control', 'no-store');
    return out;
  }

  if (LEGACY_APPCAST && path === LEGACY_APPCAST.path && LEGACY_APPCAST.userAgent.test(request.headers.get('user-agent') || '')) {
    return Response.redirect(new URL(LEGACY_APPCAST.to, url).toString(), 307);
  }

  if (path.startsWith('/downloads/') && env.DOWNLOADS && path.length > '/downloads/'.length) {
    const key = decodeURIComponent(path.slice('/downloads/'.length));
    if (request.method !== 'GET' && request.method !== 'HEAD') return new Response('Method not allowed', { status: 405 });
    const object = await env.DOWNLOADS.get(key, { range: request.headers, onlyIf: request.headers });
    if (object === null) return next();
    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set('etag', object.httpEtag);
    headers.set('accept-ranges', 'bytes');
    headers.set('content-disposition', 'attachment');
    headers.set('cache-control', 'public, max-age=3600');
    if (/\.dmg$/i.test(key)) headers.set('content-type', 'application/x-apple-diskimage');
    else if (/\.zip$/i.test(key)) headers.set('content-type', 'application/zip');
    headers.set('x-content-type-options', 'nosniff');
    if (!('body' in object)) return new Response(null, { status: 304, headers });
    let status = 200;
    if (object.range && request.headers.has('range')) {
      const { offset = 0, length = object.size - offset } = object.range;
      headers.set('content-range', `bytes ${offset}-${offset + length - 1}/${object.size}`);
      headers.set('content-length', String(length));
      status = 206;
    } else {
      headers.set('content-length', String(object.size));
    }
    return new Response(request.method === 'HEAD' ? null : object.body, { status, headers });
  }

  return next();
}
