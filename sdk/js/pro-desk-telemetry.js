/**
 * Pro Desk telemetry client: zero-dependency, read-only reader for the published static JSON API.
 * Works in Node 18+ and browsers. It only issues GET requests to the telemetry base URL. No wallet code.
 */
'use strict';
const DEFAULT_BASE_URL = 'https://cyptoboy777.github.io/Pro-Desk-bot/api/v1/';
const isObj = v => v !== null && typeof v === 'object' && !Array.isArray(v);

/** Per-resource shape checks. Each returns an error string, or null when the payload is valid. */
const VALIDATORS = {
  summary: v => !isObj(v.pass_vs_reject_24h) ? 'missing pass_vs_reject_24h' : typeof v.edge_status !== 'string' ? 'missing edge_status' : null,
  features: v => !Array.isArray(v.features) ? 'features must be an array' : null,
  recent_scans: v => !Array.isArray(v.scans) ? 'scans must be an array' : null,
  rubric: v => !isObj(v.config) ? 'missing config' : null,
  dataset: v => !Array.isArray(v.rows) ? 'rows must be an array' : null,
  actions: v => !Array.isArray(v.rules) ? 'rules must be an array' : null,
};
const NEEDS_SCHEMA = new Set(['summary', 'features', 'recent_scans', 'rubric', 'dataset']);
const RESOURCES = Object.keys(VALIDATORS);

class TelemetryClient {
  /** @param {{baseUrl?:string, ttlMs?:number, fetchImpl?:Function}} options */
  constructor({baseUrl = DEFAULT_BASE_URL, ttlMs = 60000, fetchImpl = globalThis.fetch} = {}) {
    if (typeof fetchImpl !== 'function') throw new Error('fetch is unavailable');
    this.baseUrl = baseUrl.replace(/\/?$/, '/'); this.ttlMs = ttlMs; this.fetchImpl = fetchImpl; this.cache = new Map();
  }
  /** Validate a payload for a resource; throws on a bad shape. */
  static validate(name, value) {
    if (!VALIDATORS[name]) throw new Error('unsupported telemetry resource');
    if (!isObj(value)) throw new Error('invalid telemetry JSON shape');
    if (NEEDS_SCHEMA.has(name) && !('schema' in value)) throw new Error('invalid telemetry JSON shape: missing schema');
    const err = VALIDATORS[name](value);
    if (err) throw new Error('invalid telemetry JSON shape: ' + err);
    return value;
  }
  async get(name) {
    if (!VALIDATORS[name]) throw new Error('unsupported telemetry resource');
    const now = Date.now(), c = this.cache.get(name);
    if (c && now - c.at < this.ttlMs) return c.value;
    const pending = (async () => {
      const response = await this.fetchImpl(`${this.baseUrl}${name}.json`);
      if (!response.ok) throw new Error(`telemetry request failed: ${response.status}`);
      return TelemetryClient.validate(name, await response.json());
    })();
    this.cache.set(name, {at: now, value: pending});          // concurrent callers share one request
    try { const value = await pending; this.cache.set(name, {at: now, value}); return value; }
    catch (e) { this.cache.delete(name); throw e; }
  }
  clearCache() { this.cache.clear(); }
  getSummary() { return this.get('summary'); }
  getFeatures() { return this.get('features'); }
  getRecentScans() { return this.get('recent_scans'); }
  getRubric() { return this.get('rubric'); }
  getDataset() { return this.get('dataset'); }
  getActions() { return this.get('actions'); }
  summary() { return this.getSummary(); }
  features() { return this.getFeatures(); }
  dataset() { return this.getDataset(); }
}
if (typeof module !== 'undefined') module.exports = {TelemetryClient, DEFAULT_BASE_URL, RESOURCES};
