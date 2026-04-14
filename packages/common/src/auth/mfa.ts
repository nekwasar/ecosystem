import * as bcrypt from 'bcrypt';

export interface MFAConfig {
  issuer?: string;
  algorithm?: string;
}

export class MFA {
  private issuer: string;

  constructor(config?: MFAConfig) {
    this.issuer = config?.issuer || 'Nekwasar';
  }

  generateSecret(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let secret = '';
    for (let i = 0; i < 32; i++) {
      secret += chars[Math.floor(Math.random() * chars.length)];
    }
    return secret;
  }

  generateTOTP(secret: string): string {
    const counter = Math.floor(Date.now() / 30000);
    return this.hotp(secret, counter);
  }

  verifyTOTP(secret: string, token: string, window = 1): boolean {
    const counter = Math.floor(Date.now() / 30000);
    
    for (let i = -window; i <= window; i++) {
      if (this.hotp(secret, counter + i) === token) {
        return true;
      }
    }
    return false;
  }

  private hotp(secret: string, counter: number): string {
    const base32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
    let bits = '';
    
    for (const char of secret.toUpperCase()) {
      const val = base32.indexOf(char);
      if (val === -1) continue;
      bits += val.toString(2).padStart(5, '0');
    }
    
    const hexCounter = counter.toString(16).padStart(16, '0');
    let hmac = '';
    
    for (let i = 0; i < hexCounter.length; i += 2) {
      hmac += String.fromCharCode(parseInt(hexCounter.substr(i, 2), 16));
    }
    
    const offset = (hmac.charCodeAt(hmac.length - 1) & 0x0f);
    const code = 
      ((hmac.charCodeAt(offset) & 0x7f) << 24) |
      ((hmac.charCodeAt(offset + 1) & 0xff) << 16) |
      ((hmac.charCodeAt(offset + 2) & 0xff) << 8) |
      (hmac.charCodeAt(offset + 3) & 0xff);
    
    const otp = code % 1000000;
    return otp.toString().padStart(6, '0');
  }

  getQRCodeURL(email: string, secret: string): string {
    const label = encodeURIComponent(email);
    const issuer = encodeURIComponent(this.issuer);
    return `otpauth://totp/${label}?secret=${secret}&issuer=${issuer}&algorithm=SHA1&digits=6&period=30`;
  }
}

export class PasswordHasher {
  private rounds: number;

  constructor(rounds = 12) {
    this.rounds = rounds;
  }

  async hash(password: string): Promise<string> {
    return bcrypt.hash(password, this.rounds);
  }

  async verify(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
}

export function createMFA(config?: MFAConfig): MFA {
  return new MFA(config);
}

export function createPasswordHasher(rounds?: number): PasswordHasher {
  return new PasswordHasher(rounds);
}
