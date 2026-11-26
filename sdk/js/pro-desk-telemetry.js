"""Zero-dependency JS client for Pro Desk's static, read-only telemetry JSON."""
'use strict';
const DEFAULT_BASE_URL = 'https://cyptoboy777.github.io/Pro-Desk-bot/api/v1/';
class TelemetryClient {
  /** @param {{baseUrl?:string, ttlMs?:number, fetchImpl?:Function}} options */
  constructor({baseUrl = DEFAULT_BASE_URL, ttlMs = 60000, fetchImpl = globalThis.fetch} = {}) {
    if (typeof fetchImpl !== 'function') throw new Error('fetch is unavailable');
    this.baseUrl = baseUrl.replace(/\/?$/, '/'); this.ttlMs = ttlMs; this.fetchImpl = fetchImpl; this.cache = new Map();
  }
  async get(name) {
    if (!['summary','features','dataset','recent_scans','rubric'].includes(name)) throw new Error('unsupported telemetry resource');
    const now = Date.now(), c = this.cache.get(name);
    if (c && now - c.at < this.ttlMs) return c.value;
    const response = await this.fetchImpl(`${this.baseUrl}${name}.json`);
    if (!response.ok) throw new Error(`telemetry request failed: ${response.status}`);
    const value = await response.json();
    if (!value || typeof value !== 'object' || !('schema' in value)) throw new Error('invalid telemetry JSON shape');
    this.cache.set(name, {at: now, value}); return value;
  }
  summary() { return this.get('summary'); }
  features() { return this.get('features'); }
  dataset() { return this.get('dataset'); }
}
if (typeof module !== 'undefined') module.exports = {TelemetryClient, DEFAULT_BASE_URL};
