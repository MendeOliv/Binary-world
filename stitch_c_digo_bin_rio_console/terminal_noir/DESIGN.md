---
name: Terminal Noir
colors:
  surface: '#111827'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#b7c8e1'
  on-secondary: '#213145'
  secondary-container: '#3a4a5f'
  on-secondary-container: '#a9bad3'
  tertiary: '#68dba9'
  on-tertiary: '#003825'
  tertiary-container: '#3eb686'
  on-tertiary-container: '#00422c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
  surface-elevated: '#1F2937'
  border-subtle: '#334155'
  text-primary: '#F1F5F9'
  text-secondary: '#94A3B8'
typography:
  headline-xl:
    fontFamily: JetBrains Mono
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: JetBrains Mono
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: JetBrains Mono
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: JetBrains Mono
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: JetBrains Mono
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  xs: 0.25rem
  sm: 0.5rem
  md: 1rem
  lg: 1.5rem
  xl: 2.5rem
  gutter: 1rem
  margin-mobile: 1rem
  margin-desktop: 2rem
---

## Brand & Style

This design system evolves the "Terminal Noir" aesthetic into a more sophisticated, "Soft Noir" experience. It targets professional developers and technical power users who require a high-focus environment that is easy on the eyes during extended sessions. The brand personality is disciplined, precise, and understated—moving away from high-contrast hacker tropes toward a refined, premium engineering workspace.

The design style is a blend of **Minimalism** and **Modern Corporate Noir**. It relies on deep atmospheric backgrounds, desaturated accent colors, and structural clarity. By softening the "ink-black" backgrounds and "neon" highlights of traditional terminal themes, the system achieves a more legible and professional interface that feels like a high-end IDE rather than a raw command prompt.

**Key Visual Principles:**
- **Atmospheric Depth:** Using deep charcoals and navy-greys to create a softer visual foundation.
- **Controlled Highlights:** Using emerald and forest greens sparingly to denote importance without visual noise.
- **Structural Subtlety:** Hierarchy is defined by subtle tonal shifts and thin, low-opacity borders rather than heavy shadows or bright lines.

## Colors

The palette is centered on a "Soft Noir" foundation, replacing harsh blacks with deep, desaturated cool tones to reduce eye fatigue.

- **Primary (Emerald #10B981):** A professional, desaturated green used for primary actions, active states, and success indicators.
- **Secondary (Slate #64748B):** A neutral, calming grey used for secondary text and non-essential UI elements to create a clear visual hierarchy.
- **Neutral (Deep Charcoal #0F172A):** The core background color, providing a smoother, less jarring experience than pure black.
- **Surface (#111827):** A slightly lighter container color used to lift content areas from the base background.

The system emphasizes "Slate" for secondary text specifically to lower the brightness of meta-information, ensuring that the primary content and green highlights remain the focal point.

## Typography

This system uses **JetBrains Mono** exclusively to maintain a consistent technical identity. Hierarchy is established through intentional weight management and the strategic use of color rather than font switching.

**Weight Strategy:**
- **Headlines:** Use Bold (700) or SemiBold (600) to create a clear entry point for information.
- **Body Text:** Use Regular (400) for maximum legibility in code and long-form descriptions.
- **Labels:** Use Medium (500) or SemiBold (600) in a slightly smaller size, often paired with the secondary Slate-grey color to distinguish them from interactive text.

Vertical rhythm is maintained by a 4px baseline. Large headlines should use negative letter-spacing to feel more compact and "block-like," while labels utilize positive spacing for increased clarity at small scales.

## Layout & Spacing

The layout philosophy follows a **Fixed Grid** approach for internal application views to simulate a structured dashboard, and a **Fluid Grid** for content-heavy pages.

- **Grid Model:** 12-column grid on desktop, 4-column on mobile.
- **Margins & Gutters:** 32px (2rem) desktop margins provide a "framed" look, while 16px (1rem) gutters keep data-dense components tightly organized.
- **Responsive Reflow:** On mobile, sidebars collapse into a bottom navigation or drawer, and grid columns stack vertically.

Spacing is strictly based on a 4px (0.25rem) increment system. Use `md` (16px) for internal padding of components and `xl` (40px) for separating major vertical sections.

## Elevation & Depth

Depth is achieved through **Tonal Layering** and **Low-Contrast Outlines**. This system avoids heavy drop shadows, opting instead for a "stacked" surface model that feels physical but flat.

- **Level 0 (Base):** Deep Charcoal (#0F172A).
- **Level 1 (Default Surface):** Lighter Grey-Navy (#111827). Defined by a 1px border in Slate-800 (#1E293B).
- **Level 2 (Active/Elevated):** Surface (#1F2937). Used for modals and items being hovered. 
- **Shadows:** Only used for floating elements (modals, dropdowns). Shadows are ambient, low-opacity, and tinted with the base background color (e.g., `0px 10px 15px -3px rgba(2, 6, 23, 0.5)`).

Interactive states should be indicated by changing border colors to the Primary Emerald or by a subtle brightness increase of the surface color.

## Shapes

The shape language is **Soft (0.25rem)**. This provides a subtle "friendliness" to the otherwise rigid terminal aesthetic without losing the sense of technical precision.

- **Small Components:** Buttons, inputs, and tags use `rounded` (4px).
- **Large Components:** Cards and modals use `rounded-lg` (8px).
- **Full Rounded:** Only used for status "pips" or search bars to provide a clear visual distinction from standard interactive blocks.

Borders are strictly 1px. Use the Secondary Slate color for default borders and the Primary Emerald for active/focus states.

## Components

### Buttons
- **Primary:** Forest green background (#10B981) with #0F172A text. Bold weight.
- **Secondary:** Transparent background with 1px Slate border. Text in Slate-300 (#CBD5E1).
- **Active State:** On hover, primary buttons darken slightly to #059669; secondary buttons change border and text to Emerald.

### Input Fields
- **Base:** Background #111827, 1px border #334155.
- **Focus:** Border transitions to #10B981. A very subtle inner glow (1px) in Emerald may be used to indicate focus.

### Cards
- Surfaces use #111827 with 1px #1E293B borders. 
- Headers should use a 1px divider to separate title metadata from the body.

### Chips & Status
- **Neutral:** Slate background at 10% opacity with Slate-400 text.
- **Success:** Emerald background at 10% opacity with Emerald-400 text.

### Lists & Tables
- Row dividers should be 1px and use a very low-contrast Slate (#1E293B).
- Selected rows use a subtle background highlight of #1F2937.

### Scrollbars
- Styled to be thin and unobtrusive. Thumb color should be Slate-700 with a 4px border radius.