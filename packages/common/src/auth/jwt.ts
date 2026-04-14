import * as jose from 'jose';

export interface JWTPayload {
  sub: string;
  email?: string;
  role?: string;
  service?: string;
  iat?: number;
  exp?: number;
}

export interface JWTConfig {
  secret: string;
  issuer?: string;
  audience?: string;
  expiresIn?: string;
}

export class JWT {
  private secret: Uint8Array;
  private issuer: string;
  private audience: string[];
  private expiresIn: string;

  constructor(config: JWTConfig) {
    this.secret = new TextEncoder().encode(config.secret);
    this.issuer = config.issuer || 'nekwasar-ecosystem';
    this.audience = config.audience || ['nekwasar'];
    this.expiresIn = config.expiresIn || '24h';
  }

  async sign(payload: Omit<JWTPayload, 'iat' | 'exp'>): Promise<string> {
    const jwt = await new jose.SignJWT({ ...payload })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuer(this.issuer)
      .setAudience(this.audience)
      .setIssuedAt()
      .setExpirationTime(this.expiresIn)
      .sign(this.secret);

    return jwt;
  }

  async verify(token: string): Promise<JWTPayload | null> {
    try {
      const { payload } = await jose.jwtVerify(token, this.secret, {
        issuer: this.issuer,
        audience: this.audience,
      });

      return payload as JWTPayload;
    } catch {
      return null;
    }
  }

  async refresh(token: string, newExpiresIn?: string): Promise<string | null> {
    const payload = await this.verify(token);
    if (!payload) return null;

    const { iat, exp, ...rest } = payload;
    return this.sign({ ...rest } as Omit<JWTPayload, 'iat' | 'exp'>);
  }
}

export function createJWT(config: JWTConfig): JWT {
  return new JWT(config);
}
