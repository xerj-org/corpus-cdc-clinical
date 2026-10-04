# corpus-cdc-clinical

CDC clinical guidance for healthcare providers, mirrored as plain markdown
for retrieval evaluation. Unofficial mirror — not affiliated with CDC. The
authoritative source is always cdc.gov.

## Scope — exactly what was fetched (2026-10-04, UTC)

Three groups, all HTML provider-facing pages, chrome stripped to main
content (headings, paragraphs, list items, table cells preserved as text):

1. **`sti-tx/` (56 pages)** — the STI Treatment Guidelines, 2021, per-condition
   provider pages, walked from the CDC table of contents
   (`/std/treatment-guidelines/toc.htm`): chlamydia, gonorrhea (adults /
   children / neonates / DIS), syphilis (primary+secondary / latent /
   late / congenital), HIV, HPV, hepatitis, PID, epididymitis, vaginitis
   (BV, candidiasis, trichomonas), genital ulcers, warts, ectoparasitic,
   plus the clinical-prevention chapters (screening, partner services,
   expedited partner therapy, reporting, retesting).
2. **`acip-vaccines/` (27 pages)** — ACIP current vaccine-specific
   recommendations, walked from `/acip-recs/hcp/vaccine-specific/`
   (anthrax through yellow-fever, incl. COVID-19, flu, hepatitis A/B,
   MMR, pneumococcal, RSV, Td/Tdap).
3. **`measles/` (1 page)** — the measles clinical overview for providers.

Pages that returned CDC's 404 stub, and multi-page section shells with no
body (children/specialpops/gonorrhea landing pages whose content lives in
the per-population pages), were dropped. `MANIFEST.json` lists
`path → source URL` for every kept page. 84 files total.

## Licence

CDC content is produced by the United States federal government
(42 U.S.C. § 2102 et seq. establishes the agency; its works are US
government works). Per CDC's own reuse guidance, CDC web content is in the
public domain (17 U.S.C. § 105) unless otherwise stated; the mirrored pages
carry no copyright notice and no third-party-content flag. No attribution
is legally required; the source URLs are kept in every file for provenance.
Any page later found to carry a reuse restriction will be dropped from the
mirror rather than relicensed.

## Fetching

`tools/fetch_cdc.py` (rate-capped: one page per ≥2 s, fetched once).
CDC's WAF 403s python-urllib and generic Mozilla UAs; plain curl passes —
the fetcher shells out to curl.
