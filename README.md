# Free Financial Reports API

[![Free tier](https://img.shields.io/badge/free-no%20credit%20card-brightgreen)](https://datasink.ing)
[![Exchanges](https://img.shields.io/badge/exchanges-9-blue)](https://datasink.ing)

**A free REST API for full-text financial reports — annual, semi-annual and quarterly —
from China, Korea, Japan and Taiwan, served as clean Markdown.**

This is the free tier of [DataSinking](https://datasink.ing). It is **not** a real-time quote feed
and **not** a numeric fundamentals screener. What it serves is **the report text itself**: the
actual filing, parsed into Markdown with headings, tables and paragraphs preserved, and
**queryable by section** — so an LLM can pull the MD&A chapter of a 300-page annual report
instead of ingesting the whole thing.

No credit card, no trial clock, no seat limit. One key, all 9 exchanges.

---

## What you get, free

| | |
|---|---|
| **Markets** | China · Japan · Korea · Taiwan — **all 9 exchanges** (see [coverage](#coverage)) |
| **Documents** | annual · semi-annual · q1 · q3 · amendment |
| **Format** | Full-text **Markdown**, YAML frontmatter, tables preserved |
| **Rate** | 3 API calls / second |
| **Quota** | **8,191 documents** per rolling 7 days, per key (batch up to 3 per call) |
| **Plus** | a shared pool of **524,287 documents / 7 days** across all free users and site visitors |
| **Interfaces** | REST API · MCP server · Python package (`pip install datasinking`) |
| **Price** | **$0** |

**Quotas count documents, not requests.** Listing metadata for 200 reports costs 200 documents,
and a section fetch costs one — the same as a full-report fetch. That is deliberate: you can
afford to be picky, and you cannot afford to download an entire exchange by accident.

Numbers above are the live free-tier limits and are the ones to trust over any blog post,
including this one. If they ever change, they change on [datasink.ing/pricing](https://datasink.ing/pricing).

## What the free tier is not

Being specific here saves you a support ticket:

- **No real-time or historical quotes, no klines, no order books.** Reports are filings, published
  on a disclosure calendar — not a market data feed.
- **No US, no Hong Kong, no European listings.** The 9 exchanges below are the whole list.
- **No numeric/fundamentals extraction endpoint.** You get the report text; pulling a revenue
  figure out of it is the LLM's job, and that is the point.
- **No reselling the API on a standalone basis.** Build a product, a research pipeline or a
  chatbot on top of the data — that is what it is for. What the [Terms](https://datasink.ing/terms)
  rule out is redistributing or reselling the Service or its content *as a data service of your
  own*. Keep the `source` field that travels with every document.

## Get a key — about 30 seconds

```bash
curl -X POST https://api.datasink.ing/free-key \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
```

The key arrives by email. Or use the form at [datasink.ing](https://datasink.ing).

Then every call is one query parameter — no headers, no signing, no OAuth dance:

```bash
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"
```

## Three things to do with a free key

The examples below use a real key. Shell only — nothing to install.

### 1. See the coverage

```bash
curl "https://api.datasink.ing/exchanges?apikey=YOUR_KEY"
curl "https://api.datasink.ing/stocks?exchange=jpx&apikey=YOUR_KEY"   # every Tokyo-listed company
```

### 2. List a company's reports, then pull one

```bash
# Moutai (China) — metadata only
curl "https://api.datasink.ing/documents?symbol=600519.SS&doc_type=annual&apikey=YOUR_KEY"

# Toyota (Japan) — the latest 3, full text
curl "https://api.datasink.ing/documents?symbol=7203.T&order=desc&size=3&with_content=1&apikey=YOUR_KEY"
```

Symbols are FMP-style: `600519.SS` · `005930.KS` · `7203.T` · `2330.TW`.

### 3. Pull just one section (the RAG move)

A full annual report is often 200k+ characters. This is how you don't pay for that:

```bash
# what chapters does document 42 have?
curl "https://api.datasink.ing/documents/42/sections?apikey=YOUR_KEY"

# give me only the MD&A
curl "https://api.datasink.ing/documents/42?section=MD&A&apikey=YOUR_KEY"
```

Section keywords match against the report's **own** headings, in the report's own language —
so for a Chinese filing you pass `管理层讨论与分析` or `财务报告`, and for a Japanese one
`経営成績` . See [`examples/free_quickstart.py`](examples/free_quickstart.py) for a
runnable, stdlib-only script that walks a company's last two annual reports and prints the
MD&A section of each.

## Use it from an AI agent (MCP)

The same free key works on the [MCP](https://modelcontextprotocol.io) server. Hosted endpoint —
no package, no local process:

```bash
claude mcp add --transport http datasinking https://api.datasink.ing/mcp \
  --header "Authorization: Bearer YOUR_KEY"
```

Six tools: list exchanges, list stocks, list reports, fetch a report, list sections, fetch one
section. Local builds exist too (`npx -y datasinking-mcp`, or `pip install "datasinking[mcp]"`)
with setup guides for Claude Code, Claude Desktop, Cursor, Codex, OpenCode, Windsurf, Qoder,
Doubao Work and more in the
[main repo's `docs/mcp/`](https://github.com/heubme2020/datasinking/tree/main/docs/mcp).

## Coverage

**13,000+ companies · 600,000+ reports**, and growing daily as filings are published.

| Market | Exchange | Suffix | Source |
|---|---|---|---|
| China | Shanghai Stock Exchange | `.SS` | cninfo (巨潮资讯网) |
| China | Shenzhen Stock Exchange | `.SZ` | cninfo |
| China | Beijing Stock Exchange | `.BJ` | cninfo |
| Japan | Tokyo Stock Exchange | `.T` | EDINET |
| Korea | Korea Exchange — KOSPI | `.KS` | DART |
| Korea | Korea Exchange — KOSDAQ | `.KQ` | DART |
| Korea | Korea Exchange — KONEX | `.KN` | DART |
| Taiwan | Taiwan Stock Exchange | `.TW` | MOPS |
| Taiwan | Taipei Exchange | `.TWO` | MOPS |

Every report is sourced from the official regulatory disclosure platform for that market and
converted in-house to Markdown. Korea and Japan update from the official DART/EDINET APIs, so
new filings land within about 24h of publication.

## When you outgrow free

The free tier is a real tier, not a demo — but a whole-exchange download is not what it is for.
The paid key is **31 requests/second and 524,287 documents per rolling 7 days** for
**$31/year** — an order of magnitude cheaper than the market-data APIs it is often compared to,
because report text is not a low-latency feed.

Pricing and the current limits: [datasink.ing/pricing](https://datasink.ing/pricing)

## 中文

**[DataSinking](https://datasink.ing/zh) 提供中国、日本、韩国、台湾四地上市公司
**财报全文**的免费 API** —— 年报、半年报、季报，解析成带标题层级和表格的 Markdown，
可以直接喂给大模型做 RAG。按**章节**取用（比如只取「管理层讨论与分析」），
不必把 300 页的报告整篇塞进上下文。

免费档：9 个交易所全覆盖，3 次/秒，每把 key 每 7 天 8,191 篇，**不需要信用卡**。
取 key 和接入方式见上，中文说明见 [datasink.ing/zh](https://datasink.ing/zh)。

> 注：不提供实时行情/K 线，也不包含美股和港股 —— 我们只做这 9 个交易所的**定期报告全文**。

## Links

- **Website / get a key** — [datasink.ing](https://datasink.ing)
- **Main repo** (MCP server, Python package, npm package, examples, research) —
  [github.com/heubme2020/datasinking](https://github.com/heubme2020/datasinking)
- **Per-client MCP setup guides** — [`docs/mcp/`](https://github.com/heubme2020/datasinking/tree/main/docs/mcp)
- **API examples, 7 in curl + Python + LLM** —
  [`api-examples.md`](https://github.com/heubme2020/datasinking/blob/main/api-examples.md)
- **Support** — support@datasink.ing
- **Affiliate** — earn $7 every purchase per referral (recurring, PayPal, $31 minimum withdrawal): [datasink.ing/affiliate](https://datasink.ing/affiliate)

## License

MIT — see [LICENSE](LICENSE). The license covers this repo's code and text, not the API or
the report data served by it.

---

*DataSinking is an independent project and is not affiliated with cninfo, EDINET, DART or MOPS.
The underlying financial reports are public disclosures of the respective companies and remain
subject to their original terms. The service's processing, formatting and software are ours.*
