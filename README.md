# MyGirlHub

Premium wellness, mental health, and self-care publication for women — built with [Astro](https://astro.build) and Tailwind CSS.

## Stack

- Static site generation (no accounts, no database)
- Content via Astro Content Collections (`blog`, `directory`)
- Markdown-managed articles and practitioner listings

## Commands

| Command        | Action                              |
| -------------- | ----------------------------------- |
| `npm install`  | Install dependencies                |
| `npm run dev`  | Start dev server at `localhost:4321` |
| `npm run build`| Build production site to `./dist/`  |
| `npm run preview` | Preview the production build     |

## Project structure

```
src/
  content/       # Markdown collections
  components/    # Header, footer, disclaimers
  layouts/       # Base layout
  pages/         # Routes
public/          # Static assets
```
