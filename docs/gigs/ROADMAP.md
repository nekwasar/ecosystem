# Roadmap

## Current (v0.5.x)

- ✅ Multi-source job searching (158+ sources)
- ✅ API key authentication
- ✅ Rate limiting
- ✅ In-memory caching
- ✅ CSV export and pagination
- ✅ Health check endpoints
- ✅ Docker deployment
- ✅ Swagger / OpenAPI docs
- ✅ CLI application
- ✅ MCP server for AI assistants (ChatGPT, Claude, Copilot)
- ✅ ATS integrations (38 platforms: Ashby, Greenhouse, Lever, Workable, SmartRecruiters, Rippling, Workday, Recruitee, Teamtailor, BambooHR, Personio, JazzHR, iCIMS, Taleo, SuccessFactors, Jobvite, ADP, UKG, BreezyHR, Comeet, Pinpoint, Manatal, Paylocity, Freshteam, Bullhorn, Trakstar, HiringThing, Loxo, Fountain, Deel, Phenom, Jobylon, Homerun, JobScore, TalentLyft, Crelate, iSmartRecruit, Recruiterflow)
- ✅ Company-specific scrapers (15: Amazon, Apple, Microsoft, Nvidia, TikTok, Uber, Cursor, Google, Meta, Netflix, Stripe, OpenAI, IBM, Boeing, Zoom)
- ✅ Remote job boards (RemoteOK, Remotive, Jobicy, Himalayas, Arbeitnow, We Work Remotely)
- ✅ API-key sources (USAJobs, Adzuna, Reed, Jooble, CareerJet)
- ✅ Client IP forwarding for proxy rotation strategies
- ✅ Tier 2 HTML scrapers (BambooHR, Personio, JazzHR, Dice, SimplyHired, Wellfound, StepStone)
- ✅ Tier 3 anti-bot sources (Taleo, iCIMS, SuccessFactors, CareerBuilder, Monster)
- ✅ BrowserPool stealth mode (UA rotation, viewport randomization, anti-fingerprinting JS injection)
- ✅ Additional job boards (BuiltIn, Snagajob, Dribbble)
- ✅ Phase 9 job board expansion (The Muse, Working Nomads, 4 Day Week, Startup.jobs, NoDesk, Web3 Career, Echojobs, Jobstreet)
- ✅ Phase 10 government boards & ATS (CareerOneStop, Arbeitsagentur, Jobylon, Homerun)
- ✅ Phase 11 niche boards & developer APIs (Hacker News, Landing.jobs, FindWork, JobDataAPI)
- ✅ Phase 12 ATS & niche board expansion (Authentic Jobs, JobScore, TalentLyft)
- ✅ Phase 13 RSS niche board expansion (CryptoJobsList, Jobspresso, HigherEdJobs, FOSS Jobs, LaraJobs, Python.org Jobs, Drupal Jobs, Real Work From Anywhere, Golang Projects, WordPress Jobs)
- ✅ Phase 14 API-key sources & ATS expansion (Talroo, InfoJobs, Crelate, iSmartRecruit, Recruiterflow)
- ✅ ATS integrations (35 platforms: +Crelate, iSmartRecruit, Recruiterflow)
- ✅ Phase 15 European government & regional boards (JobTech Dev/Sweden, France Travail, NAV Arbeidsplassen/Norway, jobs.ac.uk, Jobindex/Denmark)
- ✅ Phase 16 Global expansion (Get on Board/LatAm, Freelancer.com, JoinRise, Canada Job Bank)
- ✅ Phase 17 Niche & international expansion (ReliefWeb/NGO, UNDP Jobs/UN, DevITjobs/IT)
- ✅ Phase 18 Niche RSS expansion (PyJobs, VueJobs, Conservation Job Board, Coroflot, Berlin Startup Jobs)
- ✅ Phase 19 Tech niche, crypto & regional expansion (Rails Job Board, Elixir Jobs, Crunchboard, Cryptocurrency Jobs, HasJob)
- ✅ Phase 20 European regional & niche expansion (iCrunchData, SwissDevJobs, GermanTechJobs, VirtualVocations, NoFluffJobs)
- ✅ Phase 21 Niche & academic expansion (Green Jobs Board, EuroJobs, Open Source Design Jobs, Academic Careers, RemoteFirstJobs)
- ✅ Phase 22 Eastern European, CIS & Singapore expansion (Djinni, HeadHunter, Habr Career, MyCareersFuture)
- ✅ Phase 23 Japan, Nordic & Swiss expansion (Duunitori, Jobs in Japan, Jobs.ch)
- ✅ Phase 24 UK & mobile dev expansion (Guardian Jobs, AndroidJobs, iOS Dev Jobs)
- ✅ Phase 25 DevOps, FP, diversity & niche expansion (DevOpsJobs, Functional Works, PowerToFly, Clojure Jobs)
- ✅ Phase 26 Environmental & conservation expansion (EcoJobs)

## Planned### v0.6.0: Resiliency & API Expansion (current)

- [x] Redis-backed optional caching (GET/SET async)
- [x] GraphQL API implementation (searchJobs, listSources)
- [x] Prometheus metrics (HTTP tracking, scraper performance)
- [x] Configurable retry policies (linear/exponential backoff)
- [x] Plugin Architecture (Runtime scraper loading)
- [x] Expanded sources (JobsDB, Techcareers)

## Future Considerations (v0.7.0+)

- Additional ATS/company integrations (Phase 10+)
- WebSocket / SSE support for real-time search progress
- Job deduplication across sources
- OAuth2 authentication
- Frontend dashboard for job search results
- Job alerts / notifications (email, webhook)
- Enterprise features (multi-tenant, audit logs)
