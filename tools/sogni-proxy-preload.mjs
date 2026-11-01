/**
 * Preload for sogni-agent on this VM (ESM): route wss/https traffic to
 * *.sogni.ai through the egress proxy. The Sogni SDK opens its WebSocket
 * directly (wss://socket.sogni.ai) with no proxy support; this VM is
 * outbound-only via the proxy, so the handshake is patched to use
 * HttpsProxyAgent. Only sogni.ai hosts are proxied; everything else untouched.
 * The proxy URL (with credentials) is never logged.
 */
import https from 'node:https';
import { HttpsProxyAgent } from '/home/hatch/workspace/goals/win-the-sogni-world-builders-challenge/hidden_files/project/skill-cli/node_modules/https-proxy-agent/dist/index.js';

const proxyUrl = process.env.HTTPS_PROXY || process.env.https_proxy;
if (!proxyUrl) {
  console.error('[sogni-proxy] no HTTPS_PROXY set; continuing unpatched');
} else {
  const proxyAgent = new HttpsProxyAgent(proxyUrl);
  const origRequest = https.request;
  https.request = function (options, ...rest) {
    let host = '';
    if (typeof options === 'string' || options instanceof URL) {
      try { host = new URL(options.toString()).hostname; } catch { /* leave */ }
    } else if (options && typeof options === 'object') {
      host = String(options.hostname || options.host || '').split(':')[0];
    }
    if (host.endsWith('sogni.ai')) {
      const patched = { ...(options && typeof options === 'object' ? options : {}), agent: proxyAgent };
      return origRequest.call(this, patched, ...rest);
    }
    return origRequest.call(this, options, ...rest);
  };
}
