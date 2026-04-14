import { z } from 'zod';

const databaseEnv = z.object({
  DATABASE_URL: z.string().url(),
  POSTGRES_HOST: z.string().default('localhost'),
  POSTGRES_PORT: z.coerce.number().default(5432),
  POSTGRES_USER: z.string(),
  POSTGRES_PASSWORD: z.string(),
  POSTGRES_DB: z.string(),
});

const redisEnv = z.object({
  REDIS_URL: z.string().url().default('redis://localhost:6379'),
});

const appEnv = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(8000),
  SECRET_KEY: z.string().min(32),
  API_PREFIX: z.string().default('/api'),
  CORS_ORIGIN: z.string().default('*'),
});

const externalServicesEnv = z.object({
  BREVO_API_KEY: z.string().optional(),
  SENDER_EMAIL: z.string().email().optional(),
  GROQ_API_KEY: z.string().optional(),
  OPENROUTER_API_KEY: z.string().optional(),
  CEREBRAS_API_KEY: z.string().optional(),
  TELEGRAM_BOT_TOKEN: z.string().optional(),
});

const serviceUrlsEnv = z.object({
  ADMIN_URL: z.string().url().optional(),
  AGENT_URL: z.string().url().optional(),
  BLOG_URL: z.string().url().optional(),
  GIGS_URL: z.string().url().optional(),
  MAIL_URL: z.string().url().optional(),
  PORTFOLIO_URL: z.string().url().optional(),
  STORE_URL: z.string().url().optional(),
});

export const envSchema = databaseEnv
  .merge(redisEnv)
  .merge(appEnv)
  .merge(externalServicesEnv)
  .merge(serviceUrlsEnv);

export type EnvConfig = z.infer<typeof envSchema>;

class Config {
  private config: EnvConfig | null = null;

  load(): EnvConfig {
    if (this.config) return this.config;

    const result = envSchema.safeParse(process.env);

    if (!result.success) {
      const errors = result.error.issues.map(i => `${i.path.join('.')}: ${i.message}`);
      throw new Error(`Environment validation failed:\n${errors.join('\n')}`);
    }

    this.config = result.data;
    return this.config;
  }

  get<K extends keyof EnvConfig>(key: K): EnvConfig[K] {
    if (!this.config) this.load();
    return this.config![key];
  }

  getAll(): EnvConfig {
    if (!this.config) this.load();
    return this.config!;
  }

  isProduction(): boolean {
    return this.get('NODE_ENV') === 'production';
  }

  isDevelopment(): boolean {
    return this.get('NODE_ENV') === 'development';
  }
}

export const config = new Config();

export function loadEnv(): EnvConfig {
  return config.load();
}
