# UNICOM website

A dependency-free static website for UNICOM Trading & Services. It introduces the business software, presents documented hardware workflows, provides searchable manual pages with original screenshots, and includes editorial pages and search-engine/LLM discovery files.

## Preview with GitHub Pages

The `Deploy GitHub Pages preview` workflow publishes on pushes to `main` and `website-refresh`. In the repository settings, set **Pages → Build and deployment → Source** to **GitHub Actions** if it is not already selected. After a successful run, the preview URL is `https://coheretech-ca.github.io/unicom-lb.com/`.

The preview builder adds the project-path prefix, marks preview pages `noindex`, and omits the production sitemap. It does not configure a custom domain or change DNS. GitHub Pages sites are public on the internet even when their source repository is private; private-repository Pages requires an eligible GitHub plan. If this repository is not eligible, Pages must be enabled by upgrading the plan or making the repository public.

The Pages preview is for iteration, not the final custom-domain release. Before publishing on `unicom-lb.com`, configure the domain in Pages and update the workflow build command to use `--base-path / --allow-indexing`; then verify DNS and remove any previous-site routing deliberately.

## Run locally

From the repository root:

```sh
python3 -m http.server 8000
```

Open `http://localhost:8000`. The website has no JavaScript build step or runtime dependency.

## Structure

- `index.html` — landing page and interactive software walkthrough.
- `platform/` — inventory, accounting and online/AI/API capabilities.
- `products/` — hardware workflows documented for UNICOM.
- `support/` and `manual/` — support topics and searchable manual.
- `journal/` — editorial index and articles.
- `contact/` — inquiry form that opens the visitor’s email app.
- `assets/site.css` and `assets/site.js` — shared responsive design and progressive enhancements.
- `assets/manual/` — generated manual page images and selected software screenshots.
- `robots.txt`, `sitemap.xml`, and `llms.txt` — discovery and indexing resources.
- `scripts/build-pages.py` — path-aware GitHub Pages preview build.
- `.github/workflows/pages.yml` — automated preview deployment.

## Refresh manual images and searchable pages

The original `UNICOM MANUAL.pdf` is the source. When it changes, install PyMuPDF in an isolated environment and regenerate the site assets:

```sh
python3 -m venv .venv
.venv/bin/pip install pymupdf
.venv/bin/python scripts/extract-manual.py
```

The manual is dated 2019. Its text and screens are labelled as a historical edition; verify any current product workflow before publishing updates.

## Before launch

- Confirm `info@unicom-lb.com` is a monitored mailbox. The contact form uses `mailto:` and does not submit or store leads on a server.
- Confirm dashboard, AI and API wording, current promotions, hardware models and compatibility with the UNICOM team.
- Configure the chosen static host and domain. No hosting provider or DNS settings are assumed by this repository.
- Update the sitemap and canonical URLs if the production domain changes.
