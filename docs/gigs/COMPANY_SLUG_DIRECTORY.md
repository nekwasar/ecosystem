# Company Slug Directory

> A curated list of verified company slugs organized by ATS platform. Use these with the `companySlug` parameter to search jobs at specific companies.

**Last Updated:** 2026-02-23

---

## Usage

```bash
# Search Greenhouse jobs for Stripe
curl -X POST http://localhost:3001/api/jobs/search \
  -H 'Content-Type: application/json' \
  -d '{"companySlug": "stripe", "siteType": ["greenhouse"]}'

# Search all ATS platforms for Spotify (auto-detect)
curl -X POST http://localhost:3001/api/jobs/search \
  -H 'Content-Type: application/json' \
  -d '{"companySlug": "spotify"}'

# CLI usage
npm run cli -- search --company-slug stripe --site greenhouse
```

When `companySlug` is provided without `siteType`, all 28 ATS scrapers run concurrently and return results from whichever platform the company uses.

---

## Greenhouse

Greenhouse slugs are the subdomain used in `boards.greenhouse.io/{slug}`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Airbnb | `airbnb` | Travel / Tech |
| Spotify | `spotify` | Music / Tech |
| Discord | `discord` | Social / Tech |
| SpaceX | `spacex` | Aerospace |
| Cloudflare | `cloudflare` | Infrastructure |
| Twilio | `twilio` | Communications |
| Databricks | `databricks` | Data / AI |
| Datadog | `datadog` | Monitoring |
| MongoDB | `mongodb` | Database |
| Elastic | `elastic` | Search / Analytics |
| Snowflake | `snowflakeinc` | Data Cloud |
| Roblox | `roblox` | Gaming |
| Unity | `unity3d` | Gaming / 3D |
| Shopify | `shopify` | E-commerce |
| Canva | `canva` | Design |
| Pinterest | `pinterest` | Social / Tech |
| Lyft | `lyft` | Transportation |
| DoorDash | `doordash` | Delivery |
| Instacart | `instacart` | Grocery / Delivery |
| Snap | `snap` | Social / Tech |
| Rivian | `rivian` | Electric Vehicles |
| Lucid Motors | `lucidmotors` | Electric Vehicles |
| Block (Square) | `block` | Fintech |
| Notion | `notion` | Productivity |
| Stripe | `stripe` | Payments |
| Coinbase | `coinbase` | Crypto / Finance |
| HubSpot | `hubspot` | Marketing / CRM |
| Plaid | `plaid` | Fintech |

---

## Workday

Workday slugs follow the pattern `{company}:{tenant}:{careerSite}`. The format varies by deployment.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Salesforce | `salesforce:12:External` | CRM / Cloud |
| Intel | `intel:1:External` | Semiconductors |
| Cisco | `cisco:5:Cisco_External` | Networking |
| Adobe | `adobe:5:External` | Software |
| Epic Games | `epicgames:5:EpicExternalSite` | Gaming |
| Warner Bros | `warnerbros:5:WarnerBros` | Entertainment |
| Disney | `disney:5:disneycareer` | Entertainment |
| Deloitte | `deloitte:5:DeloitteUSCareers` | Consulting |
| McKinsey | `mckinsey:5:External` | Consulting |
| Tesla | `tesla:5:Tesla` | EV / Energy |
| Qualcomm | `qualcomm:5:External` | Semiconductors |
| AMD | `amd:5:External` | Semiconductors |
| Broadcom | `broadcom:5:External` | Semiconductors |
| Samsung | `samsung:3:Global` | Electronics |
| Siemens | `siemens:3:External` | Industrial |
| Lockheed Martin | `lmco:5:LMCareers` | Aerospace / Defense |

---

## Lever

Lever slugs are the subdomain at `jobs.lever.co/{slug}`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Palantir | `palantir` | Data Analytics / Defense |
| Netflix | `netflix` | Streaming |
| Atlassian | `atlassian` | Developer Tools |
| Eventbrite | `eventbrite` | Events |
| KPMG | `kpmg` | Consulting |

---

## Ashby

Ashby slugs are used in `jobs.ashbyhq.com/{slug}`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| OpenAI | `openai` | AI |
| Ramp | `ramp` | Fintech |
| Figma | `figma` | Design |
| Linear | `linear` | Developer Tools |
| Vercel | `vercel` | Developer Tools |
| Plaid | `plaid` | Fintech |
| Retool | `retool` | Developer Tools |
| Notion | `notion` | Productivity |

---

## Taleo

Taleo slugs follow the pattern `{company}:{careerSection}`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Oracle | `oracle:ORACLEEXT` | Enterprise Software |
| JPMorgan Chase | `jpmorganchase:ExternalCareerSite` | Banking |
| PepsiCo | `pepsico:ExternalSite` | Consumer Goods |

---

## iCIMS

iCIMS slugs are typically company identifiers found in the career page URL.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| EA (Electronic Arts) | `ea` | Gaming |
| Take-Two Interactive | `take2games` | Gaming |
| Goldman Sachs | `goldmansachs` | Banking |
| UPS | `ups` | Logistics |

---

## SmartRecruiters

SmartRecruiters slugs are company identifiers at `jobs.smartrecruiters.com/{slug}`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Visa | `Visa` | Payments |
| Bosch | `BoschGroup` | Industrial / Tech |
| Equinox | `Equinox` | Fitness |
| Skechers | `Skechers` | Footwear |

---

## SuccessFactors

SuccessFactors (SAP) slugs vary by company deployment.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| SAP | `sap:SAP` | Enterprise Software |
| Accenture | `accenture:Accenture` | Consulting |
| Siemens | `siemens:SiemensExternal` | Industrial |

---

## Workable

Workable slugs are the company subdomain at `apply.workable.com/{slug}`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Sephora | `sephora` | Retail / Beauty |
| Forbes | `forbes` | Media |

---

## BambooHR

BambooHR slugs are the subdomain at `{slug}.bamboohr.com/careers`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| StackOverflow | `stackoverflow` | Developer Community |
| Zapier | `zapier` | Automation |
| Buffer | `buffer` | Social Media |

---

## Recruitee

Recruitee slugs are the subdomain at `{slug}.recruitee.com`.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Toggl | `toggl` | Productivity |
| Hostinger | `hostinger` | Web Hosting |

---

## Manatal

Manatal slugs are the career page identifier. No auth required.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Manatal | `manatal` | HR Tech |

---

## Paylocity

Paylocity uses GUID identifiers found in the company's Paylocity career page URL.

| Company | Slug (GUID) | Industry |
| ------- | ----------- | -------- |
| (Discover from company career page URL pattern: `recruiting.paylocity.com/Recruiting/Jobs/Details/{guid}`) | | |

---

## Phenom

Phenom slugs are the company domain used in their Phenom-powered career site.

| Company | Slug | Industry |
| ------- | ---- | -------- |
| Boeing | `boeing` | Aerospace |
| Hilton | `hilton` | Hospitality |
| Nestle | `nestle` | Consumer Goods |
| Comcast | `comcast` | Telecom |
| Verizon | `verizon` | Telecom |

---

## Bullhorn

Bullhorn slugs follow the pattern `{cls}:{corpToken}` (found in career portal JavaScript).

| Company | Slug | Industry |
| ------- | ---- | -------- |
| (Discover from staffing agency career portal source code) | | |

---

## Tips for Finding Company Slugs

### Greenhouse
Visit `boards.greenhouse.io/{company-name}` or check the company's career page source for `greenhouse.io` links.

### Lever
Visit `jobs.lever.co/{company-name}` or check career page source for `lever.co` links.

### Workday
Look at the company's career page URL — it typically contains `{company}.wd{N}.myworkdayjobs.com`.

### Ashby
Visit `jobs.ashbyhq.com/{company-name}` or check the career page source.

### Taleo
Check the career page URL for `taleo.net` — the slug is derived from the company and career section identifiers.

### iCIMS
Check the career page URL for `icims.com` — look for the company portal identifier.

### Phenom
Check if the company's career site uses `jobs.{company}.com` — Phenom-powered sites have a consistent API pattern.

### General Strategy
1. Go to the company's career page
2. View page source (Ctrl+U)
3. Search for ATS platform domains (greenhouse.io, lever.co, ashbyhq.com, etc.)
4. Extract the slug from the URL pattern
