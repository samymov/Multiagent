# Vanguard Corporate Portal Design System

This document outlines the design system based on [Vanguard's Corporate Portal](https://investor.vanguard.com/corporate-portal) to ensure visual consistency across the application.

## Color Palette

### Primary Brand Colors
- **Vanguard Navy**: `#3C4651` - Primary brand color for headers, navigation, and key UI elements
- **Vanguard Navy Dark**: `#2D2D2D` - Dark navy for main headings and emphasis
- **Vanguard Blue**: `#558BA5` - Accent blue for links, hover states, and highlights
- **Vanguard Red**: `#BA0C2F` - Used sparingly for errors and important alerts

### Neutral Colors
- **White**: `#FFFFFF` - Primary background
- **Gray Light**: `#F5F5F5` - Light background areas
- **Gray Medium**: `#E5E7EB` - Borders and dividers
- **Gray Text**: `#6B7280` - Secondary text
- **Gray Dark**: `#1F2937` - Primary text
- **Gray Muted**: `#9CA3AF` - Muted text

### Accent Colors
- **Yellow/Gold**: `#EDBA75` - Accent color for CTAs
- **Yellow Light**: `#FFF9E6` - Light yellow background for disclaimers

### Semantic Colors
- **Success**: `#10B981` - Green for success states
- **Error**: `#BA0C2F` - Red for errors (uses Vanguard red)
- **Warning**: `#F59E0B` - Orange for warnings
- **Info**: `#558BA5` - Blue for informational messages

## Typography

### Font Family
Vanguard uses system fonts for optimal performance and consistency:
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Helvetica Neue', 'Arial', 'Helvetica', sans-serif;
```

### Font Sizes & Hierarchy
- **H1**: `2.5rem` (40px) - Main page titles, weight: 700
- **H2**: `2rem` (32px) - Section headings, weight: 600
- **H3**: `1.5rem` (24px) - Subsection headings, weight: 600
- **H4**: `1.25rem` (20px) - Card titles, weight: 600
- **Body**: `1rem` (16px) - Default text, weight: 400
- **Small**: `0.875rem` (14px) - Secondary text, weight: 400

### Line Heights
- Headings: 1.2-1.4
- Body text: 1.6
- Small text: 1.5

### Letter Spacing
- H1: `-0.01em`
- H2: `-0.01em`
- Body: Normal

## Spacing System

Based on 8px base unit:
- **XS**: `0.25rem` (4px)
- **SM**: `0.5rem` (8px)
- **MD**: `1rem` (16px)
- **LG**: `1.5rem` (24px)
- **XL**: `2rem` (32px)
- **2XL**: `3rem` (48px)
- **3XL**: `4rem` (64px)

## Layout Structure

### Container
- Max width: `1280px`
- Responsive padding:
  - Mobile: `1rem` (16px)
  - Tablet: `1.5rem` (24px)
  - Desktop: `2rem` (32px)

### Header/Navigation
- Background: White
- Height: `64px` (min-height for sticky)
- Border: `1px solid #E5E7EB`
- Shadow: `0 1px 2px rgba(0, 0, 0, 0.05)`
- Sticky header: `z-index: 1000`

### Navigation Links
- Font size: `0.9375rem` (15px)
- Font weight: 500 (normal), 600 (active)
- Color: `#6B7280` (secondary), `#3C4651` (active/hover)
- Active indicator: 2px bottom border in navy
- Padding: `0.5rem 1rem`

## Buttons

### Primary Button
- Background: `#3C4651` (Vanguard Navy)
- Color: White
- Padding: `0.75rem 1.5rem`
- Border radius: `4px`
- Font weight: 500
- Hover: Darker navy (`#2D2D2D`)

### Secondary Button
- Background: Transparent
- Color: `#3C4651`
- Border: `1px solid #3C4651`
- Hover: Fill with navy background

### Large Button
- Padding: `1rem 2rem`
- Font size: `1.125rem` (18px)

### Small Button
- Padding: `0.5rem 1rem`
- Font size: `0.875rem` (14px)

## Cards & Containers

### Card
- Background: White
- Border: `1px solid #E5E7EB`
- Border radius: `4px`
- Padding: `1.5rem` (24px)
- Shadow: `0 1px 3px rgba(0, 0, 0, 0.05)`
- Hover shadow: `0 4px 6px rgba(0, 0, 0, 0.1)`

## Links

- Color: `#3C4651` (Vanguard Navy)
- Hover: `#558BA5` (Vanguard Blue) with underline
- Focus: `2px solid #558BA5` outline with `2px` offset

## Footer

### Disclaimer Box
- Background: `#FFF9E6` (Light yellow)
- Border: `1px solid #EDBA75` (Yellow)
- Border radius: `4px`
- Padding: `1rem` (16px)
- Margin bottom: `1rem` (16px)

### Copyright
- Font size: `0.75rem` (12px)
- Color: `#9CA3AF` (Muted gray)
- Text align: Center
- Border top: `1px solid #E5E7EB`
- Padding top: `1rem` (16px)

## Responsive Breakpoints

- **Small devices** (phones): Up to `600px`
- **Medium devices** (tablets): `601px` to `900px`
- **Large devices** (desktops): `901px` and above

## Accessibility

- Focus states: `2px solid #558BA5` outline with `2px` offset
- Color contrast: All text meets WCAG AA standards
- Smooth scrolling: Enabled for better UX
- Font smoothing: Antialiased for better readability

## Usage Examples

### CSS Variables
```css
/* Colors */
color: var(--vanguard-navy);
background-color: var(--bg-primary);
border-color: var(--border-light);

/* Spacing */
padding: var(--spacing-md);
margin-top: var(--spacing-lg);

/* Typography */
font-family: var(--font-primary);
```

### Component Classes
```html
<!-- Navigation Link -->
<a href="/dashboard" class="nav-link active">Dashboard</a>

<!-- Button -->
<button class="btn btn-primary">Get Started</button>

<!-- Card -->
<div class="card">
  <h3 class="card-title">Card Title</h3>
  <p>Card content</p>
</div>
```

## Design Principles

1. **Clean & Professional**: Minimal design with clear hierarchy
2. **Consistent Spacing**: Use the 8px base unit system
3. **Accessible**: High contrast, clear focus states
4. **Performance**: System fonts for fast loading
5. **Responsive**: Mobile-first approach with breakpoints

