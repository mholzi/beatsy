# DashView - Modern Home Assistant Dashboard

A modern React-based dashboard for Home Assistant with centralized card management and flexible room configuration via admin panel.

## Project Status

**Current Phase**: Phase 0 - Proof of Concept (POC)
**Status**: In Development
**Start Date**: 2025-11-10

See [MIGRATION_PLAN.md](./MIGRATION_PLAN.md) for detailed migration strategy and task list.

## Architecture

```
dashview/
├── frontend/          # React + TypeScript + Vite
├── backend/           # Node.js + Express + TypeScript
├── database/          # PostgreSQL schema and migrations
├── docker/            # Docker configurations
└── docs/              # Documentation
```

## Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **HA Integration**: @hakit/core + @hakit/components
- **Styling**: Tailwind CSS + shadcn/ui (to be added)
- **State Management**: Zustand + TanStack Query (to be added)

### Backend
- **Runtime**: Node.js + TypeScript
- **Framework**: Express
- **Database**: PostgreSQL (to be added)
- **ORM**: Prisma/TypeORM (to be decided)

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Home Assistant instance running
- Long-lived access token from Home Assistant

### Development Setup

#### 1. Backend Setup

```bash
cd dashview/backend

# Copy environment template
cp .env.example .env

# Edit .env with your Home Assistant URL and token
# HA_URL=http://homeassistant.local:8123
# HA_TOKEN=your_token_here

# Install dependencies (already done)
npm install

# Start development server
npm run dev
```

Backend will run on `http://localhost:3001`

#### 2. Frontend Setup

```bash
cd dashview/frontend

# Install dependencies (already done)
npm install

# Start development server
npm run dev
```

Frontend will run on `http://localhost:5173`

### Testing the Setup

1. **Backend Health Check**:
   ```bash
   curl http://localhost:3001/health
   ```
   Should return: `{"status":"ok","timestamp":"..."}`

2. **Frontend**: Open `http://localhost:5173` in browser

## Development Workflow

### Project Setup (M0.1 - M0.7) ✅
- [x] M0.1: Directory structure created
- [x] M0.2: Using existing HA_Dashboard repo
- [x] M0.3: .gitignore configured
- [x] M0.4: Frontend initialized (Vite + React + TypeScript)
- [x] M0.5: Backend initialized (Express + TypeScript)
- [x] M0.6: ESLint + Prettier configured
- [x] M0.7: Development documentation created

### Next Steps (M0.8 - M0.13): Home Assistant Integration
- [ ] M0.8: Install @hakit/core and @hakit/components
- [ ] M0.9: Create HA connection service
- [ ] M0.10: Implement authentication flow
- [ ] M0.11: Test WebSocket connection
- [ ] M0.12: Create useHomeAssistant hook
- [ ] M0.13: Test reading entity states

### Git Workflow

**Branching Strategy**: Development on `main` branch (no separate branches for POC)

**Commit Convention**:
```bash
[DashView] M0.X: Brief description

# Example:
git add .
git commit -m "[DashView] M0.8: Add @hakit/core integration"
```

## Code Quality

### Linting

```bash
# Backend
cd backend
npm run lint      # (to be added)

# Frontend
cd frontend
npm run lint      # (to be added)
```

### Formatting

Both frontend and backend use Prettier for consistent code formatting:
- Single quotes
- 2-space indentation
- 100 character line width
- Semicolons enabled

## Environment Variables

### Backend (.env)

```env
# Server
PORT=3001

# Home Assistant
HA_URL=http://homeassistant.local:8123
HA_TOKEN=your_long_lived_access_token_here

# Database (future phases)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dashview
DB_USER=dashview
DB_PASSWORD=your_password_here
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:3001
VITE_HA_URL=http://homeassistant.local:8123
```

## Project Structure

### Backend Structure (Current)
```
backend/
├── src/
│   └── index.ts           # Express server entry point
├── .env.example           # Environment template
├── .eslintrc.json         # ESLint configuration
├── .prettierrc            # Prettier configuration
├── tsconfig.json          # TypeScript configuration
└── package.json           # Dependencies and scripts
```

### Frontend Structure (Current)
```
frontend/
├── src/
│   ├── App.tsx            # Main React component
│   ├── main.tsx           # React entry point
│   └── vite-env.d.ts      # Vite type definitions
├── .eslintrc.json         # ESLint configuration
├── .prettierrc            # Prettier configuration
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite configuration
└── package.json           # Dependencies and scripts
```

## Resources

- [Migration Plan](./MIGRATION_PLAN.md) - Detailed migration strategy
- [@hakit Documentation](https://github.com/shannonhochkins/ha-component-kit)
- [Home Assistant API](https://www.home-assistant.io/integrations/api/)
- [React 19 Docs](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)

## Coexistence with Existing Dashboard

The new DashView system runs **in parallel** with the existing Lovelace-gen dashboard:

- **Existing Dashboard**: `home-assistant-config/` (untouched, continues working)
- **New Dashboard**: `dashview/` (new development)
- Both connect to the same Home Assistant instance
- No disruption to current operations

## Getting Help

- **Issues**: GitHub Issues with `dashview` label
- **Milestone**: `DashView Migration`
- **Documentation**: See `docs/MIGRATION_PLAN.md`

## License

[To be determined]

---

**Status**: Phase 0 (POC) - Project Setup Complete ✅
**Next**: Home Assistant Integration (M0.8 - M0.13)
