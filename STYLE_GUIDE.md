# Website Style Guide

This style guide is based on the current visual system used in [index.html](./index.html) and [styles.css](./styles.css). The site presents a polished, modern personal brand for an engineering student and designer/technologist with a strong academic and sustainability focus.

## 1. Brand direction

The visual identity balances:

- Clean, confident technology branding
- Warm personal storytelling
- Modern engineering credibility
- A calming, sustainability-inspired palette

The overall effect is high-contrast, minimal, and forward-looking without feeling sterile.

## 2. Typography

### Font pairing

- Primary body font: Hind, sans-serif
- Heading font: Montserrat, sans-serif

The site loads the fonts from Google Fonts:

```html
<link href="https://fonts.googleapis.com/css2?family=Hind&family=Montserrat&display=swap" rel="stylesheet">
```

### Type hierarchy

| Use case | Font | Weight | Example |
| --- | --- | --- | --- |
| Body text | Hind | 400 / 500 | Paragraphs, nav items, cards |
| Section headings | Montserrat | 700-900 | "about me", "what I've been up to" |
| Hero heading | Montserrat | 900 | Large gradient display text |
| Buttons / labels | Hind / Montserrat | 500-700 | CTAs and category labels |

### Recommended scales

- Hero headline: 100px
- H1: 2.5rem
- Navbar brand: 2rem
- Body text: 1rem
- Small supporting text: 0.9rem to 1rem

### Type rules

- Use strong contrast between headings and body text
- Keep body copy clean and readable with generous line spacing
- Let typography feel technical but still approachable
- Use the gradient hero treatment sparingly to maintain dramatic emphasis

## 3. Color palette

### Core palette

| Color | Hex | RGB | Usage |
| --- | --- | --- | --- |
| Obsidian black | `#1D1D1D` | `29, 29, 29` | Backgrounds, dark sections, nav |
| Soft white | `#F9F9F9` | `249, 249, 249` | Text on dark backgrounds, light contrast panels |
| Sage green | `#8CADA7` | `140, 173, 167` | Accent color, highlights, hover states |
| Pale mint | `#A5D0A8` | `165, 208, 168` | Gradient balance and soft highlight tone |

### Palette guidance

- Use black as the dominant background to create a clean, premium base
- Use white for high readability and contrast
- Use sage green as the primary accent for emphasis, hover behavior, and key UI moments
- Use the mint gradient in hero text and limited highlight areas to add personality without clutter

### Example gradient

```css
background: linear-gradient(200deg, #f9f9f9, #8cada7, #a5d0a8);
```

## 4. Layout principles

### Structure

The site uses a simple, modular structure:

- Fixed/sticky top navigation
- Large fullscreen hero section
- Centered content containers with max-width constraints
- Strong section spacing and visual separation
- Clear vertical rhythm between blocks

### Layout values

- Max section width: approximately 1300px
- Navbar height: 80px
- Hero padding: ~200px vertical
- Section container padding: 0 50px
- Border radius on buttons: 4px

### Alignment

- Keep layouts centered and highly balanced
- Maintain a strong left-to-right reading rhythm
- Use whitespace generously around blocks and cards
- Prioritize clarity over decorative density

## 5. UI components

### Navigation

- Dark background with white text
- Small uppercase/lowercase mix for a modern personal-site feel
- Accent hover state in sage green
- CTA button uses the mint accent and black text for contrast

```css
.navbar {
  background: RGB(29, 29, 29);
}

.navbar__links:hover {
  color: #8CADA7;
}
```

### Buttons

Buttons follow a simple, high-contrast treatment:

- Solid sage fill
- Dark text on fill
- Rounded corners
- Soft transition on hover

```css
.button {
  background: linear-gradient(to right, #8CADA7, #8CADA7);
  color: RGB(29, 29, 29);
  border-radius: 4px;
  transition: all 0.3s ease;
}
```

### Hero section

The hero is the visual anchor:

- Dark background
- Oversized gradient headline
- Large animated type treatment
- Strong centered composition

This is the most distinctive visual element in the site and should be used deliberately for personal or portfolio branding moments.

### Cards and timelines

The experience section uses:

- Minimal lines and separators
- Clear text hierarchy
- Sage accent for years and hover states
- Clean, readable layout with strong structure

```css
.experience-year {
  font-size: 1.8rem;
  font-weight: 700;
  color: #8CADA7;
}
```

## 6. Interaction and motion

The site uses restrained motion and transitions:

- Hover color changes
- Smooth button transitions
- Animated gradient hero text
- Expand/collapse timeline reveal interactions

Recommended motion principles:

- Keep transitions subtle and quick
- Avoid heavy or distracting animations
- Use motion to reinforce hierarchy, not to dominate the page

## 7. Tone of voice

The site copy is:

- Thoughtful
- Confident
- Personal
- Clear and direct
- Reflective but professional

This matches the darker, minimal aesthetic and the engineering + environmental focus.

## 8. Visual rules of thumb

- Use the dark background for primary content surfaces
- Use sage green for key callouts and interactive emphasis
- Keep headings crisp, geometric, and modern
- Favor whitespace and structure over visual clutter
- Use the gradient hero only at major brand moments

## 9. Example usage summary

Use this combination when creating new content for the site:

- Background: `#1D1D1D`
- Text: `#F9F9F9`
- Accent: `#8CADA7`
- Heading style: `Montserrat` with strong weight
- Body style: `Hind`
- Button treatment: filled sage pill/button with dark text

This creates a cohesive identity that is modern, readable, and distinctly personal while still feeling technical and credible.
