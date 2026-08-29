# AMM — Automated Medical Module

School project website: concept of an Automated Medical Module for emergency care of socially vulnerable patients.

**Author:** Vera Kochergina, Moscow 2026

## Live site

Static site ready for [GitHub Pages](https://pages.github.com/).

### Deploy to GitHub Pages

1. Push this repository to GitHub
2. Go to **Settings → Pages**
3. Source: **Deploy from a branch**
4. Branch: `main`, folder: `/ (root)`
5. Save — site will be at `https://<username>.github.io/<repo>/`

### Custom domain

1. Add a `CNAME` file in the repo root with your domain (e.g. `amm.example.com`)
2. Configure DNS at your registrar (A/CNAME records per GitHub docs)
3. Enable HTTPS in GitHub Pages settings

## Languages

| Language | URL | Visible in nav |
|----------|-----|----------------|
| English (default) | `/index.html` | Yes |
| French | `/fr/index.html` | Yes |
| Russian | `/ru/index.html` | Hidden |

Russian is not shown in the language switcher by default. To show it temporarily:

- Add `?v=1` to any page URL (e.g. `index.html?v=1`)
- RU appears in the nav while the parameter is present
- Remove `?v=1` or open the site without it — RU disappears again
- Or go directly to `/ru/index.html` (Russian pages always work)

## Structure

```
├── index.html, about.html     — English (default)
├── fr/                        — French
├── ru/                        — Russian (hidden)
├── assets/
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
└── docs/                      — Full specifications (~20 pages each)
    ├── AMM_Full_Specification_EN.docx
    ├── AMM_Full_Specification_FR.docx
    ├── AMM_Full_Specification_RU.docx
    └── AMM_Full_Specification_RU.pdf
```

Download via **Full specification** button in the site header (language matches current page).

## Local preview

Open `index.html` in a browser, or use a simple server:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080`

## License

School project.
