# Portfolio site

A single self-contained page (`index.html`) presenting DevOps/SRE consulting work, built from
evidence in the public repositories on this account.

## Design constraints

- **No external requests.** Fonts are subsetted to the glyphs the page uses, converted to WOFF2 and
  inlined as data URIs. No CDN, no analytics, no tracking. The page renders identically offline.
- **~193 KB total**, fonts included — one request, nothing to block on.
- **Theme-aware.** Respects `prefers-color-scheme` and an explicit `data-theme` attribute, with the
  full palette defined as tokens so both themes resolve as a complete set.
- **Accessible.** Skip link, semantic landmarks, visible focus states, `prefers-reduced-motion`
  honoured, no horizontal scroll from 390 px upward.

## Content policy

Every claim on the page maps to a file or commit in a public repository — the "Proof" section is
that index. The page deliberately contains **no invented metrics**: no traffic figures, uptime
percentages, user counts or business impact, because none of these projects have production usage
that would make such numbers honest. Known limitations (reconcile-based rather than admission-based
enforcement; the wildcard CI Role in the EKS repo) are stated on the page rather than omitted.

## Before publishing

Two things need your confirmation — search `TODO(imad)` in `index.html`:

- **Certifications.** Add verification links (Credly / Red Hat) to each credential and correct any
  status that is out of date.
- **Contact links.** The email and LinkedIn URL are taken from your profile README; add an Upwork
  profile link if you want that as a conversion path.

## Deploying

The page is a static file with no build step. To serve it from this host's existing Nginx role,
copy it to the web root the reverse proxy already serves:

```yaml
- name: Deploy portfolio page
  ansible.builtin.copy:
    src: ../../portfolio/index.html
    dest: /var/www/html/index.html
    owner: root
    group: root
    mode: '0644'
```

`nginx-reverse-proxy/files/reverse-proxy.conf` already serves `/var/www/html` for the apex domain
over TLS, so no server-block changes are needed.

## Layout

```
portfolio/
├── index.html      generated, self-contained — this is what you deploy
├── src/page.html   source: markup + CSS, with a __FONTS__ placeholder
└── build.py        subsets the fonts to WOFF2 and inlines them
```

## Rebuilding

`index.html` is generated. For copy changes, edit `src/page.html` and rebuild:

```bash
pip install fonttools brotli
python3 build.py --fonts /path/to/ttf-directory
```

The six faces are open-source under the SIL Open Font License — Bricolage Grotesque
(display), Instrument Sans (body) and Geist Mono (labels, data and code). Download the TTFs
from Google Fonts or each project's repository into a directory and point `--fonts` at it.

Editing `index.html` directly also works for small wording fixes; just mirror the change into
`src/page.html` so the next rebuild doesn't revert it.
