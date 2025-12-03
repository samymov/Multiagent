# Vanguard Corporate Portal Design System

This document outlines the complete design system extracted from [Vanguard's Corporate Portal](https://investor.vanguard.com/corporate-portal) and implemented in this application.

## Table of Contents
1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Spacing System](#spacing-system)
4. [Layout Structure](#layout-structure)
5. [Components](#components)
6. [Responsive Design](#responsive-design)

---

## Color Palette

### Primary Colors
- **Vanguard Red**: `#A6192E` - Primary brand color, used for CTAs and important actions
- **Vanguard Navy**: `#3C4651` - Secondary brand color, used for text and navigation
- **Vanguard Navy Dark**: `#2D2D2D` - Used for main headings
- **Vanguard Blue**: `#558BA5` - Accent color for hover states and links

### Neutral Colors
- **White**: `#FFFFFF` - Primary background
- **Gray Light**: `#F5F5F5` - Secondary background
- **Gray Medium**: `#E5E7EB` - Borders and dividers
- **Gray Text**: `#6B7280` - Secondary text
- **Gray Dark**: `#1F2937` - Primary text

### Semantic Colors
- **Success**: `#10B981` - Green for positive actions
- **Error**: `#A6192E` - Uses Vanguard Red
- **Warning**: `#F59E0B` - Amber for warnings
- **Info**: `#558BA5` - Uses Vanguard Blue

### CSS Variables
All colors are available as CSS variables:
```css
--vanguard-red: #A6192E;
--vanguard-navy: #3C4651;
--vanguard-navy-dark: #2D2D2D;
--vanguard-blue: #558BA5;
--vanguard-white: #FFFFFF;
--vanguard-gray-light: #F5F5F5;
--vanguard-gray-medium: #E5E7EB;
--vanguard-gray-text: #6B7280;
--vanguard-gray-dark: #1F2937;
```

---

## Typography

### Font Family
Vanguard uses system fonts for optimal performance:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Helvetica Neue', 'Arial', 'Helvetica', sans-serif;
```

### Font Sizes & Weights

#### Headings
- **H1**: `2.5rem` (40px) / `font-weight: 700` / `line-height: 1.2`
- **H2**: `2rem` (32px) / `font-weight: 600` / `line-height: 1.3`
- **H3**: `1.5rem` (24px) / `font-weight: 600` / `line-height: 1.4`
- **H4**: `1.25rem` (20px) / `font-weight: 600` / `line-height: 1.4`
- **H5**: `1.125rem` (18px) / `font-weight: 600` / `line-height: 1.5`
- **H6**: `1rem` (16px) / `font-weight: 600` / `line-height: 1.5`

#### Body Text
- **Base**: `1rem` (16px) / `font-weight: 400` / `line-height: 1.6`
- **Small**: `0.875rem` (14px) / `line-height: 1.5`
- **Large**: `1.125rem` (18px) / `line-height: 1.6`
- **Extra Large**: `1.25rem` (20px) / `line-height: 1.6`

### Capitalization Rules
- **Page Titles**: Title Case (manually applied)
- **Section Headings**: Sentence case
- **Body Text**: Standard sentence capitalization
- **Avoid**: ALL CAPS (harder to read, perceived as "screaming")

### Letter Spacing
- **H1**: `-0.02em`
- **H2**: `-0.01em`
- **Body**: Normal (0)

---

## Spacing System

Vanguard uses an **8px base unit** spacing system:

| Token | Value | Pixels | Usage |
|-------|-------|--------|-------|
| `--spacing-xs` | 0.25rem | 4px | Tight spacing |
| `--spacing-sm` | 0.5rem | 8px | Small spacing |
| `--spacing-md` | 1rem | 16px | Medium spacing (default) |
| `--spacing-lg` | 1.5rem | 24px | Large spacing |
| `--spacing-xl` | 2rem | 32px | Extra large spacing |
| `--spacing-2xl` | 3rem | 48px | Section spacing |
| `--spacing-3xl` | 4rem | 64px | Page spacing |

---

## Layout Structure

### Container
- **Max Width**: `1280px`
- **Padding**: Responsive
  - Mobile: `16px`
  - Tablet: `24px`
  - Desktop: `32px`

### Header/Navigation
- **Height**: `64px` (standard) / `60px` (sticky)
- **Background**: White (`#FFFFFF`)
- **Border**: `1px solid #E5E7EB`
- **Shadow**: `0 1px 3px rgba(0, 0, 0, 0.05)`
- **Position**: Sticky (when applicable)
- **Z-index**: `100`

### Logo
- **Height**: `32px` (max `40px` per guidelines)
- **Display**: Inline with brand text

### Footer
- **Background**: White
- **Border Top**: `1px solid #E5E7EB`
- **Padding**: `24px` vertical

---

## Components

### Buttons

#### Primary Button
```css
.btn-primary {
  background-color: var(--vanguard-navy);
  color: var(--vanguard-white);
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
}
```

#### Secondary Button
```css
.btn-secondary {
  background-color: transparent;
  color: var(--vanguard-navy);
  border: 1px solid var(--vanguard-navy);
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
}
```

#### Red Button (CTA)
```css
.btn-red {
  background-color: var(--vanguard-red);
  color: var(--vanguard-white);
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
}
```

#### Button Sizes
- **Default**: `0.75rem 1.5rem`
- **Large**: `1rem 2rem` / `font-size: 1.125rem`
- **Small**: `0.5rem 1rem` / `font-size: 0.875rem`

### Navigation Links
```css
.nav-link {
  font-size: 0.9375rem; /* 15px */
  font-weight: 500;
  color: var(--text-secondary);
  padding: 0.5rem 1rem;
  border-bottom: 2px solid transparent;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: var(--vanguard-navy);
}

.nav-link.active {
  color: var(--vanguard-navy);
  font-weight: 600;
  border-bottom-color: var(--vanguard-navy);
}
```

### Cards
```css
.card {
  background: var(--vanguard-white);
  border: 1px solid var(--border-light);
  border-radius: 4px;
  padding: var(--spacing-lg);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### Links
```css
a {
  color: var(--vanguard-navy);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--vanguard-blue);
  text-decoration: underline;
}
```

---

## Responsive Design

### Breakpoints

| Device | Width | Description |
|--------|-------|-------------|
| **Small** | `≤ 600px` | Phones |
| **Medium** | `601px - 900px` | Tablets |
| **Large** | `≥ 901px` | Desktops |

### Responsive Typography
- **Mobile**: Reduced heading sizes
  - H1: `2rem` (32px)
  - H2: `1.75rem` (28px)
  - H3: `1.25rem` (20px)

### Responsive Layout
- **Mobile**: Full-width buttons, reduced padding
- **Tablet**: Adjusted container padding
- **Desktop**: Full container width (1280px max)

---

## Implementation

### CSS File Structure
```
frontend/styles/
├── globals.css              # Main stylesheet (imports design system)
└── vanguard-design-system.css  # Complete design system
```

### Usage Examples

#### Using CSS Variables
```css
.my-component {
  color: var(--vanguard-navy);
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  padding: var(--spacing-md);
}
```

#### Using Utility Classes
```html
<div class="container">
  <h1 class="page-title">Page Title</h1>
  <p class="text-lg">Large body text</p>
  <button class="btn btn-primary">Primary Action</button>
</div>
```

#### Using Component Classes
```html
<nav class="header sticky">
  <div class="container">
    <a href="/dashboard" class="nav-link active">Dashboard</a>
  </div>
</nav>
```

---

## Design Principles

1. **Clean & Professional**: Minimal design with focus on content
2. **Accessibility**: High contrast ratios, clear typography
3. **Performance**: System fonts for fast loading
4. **Consistency**: 8px spacing grid throughout
5. **Responsive**: Mobile-first approach
6. **Brand Alignment**: Colors and typography match Vanguard's corporate identity

---

## References

- **Source**: [Vanguard Corporate Portal](https://investor.vanguard.com/corporate-portal)
- **Brand Guidelines**: Based on Vanguard's official brand standards
- **Implementation Date**: December 2025

