# job35-directory

A curated directory of **global companies and hiring channels that are friendly to job seekers aged 35+** (individual contributors and executives alike) **and still actively hiring within the last 6 months**.

**Browse online: <https://maxliu1979.github.io/job35-directory/>**

All data comes from publicly verifiable sources. Anyone can verify, correct, or extend it.
Collection and scoring are automated by the companion framework:
[job35-crawler](https://github.com/MaxLiu1979/job35-crawler).

> 中文版：[README.md](README.md)

## How to use

Browse `data/companies.yaml` by industry and look at two dimensions:

- **Activity**: whether a public hiring signal exists within the last 180 days (company careers page / Greenhouse / Lever public API / official recruiting RSS)
- **35+ friendliness**: `explicit` (explicitly welcomes senior talent) > `likely` (indirect signals such as long-experience roles) > `unknown` (no signal yet) > `risky` (explicit age caps found)

Methodology and evidence rules: [docs/methodology.md](docs/methodology.md).

## Industry coverage & roadmap

The taxonomy (`data/industries.yaml`) builds on the GICS global classification and currently covers:

Education · Health Care · Manufacturing · Energy · Financials · Internet · Information Technology · Communication Services · Materials · Consumer Discretionary · Consumer Staples · Utilities · Real Estate · Transportation & Logistics · Agriculture · Public Sector

The list grows in tiers, each tier independently useful:

1. **Tier 1 (top 10)**: 10 recognized leaders per industry to validate the pipeline
2. **Tier 2 (top 50)**: expand to top 50 with community contributions
3. **Tier 3 (top 100)**: top 100 per industry, then national/regional lists
4. **Ongoing**: monitor activity continuously; auto-demote companies with no signal for 180 days

## Data files

| file | description |
|---|---|
| `data/industries.yaml` | Industry taxonomy (bilingual) |
| `data/companies.yaml` | Company entries: sources, tier, status |
| `data/signals/` | Automated crawl results (JSON + summary) |

## Automation

[job35-crawler](https://github.com/MaxLiu1979/job35-crawler) runs weekly and opens PRs here with updated results. Evidence should be spot-checked before merging.
The `validate.yml` workflow validates data format on every push.

## Important notes

- This directory only aggregates and labels **public information**. It is not career advice or a complete description of any company's hiring policy.
- Being listed is not an endorsement; not being listed does not mean unfriendly.
- Every entry must carry public evidence. If something is wrong, open an issue with evidence and it will be corrected promptly.

## License

Data & docs: CC0-1.0 (see LICENSE). Code (scripts & workflows): MIT.
