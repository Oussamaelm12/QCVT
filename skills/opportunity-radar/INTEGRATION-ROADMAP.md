# Opportunity Radar — intelligence and integration architecture

## Scope
The goal is a repeatable **decision system** across consumer software, creator tools, e-commerce, digital services, small-business self-serve tools, operations, AI workflows, education, finance, health, career, marketing, sales, privacy and other markets. It must distinguish a profitable hypothesis from observed evidence. There is no credible guarantee of detecting **all** opportunities or becoming the best agent globally.

## Currently implemented and runnable
- Apple iTunes Search API: app metadata and competition, free public search
- Apple public review feeds: sampled reviews, not representative
- Hacker News Algolia: technical community discussion, not demand proof
- Reddit OAuth connector: implemented, **requires** compliant access token and user-agent, not authenticated live-tested
- Google Trends through SerpApi: implemented, **requires** API key and explicit approval for any credit consumption; not authenticated live-tested
- Market radar: 16 sector families × 3 seed queries, balanced cross-sector scan, bounded 1–48 queries, JSON provenance and partial-failure reporting
- Production command and GitHub workflow; weekly GitHub Actions workflow (runs on default branch after merge); ChatGPT weekly report is a separate automation

## Providers to evaluate and integrate only with authorization
| Provider / capability | Access | Value | Current status |
|---|---|---|---|
| Google Search Console | Account OAuth | Actual site impressions/queries | Not integrated |
| Google Analytics 4 | Account OAuth | Conversion funnels | Not integrated |
| Google Ads Keyword Planner | Account and eligibility | Keyword demand/competition estimates | Not integrated |
| Google Trends | SerpApi credits or approved alternative | Relative trends | Connector built, credential-gated |
| Reddit | OAuth and API terms | Problem conversations | Connector built, credential-gated |
| YouTube Data API | Quota and key | Creator/format demand | Not integrated |
| vidIQ | Connected account | Creator competitor analytics | Not integrated |
| Product Hunt | API/permission review | New product launches | Not integrated |
| GitHub API | Token/quota | Open-source adoption and emerging dev tools | GitHub development only; market adapter not integrated |
| G2/Capterra | Licensed access/terms | B2B software complaints and alternatives | Not integrated |
| Similarweb | Subscription/API | Traffic estimates | Not integrated |
| Semrush/Ahrefs | Subscription/API | Keyword and competitor research | Not integrated |
| Sensor Tower/Appfigures | Subscription/API | App market estimates | Not integrated |
| Meta Ads Library | Official access/terms | Ad creative patterns, not profitability | Not integrated |
| TikTok Creative Center | Terms/access review | Creative and commerce trends | Not integrated |
| Shopify | Connected merchant OAuth | Store sales, product performance | Not integrated |
| Etsy | Approved API | Marketplace product trends | Not integrated |
| Stripe | Authorized account | Actual payments and retention | Not integrated |
| Exploding Topics/Trends tools | Subscription/API | Early demand hypotheses | Not integrated |
| Public datasets (Eurostat, INSEE, World Bank) | Free APIs | Macro/regulatory context | Not integrated |
| Google Patents/arXiv | Public/licensed access | Emerging tech and applications | Not integrated |

## Decision architecture to build next
1. Provider-specific adapters with schema validation, caching, quotas, privacy and provenance.
2. Cross-source evidence graph keyed by claim, domain, observation date, geography, independence and quality.
3. Novelty/change detector across weekly snapshots, including emerging strategies and distribution channels.
4. Segmented opportunity ranking: micro-SaaS, mobile, digital products, content, marketplaces, affiliate, services and self-serve B2B; evaluate effort, cash requirements, skill fit, legal constraints and sales cycle.
5. Deep strategic playbooks: JTBD, category design, distribution wedges, pricing, retention, platform arbitrage, defensibility, second-order effects and scenario planning.
6. Backtesting on historical markets, blind human review and metrics (precision@k, evidence accuracy, calibration, cost per useful lead).
7. Decision log and weekly actions with actual experiment results, not fabricated forecasts.

## Cost and safety policy
No third-party subscriptions, purchases, paid API calls, credential storage, sending messages, publishing, or merging/deploying without explicit user approval. Do not silently activate expensive sources. Set monthly cost cap per provider before activation. Free public sources have rate limits and can change terms. Reports must distinguish observed, estimated and hypothetical numbers.
