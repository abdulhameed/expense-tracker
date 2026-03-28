# The Design System: Editorial Precision for Financial Clarity

## 1. Overview & Creative North Star: "The Financial Architect"
This design system moves beyond the generic "SaaS dashboard" to create a premium, editorial experience. The Creative North Star is **The Financial Architect**: a philosophy that treats financial data not as a cluttered ledger, but as a structured, breathable landscape. 

We break the "template" look by rejecting the standard 1px border. Instead, we use **intentional asymmetry** and **tonal depth**. By utilizing a high-contrast typography scale and a sophisticated layering of whites and off-whites, we create an environment that feels both authoritative and approachable. The layout should feel "curated," where the most important financial insights are framed by expansive whitespace, drawing the eye through a clear, intentional narrative.

---

## 2. Colors: Tonal Architecture
The palette is built on a foundation of "Neutral Grays" that provide a high-end, gallery-like backdrop for vibrant data visualization.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning or containment. Boundaries must be defined solely through background color shifts. Use `surface-container-low` (#f3f4f5) to sit on a `surface` (#f8f9fa) background. This creates a "soft edge" that feels integrated and premium rather than boxed-in.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. We use the Material Design surface tiers to define importance:
- **Base Layer:** `surface` (#f8f9fa) – The canvas.
- **Sectioning:** `surface-container` (#edeeef) – Large content areas.
- **Interactive Containers:** `surface-container-lowest` (#ffffff) – High-priority cards or input fields that "pop" against the darker base.

### The "Glass & Gradient" Rule
To elevate the experience, use **Glassmorphism** for floating elements (e.g., navigation bars or modal overlays). Apply `surface-container-lowest` at 80% opacity with a `20px` backdrop blur. 
- **Signature Texture:** For primary CTAs or the "Total Balance" hero card, use a subtle linear gradient transitioning from `primary` (#0058be) to `primary_container` (#2170e4) at a 135-degree angle. This adds "soul" and depth to the data.

---

## 3. Typography: Editorial Authority
We use 'Inter' for its neutral, modernist clarity, paired with a strict focus on hierarchy.

*   **Display & Headlines:** Use `display-md` (2.75rem) for high-impact totals. The tracking should be tightened slightly (-2%) to give it an editorial, "title-page" feel.
*   **Body & Labels:** Use `body-md` (0.875rem) for general information. 
*   **The Monospace Exception:** All financial amounts, transaction logs, and currency symbols must use a Monospace variant of Inter (or a system mono like JetBrains Mono) to ensure numerical alignment and a "data-driven" professional aesthetic.
*   **Hierarchy:** High contrast is key. Pair a `headline-lg` (2rem) title with a `label-sm` (0.6875rem) in `on_surface_variant` (#424754) to create an immediate sense of scale.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are often "muddy." In this design system, we achieve depth through **Ambient Light** principles.

*   **The Layering Principle:** Place a `surface-container-lowest` (#ffffff) card on a `surface-container-low` (#f3f4f5) background. The 4-step color shift provides enough contrast to signify a "lift" without any artificial effects.
*   **Ambient Shadows:** When a floating state is required (e.g., a dragged transaction or a dropdown), use an extra-diffused shadow: `box-shadow: 0 10px 30px rgba(25, 28, 29, 0.06)`. The shadow color is a tinted version of `on_surface`, not a dead neutral black.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility (e.g., in a high-glare environment), use the `outline_variant` token at **15% opacity**. Never use 100% opaque borders.

---

## 5. Components: The Building Blocks

### Buttons
*   **Primary:** Gradient-filled (`primary` to `primary_container`), `rounded-lg` (1rem/16px), with `label-md` white text.
*   **Secondary:** No background, no border. Use `primary` text color. On hover, apply a `surface-container-high` background shift.
*   **Tertiary:** `surface-container-highest` background with `on_surface` text for low-priority actions.

### Cards & Lists
*   **Forbid Dividers:** Do not use horizontal lines between transactions. Use the Spacing Scale `spacing-3` (1rem) or `spacing-4` (1.4rem) to create separation through "void space."
*   **Transaction Items:** Use a `surface-container-lowest` background for the entire list block. Differentiate items by a subtle hover state shift to `surface-container-high`.

### Input Fields
*   **Modern Minimalism:** Instead of a box, use a "Soft Inset" look. Use `surface-container-highest` (#e1e3e4) as the background with a `rounded-md` (0.75rem) corner. The label should sit above the field in `label-md` and `on_surface_variant`.

### Signature Component: The "Spending Horizon"
A custom data visualization component using a semi-transparent `secondary_container` (#6cf8bb) area chart. It should utilize Glassmorphism to allow the grid lines of the background to peek through, reinforcing the "Data-Driven" brand attribute.

---

## 6. Do's and Don'ts

### Do:
*   **Do** use the full range of the Spacing Scale to create "breathing room" around data.
*   **Do** use `secondary` (#006c49) for all "Income" or "Success" states to maintain a professional, banking-inspired feel.
*   **Do** align all currency amounts to a right-aligned grid to ensure readability.

### Don't:
*   **Don't** use 1px borders to separate content; use background color steps (`surface` vs `surface-container`).
*   **Don't** use pure black (#000000) for text. Use `on_surface` (#191c1d) to maintain a soft, premium feel.
*   **Don't** crowd the "Total Balance" area. It should be the most isolated and prominent element on the screen.
*   **Don't** use standard "drop shadows." If a shadow is needed, make it large, soft, and barely visible (4-6% opacity).