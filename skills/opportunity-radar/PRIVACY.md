# Personal and private usage policy

**IMPORTANT:** As checked on 2026-11-10, the parent GitHub repository `Oussamaelm12/QCVT` is PUBLIC. A draft pull request is not a privacy boundary. Code, workflow logs and PR changes may be publicly visible. Do not enter personal plans, customer data, API keys or proprietary strategy into workflow inputs, source files, commit messages, issues or PR discussions.

## Intended usage
- Single owner; no multi-user accounts, SaaS resale, public dashboard, third-party sharing or monetization of the agent itself.
- Research sources may be public, but personal business decisions and annotations should remain private.
- No third-party access or account changes without owner approval.

## Controls
- The manually triggered and weekly research workflows upload report artifacts **only when the repository is private**. This prevents new reports from being published as artifacts in the currently public repository.
- The existing check/smoke workflow can still expose demonstration data and logs. Its fixed public test queries must not include private topics.
- GitHub Actions logs, input parameters, historical artifacts, PR commits and forks may remain accessible even after changing repository visibility. Audit and remove exposed information where possible; deletion does not guarantee erasure of copies.
- Before enabling personal research, make a dedicated PRIVATE repository or approve a repository visibility change. Keep this code separate from public projects. Restrict collaborators, Actions permissions and token scopes; enable 2FA and branch protections.
- Use GitHub Actions secrets for API tokens only on a private repository; never echo credentials, tokens, sensitive queries or raw authenticated responses in logs.
- Prefer local encrypted storage or private access-controlled artifacts with minimal retention. Existing workflow retention is 14–30 days; shorter retention is preferable for sensitive data.
- Private repository is not end-to-end encryption: GitHub and any connected provider still process the data. Review their policies and data-sharing terms.

## Privacy launch gate
1. Confirm private repository ownership and visibility via GitHub API.
2. Confirm only the owner/approved collaborators can access code, workflow logs and artifacts.
3. Confirm secrets are stored securely and paid-provider access is separately authorized.
4. Run a synthetic research topic; check logs and outputs for leaked identifiers.
5. Only then enable personal data and automated weekly reporting.

**No automatic privacy claim** until the private-repository checks pass.
