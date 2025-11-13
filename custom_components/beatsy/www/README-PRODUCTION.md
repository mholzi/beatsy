# Beatsy Production Build

## Tailwind CSS Compilation

For production deployment, compile Tailwind CSS to reduce bundle size from 50KB (CDN) to ~10KB (compiled).

### Prerequisites

Install Tailwind CSS CLI (one-time setup):

```bash
npm install -D tailwindcss
```

### Build Command

From the `www/` directory, run:

```bash
npx tailwindcss -i css/input.css -o css/tailwind.min.css --minify
```

This will:
- Scan `admin.html`, `player.html`, and `js/**/*.js` for Tailwind classes
- Generate a minified CSS file with only the classes you're using
- Reduce CSS payload from 50KB to ~10KB

### Update HTML

After compilation, update `admin.html` to use the compiled CSS instead of CDN:

**Change from:**
```html
<!-- Tailwind CSS CDN for development -->
<script src="https://cdn.tailwindcss.com"></script>
```

**Change to:**
```html
<!-- Tailwind CSS (compiled for production) -->
<link rel="stylesheet" href="/local/beatsy/css/tailwind.min.css">
```

### Load Order

The final CSS load order should be:

1. `/local/beatsy/css/tailwind.min.css` - Tailwind utilities
2. `/local/beatsy/css/custom.css` - Custom Beatsy styles

### Performance Impact

- **Before:** 109KB total (50KB Tailwind CDN + 38KB JS + 18KB HTML + 3KB custom CSS)
- **After:** 51KB total (10KB Tailwind compiled + 20KB JS minified + 18KB HTML + 3KB custom CSS)
- **Load time improvement:** ~2.18s → ~1.02s on 3G

### Current Status

- **Development:** Using Tailwind CDN (easier for rapid iteration)
- **Production:** Should use compiled Tailwind (better performance)

See Story 3.1 code review for full optimization recommendations.
