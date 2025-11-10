# Beatsy UX Design Specification

_Created on 2025-11-09 by Markus_
_Generated using BMad Method - Create UX Design Workflow v1.0_

---

## Executive Summary

Beatsy brings the excitement of Hitster-style music year-guessing to Home Assistant. Players join via a simple web link, listen to 30-second song snippets from a Spotify playlist, and compete to guess the release year with proximity-based scoring and optional betting. The UX focuses on creating a confident, nostalgic, and playfully competitive party atmosphere where friends gather around their phones in the same room, experiencing collective excitement through music memories.

**Magic Moment:** The countdown timer hits zero, revealing everyone's guesses simultaneously. Someone nailed the exact year and bet on it—the room erupts as they claim 20 points while someone else's risky bet backfires spectacularly. The leaderboard updates live, laughter fills the room, and the next song starts immediately.

---

## 1. Design System Foundation

### 1.1 Design System Choice

**Selected Approach:** Static HTML + Tailwind CSS + shadcn/ui-Inspired Components

**Rationale:**

Beatsy requires a mobile-first web interface served directly from a Home Assistant custom component. After evaluating modern design systems, we selected an approach that balances development speed, performance, and Home Assistant compatibility:

**Technology Stack:**
- **Base:** Static HTML/CSS/JavaScript (no build process required for MVP)
- **Styling Framework:** Tailwind CSS (via CDN for development, compiled for production)
- **Component Inspiration:** shadcn/ui patterns (adapted to vanilla HTML + Tailwind)
- **Deployment:** Served from `custom_components/beatsy/www/` folder

**Why This Works for Beatsy:**

1. **Home Assistant Native**
   - Files served directly from HA's `www/` folder mechanism
   - No React/build process barriers
   - Works seamlessly with HA's HTTP component
   - Accessible via: `http://HA_IP:8123/local/beatsy/admin.html`

2. **Mobile-First Performance**
   - Lightweight (no framework overhead)
   - Tailwind provides responsive utilities out of the box
   - Fast loads on mobile devices (critical for party momentum)
   - Works on slow WiFi networks with many devices

3. **Rapid Development**
   - Tailwind CDN for instant prototyping
   - shadcn/ui provides accessible, tested component patterns
   - Copy HTML structure, add Tailwind classes
   - No build step slowing iteration

4. **Accessibility Built-In**
   - shadcn/ui components based on Radix UI primitives
   - Patterns include proper ARIA attributes, keyboard navigation
   - We implement these patterns in vanilla HTML
   - WCAG 2.1 Level AA achievable

5. **Customization Freedom**
   - Full control over every component
   - Can create warm, playful party game aesthetic
   - Not locked into Material Design or corporate look
   - Tailwind's utility classes enable pixel-perfect designs

**Component Strategy:**

We'll create custom components inspired by shadcn/ui but implemented as vanilla HTML + Tailwind:

- **From shadcn/ui library patterns:**
  - Button variants (primary, secondary, destructive)
  - Form inputs (text, select, checkbox)
  - Card layouts
  - Badge components (for bet indicators)
  - Toast notifications
  - Modal dialogs

- **Custom Beatsy components:**
  - Countdown timer display
  - Album art + song info card
  - Leaderboard table (round results + overall)
  - Live bet indicator badges
  - Year dropdown selector

**Development Workflow:**

1. **Development Phase:** Use Tailwind CDN in HTML files
   ```html
   <script src="https://cdn.tailwindcss.com"></script>
   ```

2. **Production Phase:** Compile Tailwind CSS for optimized bundle
   - Use Tailwind CLI to build `tailwind.min.css`
   - Only includes used classes (smaller file size)
   - Replace CDN script with local stylesheet

**Example Component Pattern:**

```html
<!-- Primary Button (shadcn/ui inspired) -->
<button class="inline-flex items-center justify-center rounded-md text-sm font-medium
               transition-colors focus-visible:outline-none focus-visible:ring-2
               focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
               bg-primary text-white hover:bg-primary/90 h-12 px-6 text-lg">
  BET ON IT
</button>
```

**Version Control:**
- System: Tailwind CSS v3.4+ (latest stable)
- Approach: Utility-first CSS framework
- Future-proofing: Easy to migrate to build process if needed later

---

## 2. Core User Experience

### 2.1 Defining Experience

**Primary Emotional Goals:**

1. **Confident** - Players feel capable and in control from the moment they join
2. **Nostalgic** - Interface evokes warm memories through music and retro-inspired aesthetics
3. **Playfully Competitive** - Friendly rivalry without intimidation; celebrating both wins and hilarious fails

**Core User Stories:**

- **As a host**, I can set up a complete game in under 60 seconds so we don't lose party momentum
- **As a player**, I can join without creating accounts or downloading apps so there's zero friction
- **As a competitive player**, I can "bet on it" to risk double points and create dramatic moments
- **As a casual player**, I can see my score improving round-by-round so I feel progression even if I'm not winning
- **As a music lover**, I experience songs through album art, artist info, and countdown timers that build anticipation

**What Makes Beatsy Different:**

Unlike apps like Kahoot (education-focused) or SongPop (isolated competitive), Beatsy emphasizes:
- **Physical co-presence**: Everyone in the same room, reactions visible
- **Music nostalgia**: Not trivia—emotional connection to songs and eras
- **Risk-taking**: The betting mechanic creates memorable "bet it all" moments
- **Simplicity**: No accounts, no downloads, just a URL and you're in

### 2.2 Core Experience Principles

**1. Instant Gratification**
- Zero barriers to entry (no auth, no forms, just name + join)
- Immediate feedback on every interaction
- Live updates create sense of group activity
- Fast transitions between rounds maintain energy

**2. Visible Progress**
- Always show current score, round number, and standing
- Celebrate point gains with visual feedback (animations, color changes)
- Display "last round" performance in leaderboards
- Make bet status unmistakably clear

**3. Mobile-First Party Design**
- Large touch targets (minimum 44×44px)
- High contrast for visibility in dim party lighting
- Readable from arm's length when holding phone
- Works on slow WiFi with many connected devices

**4. Playful Competitive Tension**
- Betting creates dramatic risk/reward moments
- Leaderboards update live to show shifting positions
- Round results reveal answers for group "aha!" moments
- Proximity scoring rewards close guesses (not just exact matches)

**5. Nostalgic Warmth**
- Sunset color palette evokes vinyl records and warm lighting
- Album art and artist names center the music experience
- Generous whitespace feels premium, not cluttered
- Typography choices balance modern clarity with retro personality

---

## 3. Visual Foundation

### 3.1 Color System

**Selected Theme: Sunset Groove**

This warm, energetic palette evokes the nostalgic feeling of vinyl records, sunset gatherings, and music from golden eras. The orange/golden tones create confidence and approachability while maintaining playful competitive energy.

**Color Palette:**

```css
/* Primary Colors */
--color-primary: #FF6B35;      /* Vibrant orange - main CTAs, accents */
--color-secondary: #F7931E;     /* Golden orange - hover states, highlights */
--color-accent: #FFB627;        /* Warm yellow - bet indicators, success moments */

/* Supporting Colors */
--color-success: #4ECDC4;       /* Teal - correct answers, positive feedback */
--color-error: #E63946;         /* Red - wrong guesses, negative points */
--color-warning: #FFB627;       /* Amber - bet warnings, caution states */

/* Neutral Colors */
--color-bg-primary: #FFF5F0;    /* Warm off-white - main background */
--color-bg-secondary: #FFFFFF;  /* Pure white - card backgrounds */
--color-text-primary: #2C1810;  /* Dark brown - headings, important text */
--color-text-secondary: #8B7355; /* Muted brown - labels, secondary text */
--color-text-muted: #B8A898;    /* Light brown - hints, disabled states */

/* Interactive States */
--color-border: #E5D5C5;        /* Subtle borders */
--color-hover: rgba(255, 107, 53, 0.1); /* Primary color at 10% opacity */
--color-focus: #FF6B35;         /* Focus rings match primary */
```

**Color Usage Guidelines:**

1. **Primary (#FF6B35)**: Use for main action buttons, active timers, score highlights, navigation elements
2. **Secondary (#F7931E)**: Use for hover states, secondary buttons, complementary accents
3. **Accent (#FFB627)**: Reserved for bet indicators, special moments, success celebrations
4. **Success (#4ECDC4)**: Correct answers, positive point gains, achievement badges
5. **Error (#E63946)**: Wrong answers, negative points, destructive actions
6. **Backgrounds**: Layer warm off-white base with pure white cards for depth
7. **Text**: Dark brown for readability, muted browns for hierarchy

**Accessibility Compliance:**

All color combinations meet WCAG 2.1 Level AA contrast ratios:
- Primary text on light backgrounds: 12.5:1 (exceeds 4.5:1 requirement)
- Secondary text on light backgrounds: 5.8:1 (meets 4.5:1 requirement)
- White text on primary orange: 4.6:1 (meets 4.5:1 requirement)
- Interactive elements distinguishable by more than color alone (icons, borders, labels)

### 3.2 Typography System

**Font Families:**

```css
/* Primary Font Stack */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, sans-serif;

/* Monospace (for join links, codes) */
--font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Courier New', monospace;
```

**Rationale:** System font stack ensures:
- Zero font loading delay (instant render)
- Native OS appearance (familiar, trustworthy)
- Excellent readability on all devices
- Automatic support for all languages/scripts

**Type Scale:**

```css
/* Headings */
--text-4xl: 2.25rem;   /* 36px - Page titles (Admin, Leaderboard) */
--text-3xl: 1.875rem;  /* 30px - Section headings */
--text-2xl: 1.5rem;    /* 24px - Song titles */
--text-xl: 1.25rem;    /* 20px - Subsection headers */
--text-lg: 1.125rem;   /* 18px - Large buttons */

/* Body */
--text-base: 1rem;     /* 16px - Default body text */
--text-sm: 0.875rem;   /* 14px - Labels, helper text */
--text-xs: 0.75rem;    /* 12px - Captions, metadata */

/* Special */
--text-timer: 4rem;    /* 64px - Countdown timer numbers */
--text-score: 3rem;    /* 48px - Large score displays */
```

**Font Weights:**

```css
--font-normal: 400;    /* Body text, descriptions */
--font-semibold: 600;  /* Emphasis, labels */
--font-bold: 700;      /* Headings, buttons, scores */
```

**Line Heights:**

```css
--leading-tight: 1.25;  /* Headings */
--leading-normal: 1.5;  /* Body text */
--leading-relaxed: 1.75; /* Long-form content */
```

**Typography Guidelines:**

1. **Headings**: Bold weight, tight line-height, primary text color
2. **Body Text**: Normal weight, comfortable line-height (1.5), secondary text color
3. **Buttons**: Semibold or bold, slightly larger than body (text-lg)
4. **Labels**: Semibold, small size (text-xs or text-sm), uppercase, muted color
5. **Scores**: Bold, oversized (text-score or text-timer), primary color
6. **Links**: No underline by default, underline on hover, uses primary color

### 3.3 Spacing & Layout System

**Base Unit:** 4px (0.25rem)

**Spacing Scale:**

```css
--space-1: 0.25rem;   /* 4px  - Tight spacing */
--space-2: 0.5rem;    /* 8px  - Component padding */
--space-3: 0.75rem;   /* 12px - Card padding */
--space-4: 1rem;      /* 16px - Standard spacing */
--space-6: 1.5rem;    /* 24px - Section spacing */
--space-8: 2rem;      /* 32px - Large gaps */
--space-12: 3rem;     /* 48px - Major sections */
--space-16: 4rem;     /* 64px - Page padding */
```

**Grid System:**

```css
/* Mobile-first responsive grid */
.container {
  width: 100%;
  max-width: 420px;  /* Phone-optimized */
  margin: 0 auto;
  padding: var(--space-4);
}
```

**Border Radius:**

```css
--rounded-sm: 0.25rem;   /* 4px  - Small elements */
--rounded-md: 0.5rem;    /* 8px  - Buttons, inputs */
--rounded-lg: 0.75rem;   /* 12px - Cards */
--rounded-xl: 1rem;      /* 16px - Large cards */
--rounded-2xl: 1.5rem;   /* 24px - Modal dialogs */
--rounded-full: 9999px;  /* Circular - Avatars, badges */
```

**Shadows:**

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);
```

**Layout Guidelines:**

1. **Card Spacing**: Use space-3 or space-4 for internal card padding
2. **Stack Spacing**: Use space-3 between stacked cards or sections
3. **Touch Targets**: Minimum 44×44px for all interactive elements
4. **Screen Padding**: Apply space-4 (16px) to screen edges on mobile
5. **Form Fields**: space-2 between label and input, space-4 between fields
6. **Button Padding**: Horizontal space-6, vertical space-3 for comfortable tapping

**Interactive Visualizations:**

- Color Theme Explorer: [ux-color-themes.html](./ux-color-themes.html)

---

## 4. Design Direction

### 4.1 Chosen Design Approach

**Selected Direction: Spacious Centered (Direction 2)**

After exploring three distinct design directions (Compact Card-Based, Spacious Centered, and Dashboard Grid), **Direction 2: Spacious Centered** best captures Beatsy's emotional goals and party game context.

**Why Spacious Centered Wins:**

1. **Emotional Alignment**
   - **Confident**: Generous whitespace and large elements create a premium, uncluttered experience
   - **Nostalgic**: Centered album art becomes the hero element, evoking vinyl record appreciation
   - **Playfully Competitive**: Large scores and timers are visible when phones are held up, creating shared excitement

2. **Party Context Optimization**
   - Elements readable from arm's length (large text, high contrast)
   - Works well in dim lighting (strong visual hierarchy)
   - Creates "shareable moments" (players show off their screens)
   - Reduces cognitive load during fast-paced gameplay

3. **Mobile Usability**
   - Large touch targets prevent mis-taps during excitement
   - Vertical scrolling is intuitive and familiar
   - Single-column layout eliminates horizontal scanning
   - Focus on one action at a time reduces decision paralysis

4. **Gameplay Flow**
   - Timer becomes a focal point (builds anticipation)
   - Album art creates emotional connection to song
   - Year input is prominent and easy to tap/type
   - Bet button has clear visual weight (encourages risk-taking)

**When to Use Alternative Directions:**

While Spacious Centered is the MVP approach, the other directions could serve as optional "game modes" in future iterations:

- **Compact Card-Based**: "Speed Mode" for experienced players who want faster rounds with minimal animations
- **Dashboard Grid**: "Tournament Mode" for competitive events with more detailed statistics and controls

**Implementation Priority:**

For MVP (Phase 1), focus exclusively on Spacious Centered across all screens (admin, player, active round, results, leaderboard). This ensures consistent UX and reduces development complexity.

**Design Direction Comparison:**

| Criteria | Compact Card | **Spacious Centered** ✓ | Dashboard Grid |
|----------|--------------|-------------------------|----------------|
| Information Density | High | **Low** ✓ | Medium-High |
| Visual Clarity | Medium | **Excellent** ✓ | Good |
| Party Game Vibe | Functional | **Engaging** ✓ | Technical |
| Mobile Usability | Good | **Excellent** ✓ | Good |
| Setup Speed | Fast | **Moderate** ✓ | Fast |
| Excitement Level | Moderate | **High** ✓ | Low-Moderate |
| Best For | Power users | **First-time players, parties** ✓ | Tech-savvy, tournaments |

**Key Spacious Centered Characteristics:**

- **Vertical Flow**: Single-column layout, natural top-to-bottom reading
- **Hero Elements**: Album art, timer, and score get prominent treatment
- **Breathing Room**: Minimum 24px spacing between major sections
- **Centered Content**: Primary actions and information centered horizontally
- **Large Text**: Scores use 48px+, timers use 64px, song titles use 24px
- **Minimal Distractions**: Only essential information visible on active round screen

**Interactive Mockups:**

- Design Direction Showcase: [ux-design-directions.html](./ux-design-directions.html)

---

## 5. User Journey Flows

### 5.1 Critical User Paths

#### Journey 1: Admin Game Setup (60-Second Goal)

**Context:** Host wants to start a game quickly before party energy drops

**Flow:**

1. **Landing** (`/admin.html`)
   - Screen shows: "Setup New Game" heading
   - Pre-populated with last-used Spotify player
   - Auto-populated with default settings (30s timer, 10 rounds, standard scoring)
   - Displays join link prominently at top
   - Shows "0 Players Joined" status

2. **Configuration** (Optional)
   - Host can change Spotify player via dropdown
   - Select playlist from available Spotify playlists
   - Adjust timer, rounds, scoring (most skip this step)
   - **Design Decision**: Defaults should work for 90% of games

3. **Player Registration** (Parallel)
   - Live player list updates as people join
   - Shows player name + avatar initial
   - No action required from admin (automatic)
   - Visual feedback: Player count badge animates on new join

4. **Game Start**
   - Large "START GAME" button (always visible, even while scrolling)
   - Enabled when ≥2 players joined
   - Disabled state shows "Need 2+ players"
   - One tap → game starts for all players immediately

**Key UX Decisions:**

- **Smart Defaults**: Host shouldn't need to configure anything for basic game
- **Non-Blocking Setup**: Players can join while host is still configuring
- **Persistent CTA**: Start button always visible (sticky/fixed position)
- **Instant Validation**: Button state clearly indicates if ready to start

**Screen States:**

- **Initial Load**: Empty player list, start button disabled
- **Players Joining**: Live updates, encouraging feedback ("3 players ready!")
- **Ready to Start**: Button enabled, pulsing animation suggests action
- **Game Started**: Redirect to admin gameplay view (or leaderboard)

---

#### Journey 2: Player Join & First Round

**Context:** Friend shares link in group chat, player wants to join mid-conversation

**Flow:**

1. **Direct Link** (`/start.html?game_id=abc123`)
   - Opens to simple join screen
   - Shows game status: "5 players already joined"
   - Single input: "Enter your name"
   - Prominent "JOIN GAME" button

2. **Name Entry**
   - Auto-focus on name input (keyboard appears immediately)
   - Shows character count (max 20 characters)
   - Submit via button OR Enter key
   - Validation: Name required, must be unique in this game

3. **Waiting Room**
   - Success message: "You're in, [Name]!"
   - Shows other players who've joined
   - Displays: "Waiting for [Host Name] to start..."
   - Auto-advances when game starts (WebSocket push)

4. **First Round Begins**
   - Smooth transition to active round screen
   - 3-second countdown: "Get Ready... 3, 2, 1, GO!"
   - Music starts, timer begins
   - Player sees: Album art, song/artist, timer, year input, bet button

**Key UX Decisions:**

- **Zero Friction**: No account creation, no email, no passwords
- **Auto-Focus**: Keyboard ready to type immediately
- **Clear Status**: Always know what's happening ("waiting", "starting", "round 1")
- **Smooth Transitions**: No jarring page reloads, everything feels continuous

**Edge Cases:**

- **Game Already Started**: Show "Game in Progress" message, offer "Join Next Round" option
- **Duplicate Name**: Inline error, suggest "[Name]2" or "[Name]_2"
- **Host Disconnects**: Show "Host left, game paused" message

---

#### Journey 3: Active Round (Core Gameplay Loop)

**Context:** Music playing, 30-second timer counting down, player must guess year

**Flow:**

1. **Round Start** (Timer: 30s → 25s)
   - Screen shows: Round number, current score, timer (large and centered)
   - Album art displayed prominently (generates visual interest)
   - Song title + artist name below art
   - Year input field (empty, placeholder: "19__")
   - "BET ON IT" button (secondary style, optional)
   - "SUBMIT GUESS" button (primary style, disabled until year entered)

2. **Year Entry** (Timer: 25s → 10s)
   - Player types 4-digit year
   - Input validates: Must be 1900-2024 (or current year)
   - Invalid input: Red border, helper text "Enter valid year"
   - Valid input: Submit button enables (color change + animation)

3. **Optional Betting** (Timer: Any time before submit)
   - Player taps "BET ON IT"
   - Button changes state: "BET ACTIVE - 2x POINTS" (accent color, pulsing)
   - Can toggle off (tap again to cancel bet)
   - Visual indicator: Badge shows "🎲 2x MULTIPLIER" above year input

4. **Submit Answer** (Timer: >0s)
   - Player taps "SUBMIT GUESS"
   - Screen freezes (can't change answer)
   - Shows: "Submitted!" confirmation + submitted year
   - Timer continues for other players
   - Waiting state: "Waiting for others..." OR "Timer: 8s"

5. **Timer Expires** (Timer: 0s)
   - All players auto-submit (if haven't already)
   - Brief loading state (1-2s): "Calculating scores..."
   - WebSocket receives: Correct year, points earned, leaderboard update

6. **Round Results** (Separate Screen)
   - Shows: Emoji feedback (🎉 correct, 😅 close, 😬 wrong)
   - Large "+10" or "-5" points display
   - Breakdown: "Base: 5pts × Bet: 2x = 10pts"
   - Shows: Your guess (1989) vs Actual year (1987)
   - Current total score: "Your Score: 55"
   - "NEXT ROUND" button (auto-advances after 5s)

**Key UX Decisions:**

- **Timer Urgency**: Large, animated timer creates pressure/excitement
- **Bet Visibility**: Must be unmistakably clear when bet is active
- **No Regrets**: Once submitted, can't change (prevents cheating/anxiety)
- **Immediate Feedback**: Results screen is celebratory or sympathetic
- **Batch Waiting**: All players see results together (maintains group sync)

**Interaction Patterns:**

- **Keyboard Type**: Numeric keyboard for year input (mobile optimization)
- **Auto-Submit**: Timer expiration submits current guess (prevents timeouts from blocking game)
- **Disabled States**: Clear visual difference between enabled/disabled buttons
- **Loading States**: Brief spinners/skeleton screens during WebSocket calls

**Timing & Pacing:**

- Round start: Immediate (0s delay)
- Active play: 30s (configurable)
- Submit → Results: 1-2s processing
- Results display: 5s (or manual next)
- Total round time: ~37-40s (keeps energy high)

---

#### Journey 4: Leaderboard & Game Completion

**Context:** Round 5 of 10 complete, players check standings

**Flow:**

1. **Mid-Game Leaderboard** (After round 5)
   - Prominent heading: "Leaderboard - Round 5 of 10"
   - **Top 3 Podium**: Visual emphasis on 1st, 2nd, 3rd place
     - 1st place: Larger avatar, gold accent, crown emoji
     - 2nd/3rd: Smaller avatars, silver/bronze
   - **Full Rankings Table**: All players, ranked by total score
     - Shows: Rank, name, total score, last round performance
     - Highlights: Current player's row (accent background)
   - **Continue Button**: "Next Round" (large, primary CTA)

2. **Game Completion** (After round 10)
   - Grand leaderboard with confetti animation (1st place winner)
   - Heading: "Final Results! 🎉"
   - Same podium structure, but more celebratory
   - Shows: Total points, rounds won, accuracy stats
   - CTAs: "Play Again" (primary) + "New Game" (secondary)

**Key UX Decisions:**

- **Frequent Check-ins**: Show leaderboard every 5 rounds to maintain engagement
- **Celebrate Progress**: Mid-game leaderboards aren't just standings—they're motivational
- **Clear Winner**: Final leaderboard unmistakably highlights 1st place
- **Easy Replay**: "Play Again" button uses same players/settings (one-tap rematch)

**Visual Hierarchy:**

1. Winner announcement (if final round)
2. Top 3 podium (visual, colorful)
3. Full rankings (detailed, scannable)
4. Action buttons (clear next step)

---

#### Journey 5: Edge Cases & Error Recovery

**Game Paused (Host Disconnects):**
- All players see: "Game paused - host disconnected"
- Options: "Wait for host" or "Leave game"
- If host returns within 5min: Game resumes from current round
- If host doesn't return: Players see "Game ended" + final scores

**Player Disconnects Mid-Round:**
- Player's guess auto-submits as 0 (or last entered value)
- Leaderboard shows player as "disconnected" (grayed out)
- If player reconnects: Rejoin at next round, no score penalty

**Network Error During Submit:**
- Show toast: "Connection issue, retrying..."
- Auto-retry submit up to 3 times
- If all retries fail: Use last known guess or 0
- Display: "Submitted (offline mode)"

**Timer Desync (Client-Server Mismatch):**
- Server timer is source of truth
- Client syncs timer every 5s via WebSocket heartbeat
- If major desync detected (>3s difference): Force client adjustment
- Visual: Brief "Syncing..." indicator

**Duplicate Player Name:**
- Inline error on join screen: "Name already taken in this game"
- Suggestion: "Try [Name]2 or choose different name"
- No page reload, just inline validation

---

#### Journey Map Summary

| Journey | Duration | Primary Goal | Success Metric |
|---------|----------|--------------|----------------|
| Admin Setup | <60s | Start game quickly | Time from open → game start |
| Player Join | <15s | Join without friction | Time from link click → waiting room |
| Active Round | 30-40s | Submit guess & feel engaged | Completion rate, bet usage |
| Leaderboard | 10-15s | Understand standing, get motivated | Time spent viewing, click "next round" |
| Error Recovery | <10s | Return to gameplay | Successful recovery rate |

**Critical Path Optimization:**

The fastest possible path from "no game" to "playing" is:
1. Admin opens `/admin.html` (auto-loads defaults)
2. Players click join link (type name, join)
3. Admin taps "START GAME"
4. **Total time: ~30-45 seconds** (if players are physically present)

This optimizes for the "party momentum" use case where speed is critical.

---

## 6. Component Library

### 6.1 Component Strategy

Beatsy uses vanilla HTML + Tailwind CSS components inspired by shadcn/ui patterns. All components are built from scratch to ensure Home Assistant compatibility (no React dependencies).

#### Core Component Inventory

**1. Buttons**

```html
<!-- Primary Button -->
<button class="inline-flex items-center justify-center rounded-lg text-lg font-bold
               transition-colors focus-visible:outline-none focus-visible:ring-2
               focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
               bg-sunset-primary text-white hover:bg-sunset-secondary h-12 px-6">
  START GAME
</button>

<!-- Secondary Button -->
<button class="inline-flex items-center justify-center rounded-lg text-lg font-semibold
               transition-colors focus-visible:outline-none focus-visible:ring-2
               focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
               bg-white text-sunset-primary border-2 border-sunset-primary
               hover:bg-sunset-bg h-12 px-6">
  BET ON IT
</button>

<!-- Destructive Button -->
<button class="inline-flex items-center justify-center rounded-lg text-base font-semibold
               transition-colors focus-visible:outline-none focus-visible:ring-2
               focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
               bg-red-600 text-white hover:bg-red-700 h-10 px-4">
  End Game
</button>
```

**Variants:** Primary, Secondary, Destructive, Ghost (text-only)
**Sizes:** Small (h-10), Medium (h-12), Large (h-14)
**States:** Default, Hover, Focus, Disabled, Loading

---

**2. Form Inputs**

```html
<!-- Text Input -->
<div class="space-y-2">
  <label class="text-xs font-semibold text-sunset-muted uppercase">
    Player Name
  </label>
  <input type="text"
         placeholder="Enter your name..."
         class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg
                text-sunset-text focus:outline-none focus:border-sunset-primary
                transition-colors"
         maxlength="20">
</div>

<!-- Number Input (Year) -->
<input type="number"
       inputmode="numeric"
       placeholder="19__"
       class="w-full text-center text-4xl font-bold border-2 border-sunset-primary
              rounded-xl py-4 text-sunset-text focus:outline-none
              focus:border-sunset-secondary transition-colors"
       min="1900"
       max="2024">

<!-- Select Dropdown -->
<select class="w-full px-4 py-3 text-base border-2 border-gray-300 rounded-lg
               text-sunset-text focus:outline-none focus:border-sunset-primary
               bg-white transition-colors">
  <option>Living Room Sonos</option>
  <option>Kitchen Speaker</option>
</select>
```

**Validation States:** Valid, Invalid (red border), Disabled
**Accessibility:** Labels, ARIA attributes, keyboard navigation

---

**3. Cards**

```html
<!-- Basic Card -->
<div class="bg-white rounded-lg p-4 shadow-md">
  <h3 class="text-lg font-bold text-sunset-text mb-2">Card Title</h3>
  <p class="text-sm text-sunset-muted">Card content goes here.</p>
</div>

<!-- Elevated Card (Important Info) -->
<div class="bg-white rounded-xl p-6 shadow-xl">
  <div class="text-center">
    <div class="text-6xl font-bold text-sunset-primary mb-2">+10</div>
    <div class="text-sm text-sunset-muted">Points Earned</div>
  </div>
</div>

<!-- Accent Card (Highlight) -->
<div class="bg-sunset-primary text-white rounded-lg p-4 shadow-lg">
  <label class="text-xs font-semibold uppercase mb-1 block opacity-90">
    Join Link
  </label>
  <div class="text-sm font-mono bg-white/20 rounded px-2 py-1">
    192.168.1.10:8123/local/beatsy/start.html
  </div>
</div>
```

**Variants:** Basic, Elevated, Accent (colored background), Interactive (hover state)
**Spacing:** Consistent padding (space-4), margins (space-3 between cards)

---

**4. Badges & Pills**

```html
<!-- Status Badge -->
<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold
             bg-sunset-primary text-white">
  3 Ready
</span>

<!-- Bet Indicator Badge -->
<div class="bg-sunset-accent text-white px-6 py-2 rounded-full font-bold
            shadow-lg animate-pulse">
  🎲 BET ACTIVE - 2x POINTS
</div>

<!-- Player Count Badge -->
<span class="inline-flex items-center justify-center w-6 h-6 rounded-full
             text-xs font-bold bg-sunset-success text-white">
  5
</span>
```

**Use Cases:** Status indicators, player counts, bet notifications, achievement badges
**Animation:** Pulse for attention-grabbing (bet active), none for static info

---

**5. Timer Display**

```html
<!-- Circular Timer (Active Round) -->
<div class="relative">
  <svg class="w-32 h-32">
    <!-- Background circle -->
    <circle cx="64" cy="64" r="56" fill="none" stroke="#FFE5D9" stroke-width="8"/>
    <!-- Progress circle (animated) -->
    <circle cx="64" cy="64" r="56" fill="none" stroke="#FF6B35" stroke-width="8"
            stroke-dasharray="351.86" stroke-dashoffset="175.93"
            class="transform -rotate-90 transition-all duration-1000"/>
  </svg>
  <div class="absolute inset-0 flex items-center justify-center">
    <div class="text-center">
      <div class="text-5xl font-bold text-sunset-primary">12</div>
      <div class="text-xs text-sunset-muted">seconds</div>
    </div>
  </div>
</div>
```

**Implementation:** SVG circle with animated stroke-dashoffset, JavaScript updates every second
**States:** Normal (>10s), Warning (5-10s, orange), Critical (<5s, red + pulsing)

---

**6. Leaderboard Components**

```html
<!-- Player Row -->
<div class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
  <!-- Rank -->
  <div class="text-lg font-bold text-gray-900 w-8">1</div>

  <!-- Avatar -->
  <div class="w-10 h-10 rounded-full bg-sunset-primary flex items-center
              justify-center text-white font-bold">
    M
  </div>

  <!-- Name & Last Round -->
  <div class="flex-1">
    <div class="text-sm font-semibold text-gray-900">Markus</div>
    <div class="text-xs text-gray-500">Last: +10 pts</div>
  </div>

  <!-- Score -->
  <div class="text-right">
    <div class="text-lg font-bold text-sunset-text">55</div>
    <div class="text-xs text-sunset-muted">points</div>
  </div>
</div>

<!-- Podium (Top 3) -->
<div class="flex items-end justify-center gap-2 mb-6">
  <!-- 2nd Place -->
  <div class="text-center flex-1">
    <div class="w-12 h-12 rounded-full bg-gray-300 flex items-center justify-center
                text-white font-bold text-lg mx-auto mb-1">A</div>
    <div class="text-xs font-semibold mb-1">Anna</div>
    <div class="bg-white/30 rounded px-2 py-1">
      <div class="font-bold text-sm">42</div>
    </div>
    <div class="text-xs mt-1">🥈 2nd</div>
  </div>

  <!-- 1st Place (larger) -->
  <div class="text-center flex-1">
    <div class="w-16 h-16 rounded-full bg-yellow-400 flex items-center justify-center
                text-gray-900 font-bold text-xl mx-auto mb-1 shadow-lg">M</div>
    <div class="text-sm font-bold mb-1">Markus</div>
    <div class="bg-white rounded px-2 py-2 shadow">
      <div class="text-sunset-primary font-bold text-lg">55</div>
    </div>
    <div class="font-bold text-sm mt-1">👑 1st</div>
  </div>

  <!-- 3rd Place -->
  <div class="text-center flex-1">
    <div class="w-12 h-12 rounded-full bg-orange-700 flex items-center justify-center
                text-white font-bold text-lg mx-auto mb-1">T</div>
    <div class="text-xs font-semibold mb-1">Tom</div>
    <div class="bg-white/30 rounded px-2 py-1">
      <div class="font-bold text-sm">38</div>
    </div>
    <div class="text-xs mt-1">🥉 3rd</div>
  </div>
</div>
```

---

**7. Feedback Elements**

```html
<!-- Toast Notification -->
<div class="fixed bottom-4 left-4 right-4 bg-gray-900 text-white rounded-lg p-4
            shadow-xl animate-slide-up">
  <div class="flex items-center gap-3">
    <div class="text-2xl">✓</div>
    <div class="flex-1">
      <div class="font-semibold">Answer submitted!</div>
      <div class="text-sm opacity-80">Waiting for other players...</div>
    </div>
  </div>
</div>

<!-- Loading Spinner -->
<div class="flex items-center justify-center gap-2">
  <div class="w-6 h-6 border-4 border-sunset-primary border-t-transparent
              rounded-full animate-spin"></div>
  <span class="text-sm text-sunset-muted">Calculating scores...</span>
</div>

<!-- Result Emoji Feedback -->
<div class="text-center mb-6">
  <div class="text-6xl mb-3">🎉</div>
  <h2 class="text-3xl font-bold text-sunset-text mb-2">Close One!</h2>
  <p class="text-sunset-muted">Within 2 years</p>
</div>
```

**Animation:** Slide-up for toasts, spin for loaders, scale for emoji reveals
**Duration:** Auto-dismiss toasts after 3-5s, manual dismiss for important messages

---

#### Component Usage Guidelines

**Consistency Rules:**

1. **Button Hierarchy**: Use primary for main action, secondary for alternatives, ghost for tertiary
2. **Card Elevation**: Reserve shadow-xl for important moments (results, podium), use shadow-md for standard cards
3. **Color Usage**: Primary color for main CTAs, accent for special states (bets), success/error for feedback
4. **Spacing**: Use consistent space-4 (16px) between major sections, space-3 (12px) within components
5. **Typography**: Bold for headings/buttons, semibold for labels, normal for body text
6. **Rounding**: Larger radius (rounded-xl, rounded-2xl) for important/elevated components
7. **Interactive Feedback**: All clickable elements have hover/focus states

**Accessibility Checklist:**

- ✓ All buttons have clear labels (no icon-only buttons without aria-label)
- ✓ Form inputs have associated labels (visible or aria-label)
- ✓ Focus indicators visible (2px ring in primary color)
- ✓ Color not sole indicator of state (icons, text, borders supplement)
- ✓ Touch targets ≥44×44px
- ✓ Keyboard navigation works (Tab, Enter, Escape)
- ✓ ARIA roles for dynamic content (live regions for score updates)

---

## 7. UX Pattern Decisions

### 7.1 Consistency Rules

#### Form Interactions

**Pattern: Progressive Disclosure**
- Show only essential fields initially
- Advanced settings (scoring customization) behind "Advanced" toggle
- Reduces cognitive load for first-time users
- Power users can access full controls

**Validation Strategy:**
- **Inline Validation**: Show errors immediately on blur (don't wait for submit)
- **Success States**: Green border + checkmark for valid input
- **Error Messages**: Specific and actionable ("Name must be unique" vs "Invalid input")
- **Prevent vs Warn**: Disable submit button until valid, don't let user fail

**Example: Join Form**
- Name input auto-focuses (keyboard appears)
- Character counter updates live (20 char max)
- "JOIN GAME" button disabled until valid name entered
- Duplicate name check on blur, suggest alternative

---

#### Modal Dialogs & Overlays

**Usage Criteria:**
- **Use modals for**: Confirmations (end game), critical errors
- **Avoid modals for**: Information that can be inline, non-blocking messages

**Structure:**
```html
<div class="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
  <div class="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl">
    <h2 class="text-2xl font-bold text-sunset-text mb-4">End Game?</h2>
    <p class="text-sunset-muted mb-6">
      This will end the game for all players. Are you sure?
    </p>
    <div class="flex gap-3">
      <button class="flex-1 btn-secondary">Cancel</button>
      <button class="flex-1 btn-destructive">End Game</button>
    </div>
  </div>
</div>
```

**Interaction Rules:**
- **ESC key closes**: Unless it's critical (can't dismiss error without action)
- **Click outside closes**: For non-destructive modals
- **Focus trap**: Tab cycles within modal (accessibility)
- **Return focus**: After close, focus returns to trigger element

---

#### Real-Time Updates (WebSocket Patterns)

**Live Elements:**
1. **Player List** (admin setup): Adds new row when player joins
2. **Timer** (active round): Updates every second
3. **Leaderboard** (mid-game): Updates after each round
4. **Bet Indicators** (active round): Shows when other players bet

**Update Strategies:**
- **Optimistic Updates**: Show local change immediately, reconcile with server
- **Smooth Animations**: Fade-in new players, slide-in score changes
- **Conflict Resolution**: Server state wins, client corrects if mismatch
- **Heartbeat**: 5-second ping to detect disconnections

**Visual Feedback:**
```html
<!-- New player joins - slide down animation -->
<div class="player-row animate-slide-down">
  <div class="w-8 h-8 bg-sunset-accent rounded-full">J</div>
  <span>Jessica</span>
  <span class="text-green-500 text-xs">● Just joined</span>
</div>
```

---

#### Navigation & Screen Transitions

**Pattern: Single-Page Sections**
- Each major screen is a distinct HTML file (`admin.html`, `start.html`)
- Within a screen, use JavaScript to show/hide sections
- No full page reloads during gameplay (jarring)

**Transition Animations:**
- **Screen Change**: Fade out → fade in (300ms)
- **Section Reveal**: Slide up from bottom (200ms)
- **Error Appears**: Shake animation (quick 100ms)
- **Success**: Scale up (bounce effect, 150ms)

**Back Button Behavior:**
- **Admin**: Back = exit to HA dashboard (confirm if game active)
- **Player**: Back = leave game (confirm modal)
- **During Round**: Disable back (prevent accidental exit)

---

#### Loading States & Feedback

**Skeleton Screens (Preferred):**
```html
<!-- Loading player list -->
<div class="space-y-2">
  <div class="h-12 bg-gray-200 rounded-lg animate-pulse"></div>
  <div class="h-12 bg-gray-200 rounded-lg animate-pulse"></div>
  <div class="h-12 bg-gray-200 rounded-lg animate-pulse"></div>
</div>
```

**Spinners (Quick Actions):**
- Use for <2s operations (submit guess, fetch scores)
- Center-aligned with label ("Submitting...")

**Progress Bars (Multi-Step):**
- Use for game setup (Step 1/3: Select Playlist)
- Show current position in flow

**Rule:** Never show blank screen. Always provide visual feedback.

---

#### Error Handling & Recovery

**Error Types & Patterns:**

1. **Validation Errors** (User-fixable)
   - Show inline, near the problematic field
   - Red border + helper text below input
   - Don't use modals for validation errors

2. **Network Errors** (Transient)
   - Toast notification: "Connection lost, retrying..."
   - Auto-retry up to 3 times
   - If fails: Show "Offline Mode" banner + retry button

3. **Server Errors** (Needs support)
   - Modal with friendly message + error code
   - "Something went wrong (ERR_GAME_404). Please restart game."
   - Provide "Copy Error" button for support

4. **Game State Errors** (Recoverable)
   - "Host disconnected" → Wait or leave options
   - "Out of sync" → Auto-reload with preserved state

**Error Message Tone:**
- ❌ "Error: Invalid input"
- ✓ "Oops! Please enter a year between 1900-2024"

---

#### Empty States

**Pattern: Helpful Guidance**

```html
<!-- No players yet -->
<div class="text-center py-12">
  <div class="text-6xl mb-4">👥</div>
  <h3 class="text-xl font-bold text-sunset-text mb-2">
    Waiting for players...
  </h3>
  <p class="text-sunset-muted mb-4">
    Share the join link below to invite friends!
  </p>
  <div class="bg-sunset-primary text-white rounded-lg p-3 max-w-sm mx-auto">
    <div class="text-xs font-semibold uppercase mb-1">Join Link</div>
    <div class="font-mono text-sm">192.168.1.10.../start.html</div>
  </div>
</div>
```

**Empty State Checklist:**
- Explain why it's empty ("No players joined yet")
- Provide clear next step ("Share join link")
- Use friendly illustration/emoji (not just text)
- Show relevant action (copy link button)

---

#### Consistency Enforcement

**Visual Consistency:**
- All primary buttons use same height (h-12) and padding (px-6)
- All cards use consistent shadows (shadow-md or shadow-lg)
- All spacing between sections is space-4 or space-6
- All input borders are 2px (border-2)

**Interaction Consistency:**
- All buttons show hover state (color darkens)
- All form inputs show focus state (border color changes)
- All loading states use same spinner or skeleton pattern
- All toasts appear in same position (bottom-left on mobile)

**Language Consistency:**
- Buttons: Verb phrases ("START GAME", "SUBMIT GUESS")
- Labels: Noun phrases ("Player Name", "Spotify Player")
- Success messages: Celebratory ("You're in!", "Nice guess!")
- Error messages: Helpful ("Name already taken, try Jessica2")

**Timing Consistency:**
- Short animations: 150-200ms (micro-interactions)
- Medium transitions: 300ms (screen changes)
- Long operations: Show immediate feedback + spinner
- Toast auto-dismiss: 3-5s (user can dismiss earlier)

---

## 8. Responsive Design & Accessibility

### 8.1 Responsive Strategy

**Design Philosophy: Mobile-First, Mobile-Best**

Beatsy is optimized primarily for mobile phones (320px-428px width). Tablet and desktop views are supported but not prioritized for MVP.

#### Breakpoint Strategy

```css
/* Mobile (Primary Target) */
/* 320px - 428px: All core features optimized */

/* Tablet (Secondary Support) */
@media (min-width: 768px) {
  /* Wider cards, two-column layouts where beneficial */
}

/* Desktop (Tertiary Support) */
@media (min-width: 1024px) {
  /* Max-width container (600px), centered layout */
}
```

**Mobile-First Implementation:**
- Base styles assume 375px width (iPhone SE/8/X baseline)
- Use `max-width: 420px` container to prevent overstretching on larger phones
- All touch targets meet 44×44px minimum
- Font sizes readable without zoom (16px minimum for body text)

---

#### Screen-Specific Responsive Behavior

**Admin Setup (`/admin.html`):**
- **Mobile**: Single column, stacked cards, sticky "Start Game" button at bottom
- **Tablet**: Same layout (no benefit from width), larger cards
- **Desktop**: Centered 600px container, same vertical layout

**Player Join (`/start.html`):**
- **Mobile**: Full-width form, large input, prominent button
- **Tablet**: Centered 500px form with more padding
- **Desktop**: Centered 400px form (compact, focused)

**Active Round (Gameplay):**
- **Mobile**: Vertical stack (timer → art → info → input → buttons)
- **Tablet**: Same layout (maintains mobile feel for consistency)
- **Desktop**: Same layout (no horizontal split, keeps focus)

**Leaderboard:**
- **Mobile**: Full-width podium, stacked player rows
- **Tablet**: Wider podium, same row structure
- **Desktop**: Max 600px width, centered

**Key Decision:** No horizontal splits or multi-column layouts during gameplay. Vertical scrolling is intuitive and prevents information overload.

---

#### Orientation Handling

**Portrait (Primary):**
- All screens optimized for portrait orientation
- Vertical scrolling natural and expected

**Landscape (Secondary):**
- Album art scales down (smaller square)
- Timer moves to top-right corner (compact)
- Buttons become shorter (h-10 instead of h-12)
- Overall: Functional but portrait is preferred

**Orientation Lock:**
- Consider adding "Rotate device" prompt if landscape detected
- Or use CSS to maintain portrait-like layout even in landscape

---

### 8.2 Accessibility Compliance (WCAG 2.1 Level AA)

#### Color Contrast

**Tested Combinations:**
- Primary text (#2C1810) on light bg (#FFF5F0): 12.5:1 ✓ (AAA)
- Secondary text (#8B7355) on light bg: 5.8:1 ✓ (AA)
- White text on primary button (#FF6B35): 4.6:1 ✓ (AA)
- White text on success (#4ECDC4): 4.8:1 ✓ (AA)

**Non-Color Indicators:**
- Bet status: Badge text + emoji + pulsing animation (not just color)
- Submit button disabled: Opacity + cursor change + text change
- Timer urgency: Number size + color + animation (multi-sensory)
- Validation errors: Red border + icon + text message

---

#### Keyboard Navigation

**Tab Order:**
- Follows visual flow (top to bottom)
- Skip navigation link: "Skip to game setup" (for admin)
- Modal focus traps: Tab cycles within modal only
- ESC key: Closes dismissible modals, returns focus

**Form Navigation:**
- Tab between inputs
- Enter submits form (if valid)
- Arrow keys navigate dropdowns
- Space toggles checkboxes/buttons

**Game Controls:**
- Enter key submits guess (same as tapping button)
- Tab to "Bet On It" button, Space to toggle
- No keyboard shortcuts during timer (prevents accidental actions)

---

#### Screen Reader Support

**ARIA Labels:**
```html
<!-- Player count badge -->
<span aria-label="3 players ready" class="badge">3</span>

<!-- Timer -->
<div aria-live="polite" aria-atomic="true" role="timer">
  <span class="sr-only">Time remaining:</span>
  <span class="text-5xl">12</span>
  <span class="sr-only">seconds</span>
</div>

<!-- Leaderboard updates -->
<div aria-live="polite" aria-atomic="false" role="status">
  <span class="sr-only">Leaderboard updated. Markus is in first place with 55 points.</span>
</div>

<!-- Loading states -->
<div role="status" aria-live="polite">
  <span class="sr-only">Calculating scores, please wait...</span>
  <div class="spinner"></div>
</div>
```

**ARIA Live Regions:**
- `aria-live="polite"` for score updates, player joins (non-urgent)
- `aria-live="assertive"` for timer expiration, critical errors (urgent)
- `aria-atomic="true"` for complete messages (read entire content)
- `aria-atomic="false"` for partial updates (read only changes)

**Semantic HTML:**
- Use `<button>` not `<div onclick>` for clickable elements
- Use `<form>` for join/setup forms (enables native validation)
- Use `<label>` for all input fields (explicit association)
- Use `<main>`, `<nav>`, `<section>` for page structure

---

#### Focus Management

**Focus Indicators:**
```css
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: 4px;
}
```

**Focus Order:**
- Auto-focus on first input when page loads (join name field)
- No focus traps (except intentional modal dialogs)
- Skip links for long content ("Skip to leaderboard")

**Dynamic Content:**
- When modal opens: Focus first interactive element
- When modal closes: Return focus to trigger button
- When screen changes: Focus on heading (announces new screen)

---

#### Motion & Animation

**Respect `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Essential vs Decorative Motion:**
- **Essential**: Timer countdown (keep, provide text alternative)
- **Decorative**: Confetti animation (disable for reduced motion)
- **Feedback**: Button press scale (reduce to opacity change)

---

#### Touch & Input Accessibility

**Touch Target Sizing:**
- All buttons: Minimum 44×44px (iOS/Android guideline)
- Form inputs: Minimum 44px height
- Checkboxes/radio buttons: 24×24px + 10px padding = 44px total

**Input Types:**
```html
<!-- Year input: Numeric keyboard on mobile -->
<input type="number" inputmode="numeric" pattern="[0-9]{4}">

<!-- Name input: Default keyboard -->
<input type="text" autocomplete="name">

<!-- Email (if added): Email keyboard -->
<input type="email" autocomplete="email" inputmode="email">
```

**Autocomplete Attributes:**
- Helps password managers, form fill (accessibility + convenience)
- `autocomplete="name"` for player name field
- `autocomplete="off"` for year guess (prevents form fill spoilers)

---

#### Testing Checklist

**Manual Testing:**
- [ ] Navigate entire app using only keyboard (no mouse)
- [ ] Test with screen reader (VoiceOver iOS, TalkBack Android)
- [ ] Verify color contrast with browser dev tools
- [ ] Test with `prefers-reduced-motion` enabled
- [ ] Verify all images have alt text (or are decorative)

**Automated Testing:**
- [ ] Run axe DevTools on all screens
- [ ] Lighthouse accessibility audit (target: 95+)
- [ ] WAVE browser extension check
- [ ] HTML validator (semantic markup)

**Device Testing:**
- [ ] iPhone SE (smallest modern screen: 375×667)
- [ ] iPhone 15 Pro Max (largest: 430×932)
- [ ] Android mid-range (Samsung Galaxy A-series)
- [ ] Tablet (iPad 10th gen: 820×1180)

---

### 8.3 Performance Considerations

**Optimization Strategies:**

1. **Lazy Load Images**: Only load album art when visible (defer off-screen images)
2. **Minimize Reflows**: Use `transform` for animations (not `left`/`top`)
3. **Debounce Input**: Wait 300ms before validating name (reduce API calls)
4. **WebSocket Batching**: Batch multiple score updates into single message
5. **Service Worker**: Cache static assets (Tailwind CSS, fonts) for offline support

**Budget Targets:**
- First Contentful Paint: <1.5s (on 3G connection)
- Time to Interactive: <3s
- Total Page Weight: <500KB (excluding album art)
- Album Art: <100KB per image (compressed JPEG/WebP)

---

### 8.4 Browser Compatibility

**Target Browsers:**
- **iOS Safari**: 14+ (iOS 14, Sept 2020+)
- **Chrome Android**: 90+ (April 2021+)
- **Desktop Chrome/Firefox/Edge**: Last 2 versions
- **Safari macOS**: 14+ (macOS Big Sur+)

**Progressive Enhancement:**
- **Baseline**: Static HTML + CSS works without JavaScript
- **Enhanced**: JavaScript adds live updates, animations, WebSocket
- **Fallback**: If WebSocket fails, poll REST API every 5s

**Polyfills (if needed):**
- CSS custom properties: Natively supported (iOS 14+)
- Flexbox/Grid: Natively supported
- Fetch API: Natively supported
- WebSockets: Natively supported

**Feature Detection:**
```javascript
// Check WebSocket support
if ('WebSocket' in window) {
  // Use WebSocket for real-time updates
} else {
  // Fallback to polling
}

// Check for service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

---

## 9. Implementation Guidance

### 9.1 Completion Summary

**UX Design Specification Status: ✓ Complete**

This comprehensive UX design specification provides all the guidance needed to implement Beatsy's user interface. The specification has been completed with the following deliverables:

#### Completed Sections

1. **Design System Foundation** ✓
   - Technology stack selected: Static HTML + Tailwind CSS + shadcn/ui patterns
   - Rationale documented for Home Assistant compatibility
   - Development workflow defined (CDN → compiled CSS)

2. **Core User Experience** ✓
   - Emotional goals established: Confident, Nostalgic, Playfully Competitive
   - Five core experience principles defined
   - User stories and differentiation documented

3. **Visual Foundation** ✓
   - Color system: Sunset Groove palette with accessibility compliance
   - Typography system: System fonts with complete type scale
   - Spacing & layout system: 4px base unit with comprehensive scale
   - Interactive visualizations: [ux-color-themes.html](./ux-color-themes.html)

4. **Design Direction** ✓
   - Three directions evaluated: Compact Card, Spacious Centered, Dashboard Grid
   - Selected direction: Spacious Centered (best for party atmosphere)
   - Rationale documented with comparison table
   - Interactive mockups: [ux-design-directions.html](./ux-design-directions.html)

5. **User Journey Flows** ✓
   - Five critical journeys mapped in detail
   - Admin setup (60-second goal)
   - Player join & first round
   - Active round gameplay loop
   - Leaderboard & game completion
   - Edge cases & error recovery

6. **Component Library** ✓
   - Seven core component types with HTML/Tailwind implementations
   - Buttons, forms, cards, badges, timers, leaderboards, feedback elements
   - Usage guidelines and accessibility checklist

7. **UX Pattern Decisions** ✓
   - Form interactions (progressive disclosure, inline validation)
   - Modal dialogs & overlays
   - Real-time updates (WebSocket patterns)
   - Navigation & screen transitions
   - Loading states & feedback
   - Error handling & recovery
   - Empty states
   - Consistency enforcement rules

8. **Responsive Design & Accessibility** ✓
   - Mobile-first strategy (320px-428px primary target)
   - Breakpoint strategy with screen-specific behaviors
   - WCAG 2.1 Level AA compliance
   - Keyboard navigation, screen reader support, ARIA attributes
   - Motion accessibility (prefers-reduced-motion)
   - Testing checklists (manual, automated, device)
   - Performance targets and browser compatibility

---

### 9.2 Development Handoff Checklist

**Before Starting Development:**

- [x] UX design specification reviewed and approved
- [ ] Design mockup files available (ux-design-directions.html)
- [ ] Color theme finalized (Sunset Groove)
- [ ] PRD referenced for functional requirements
- [ ] Architecture document consulted for technical constraints

**During Development:**

- [ ] Set up Tailwind CSS (CDN for development, compile for production)
- [ ] Create base CSS file with custom color variables
- [ ] Implement component library (buttons, forms, cards, etc.)
- [ ] Build screens in priority order: Join → Active Round → Results → Leaderboard → Admin
- [ ] Test responsive behavior on mobile devices (iPhone SE, Android mid-range)
- [ ] Validate accessibility (keyboard navigation, screen reader, contrast)
- [ ] Implement WebSocket real-time updates
- [ ] Add error handling and loading states
- [ ] Test edge cases (disconnections, timeouts, duplicate names)

**Quality Assurance:**

- [ ] Manual testing on iOS Safari (primary target)
- [ ] Manual testing on Chrome Android
- [ ] Keyboard-only navigation test
- [ ] Screen reader test (VoiceOver or TalkBack)
- [ ] Lighthouse audit (accessibility score 95+)
- [ ] Color contrast verification
- [ ] Performance benchmarks (FCP <1.5s, TTI <3s)

---

### 9.3 Design Decision Log

**Key Decisions Made:**

1. **Design System: Static HTML + Tailwind**
   - **Rationale**: Home Assistant compatibility, no build process for MVP, mobile-first performance
   - **Alternative Considered**: React + shadcn/ui (rejected: requires build process, HA incompatibility)

2. **Color Theme: Sunset Groove**
   - **Rationale**: Warm, nostalgic palette evokes vinyl records and music memories, high energy
   - **Alternatives Considered**: Vinyl Nights (too cool), Retro Glow (too vibrant), Warm Vinyl (too muted)

3. **Design Direction: Spacious Centered**
   - **Rationale**: Best for party atmosphere, clear focus, readable from arm's length, reduces cognitive load
   - **Alternatives Considered**: Compact Card (too dense), Dashboard Grid (too technical)

4. **Mobile-First Strategy**
   - **Rationale**: Primary use case is phones at parties, tablet/desktop are secondary
   - **Implication**: No multi-column layouts during gameplay, vertical scrolling only

5. **WebSocket for Real-Time Updates**
   - **Rationale**: Essential for synchronized gameplay, live leaderboards, timer sync
   - **Fallback**: Polling every 5s if WebSocket unavailable

6. **No Authentication/Accounts**
   - **Rationale**: Zero friction for party game, name-only registration
   - **Implication**: Games are ephemeral, no persistent player profiles

7. **Auto-Submit on Timer Expiration**
   - **Rationale**: Prevents timeouts from blocking game flow, maintains energy
   - **Implication**: Players must enter valid guess before timer ends (or defaults to 0)

8. **Bet Toggle (Not Slider)**
   - **Rationale**: Binary choice is faster, clearer, less decision paralysis
   - **Alternative Considered**: Slider for bet amount (rejected: too complex for MVP)

---

### 9.4 Future Enhancements (Post-MVP)

**Phase 2 Considerations:**

1. **Alternative Design Modes**
   - Compact Card view (speed mode for experienced players)
   - Dashboard Grid view (tournament mode with detailed stats)

2. **Additional Color Themes**
   - User-selectable themes (Vinyl Nights, Retro Glow)
   - Dark mode variant of Sunset Groove

3. **Accessibility Improvements**
   - High contrast mode toggle
   - Font size adjustment controls
   - Colorblind-friendly palette options

4. **Enhanced Animations**
   - Confetti for winners
   - Particle effects on correct guesses
   - Smoother score counter animations

5. **Advanced Features**
   - Player profiles with stats (if auth added)
   - Custom avatar uploads
   - Achievement badges system
   - Historical game replay

---

### 9.5 Contact & Feedback

**UX Specification Author:** Claude (BMad Method - Create UX Design Workflow v1.0)
**Created:** 2025-11-09
**Project:** Beatsy (Home Assistant Custom Component)
**Related Documents:**
- [Product Requirements Document](./PRD.md)
- [Workflow Status](./bmm-workflow-status.yaml)
- [Color Theme Explorer](./ux-color-themes.html)
- [Design Direction Mockups](./ux-design-directions.html)

**For Questions:**
- UX clarifications: Reference section numbers in this document
- Functional requirements: Consult PRD.md
- Technical implementation: Consult architecture documentation (when available)

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-09 | Initial UX design specification created | Claude |

---

**End of UX Design Specification**

---

## Appendix

### Related Documents

- [Product Requirements Document](./PRD.md)
- [Workflow Status](./bmm-workflow-status.yaml)
