import { v4 as uuidv4 } from 'uuid';

export interface DeviceFingerprint {
  fingerprint: string;
  userAgent: string;
  language: string;
  platform: string;
  screenResolution: string;
  timezone: string;
  cookiesEnabled: boolean;
  doNotTrack: boolean;
}

export interface FingerprintOptions {
  cookieName?: string;
  cookieExpiry?: number;
  regenerateOnChange?: boolean;
}

export class DeviceFingerprinter {
  private cookieName: string;
  private cookieExpiry: number;
  private regenerateOnChange: boolean;

  constructor(options?: FingerprintOptions) {
    this.cookieName = options?.cookieName || 'nekwasar_fp';
    this.cookieExpiry = options?.cookieExpiry || 365 * 24 * 60 * 60 * 1000;
    this.regenerateOnChange = options?.regenerateOnChange ?? true;
  }

  async generate(request: Request | null = null): Promise<DeviceFingerprint> {
    const fp: DeviceFingerprint = {
      fingerprint: uuidv4(),
      userAgent: this.getUserAgent(request),
      language: this.getLanguage(request),
      platform: this.getPlatform(request),
      screenResolution: this.getScreenResolution(),
      timezone: this.getTimezone(),
      cookiesEnabled: this.areCookiesEnabled(),
      doNotTrack: this.getDoNotTrack(request),
    };

    return fp;
  }

  private getUserAgent(request: Request | null): string {
    if (typeof window !== 'undefined' && !request) {
      return navigator.userAgent || '';
    }
    return request?.headers.get('user-agent') || '';
  }

  private getLanguage(request: Request | null): string {
    if (typeof window !== 'undefined' && !request) {
      return navigator.language || '';
    }
    return request?.headers.get('accept-language')?.split(',')[0] || '';
  }

  private getPlatform(request: Request | null): string {
    if (typeof window !== 'undefined' && !request) {
      return navigator.platform || '';
    }
    const ua = request?.headers.get('user-agent') || '';
    if (ua.includes('Win')) return 'Win32';
    if (ua.includes('Mac')) return 'MacIntel';
    if (ua.includes('Linux')) return 'Linux x86_64';
    if (ua.includes('Android')) return 'Android';
    if (ua.includes('iPhone') || ua.includes('iPad')) return 'iOS';
    return 'Unknown';
  }

  private getScreenResolution(): string {
    if (typeof window === 'undefined') return 'Unknown';
    return `${screen.width}x${screen.height}x${screen.colorDepth}`;
  }

  private getTimezone(): string {
    if (typeof window === 'undefined') return 'Unknown';
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
  }

  private areCookiesEnabled(): boolean {
    if (typeof navigator === 'undefined') return false;
    return navigator.cookieEnabled;
  }

  private getDoNotTrack(request: Request | null): boolean {
    if (typeof window !== 'undefined' && !request) {
      return navigator.doNotTrack === '1' || (navigator as any).globalPrivacyControl === true;
    }
    return request?.headers.get('dnt') === '1';
  }

  getFingerprintHash(fp: DeviceFingerprint): string {
    const str = JSON.stringify({
      ua: fp.userAgent,
      lang: fp.language,
      plat: fp.platform,
      screen: fp.screenResolution,
      tz: fp.timezone,
    });
    
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(36);
  }

  setCookie(value: string): void {
    if (typeof document === 'undefined') return;
    const expires = new Date(Date.now() + this.cookieExpiry).toUTCString();
    document.cookie = `${this.cookieName}=${value};expires=${expires};path=/;SameSite=Strict`;
  }

  getCookie(): string | null {
    if (typeof document === 'undefined') return null;
    const name = this.cookieName + '=';
    const decoded = decodeURIComponent(document.cookie);
    const ca = decoded.split(';');
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) === ' ') c = c.substring(1);
      if (c.indexOf(name) === 0) return c.substring(name.length, c.length);
    }
    return null;
  }
}

export function createFingerprinter(options?: FingerprintOptions): DeviceFingerprinter {
  return new DeviceFingerprinter(options);
}
