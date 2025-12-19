# Karigar Frontend

A modern, responsive frontend for the Karigar hyperlocal services marketplace built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🎨 **Modern UI/UX** - Clean, professional design with Tailwind CSS
- 🔐 **Authentication** - JWT-based auth with role-based access control
- 👥 **Multi-role Support** - Customer, Provider, and Admin portals
- 🔍 **Search & Discovery** - Find service providers with filters and location-based search
- 📱 **Responsive Design** - Mobile-first approach with excellent mobile experience
- ⚡ **Performance** - Optimized with Next.js App Router and code splitting
- 🎯 **Type Safety** - Full TypeScript implementation
- 🎨 **Component Library** - Reusable UI components built with Radix UI

## Tech Stack

- **Framework:** Next.js 14+ (App Router)
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS + Custom CSS Variables
- **UI Components:** Radix UI + Custom components
- **State Management:** Zustand with persistence
- **Forms:** React Hook Form + Zod validation
- **Icons:** Lucide React
- **Animations:** Framer Motion
- **Notifications:** Sonner

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_key_here
NEXT_PUBLIC_APP_NAME=Karigar
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication routes
│   ├── (customer)/        # Customer portal routes
│   ├── (provider)/        # Provider portal routes
│   ├── (admin)/           # Admin dashboard routes
│   └── layout.tsx         # Root layout
├── components/
│   ├── ui/                # Base UI components
│   ├── layout/           # Layout components
│   ├── auth/             # Auth components
│   ├── customer/         # Customer-specific components
│   ├── provider/         # Provider-specific components
│   ├── admin/            # Admin-specific components
│   └── shared/           # Shared components
├── lib/
│   ├── api/              # API client modules
│   └── utils/            # Utility functions
├── stores/               # Zustand state stores
├── hooks/                # Custom React hooks
└── types/                # TypeScript type definitions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Key Features

### Authentication
- Login/Registration for Customers and Providers
- JWT token management
- Protected routes with middleware
- Role-based access control

### Customer Portal
- Dashboard with booking overview
- Search and discover providers
- View provider profiles
- Create and manage bookings
- Review and rate services

### Provider Portal
- Dashboard with booking requests
- Service management
- Booking management
- Availability calendar
- Reviews and ratings
- Analytics dashboard

### Admin Dashboard
- User management
- Provider approval workflow
- Booking oversight
- Review moderation
- Dispute resolution
- Platform analytics

## Design System

The app uses a comprehensive design system with:
- Custom color palette (primary, secondary, role-specific accents)
- Typography scale (Inter font family)
- Spacing system (Tailwind scale)
- Border radius variants
- Shadow elevation system
- Animation patterns

## API Integration

The frontend communicates with the backend API through:
- Base API client with authentication
- Error handling and retry logic
- Request/response interceptors
- Type-safe API modules

## Contributing

1. Follow the existing code structure
2. Maintain TypeScript strict mode
3. Use the design system components
4. Write accessible, semantic HTML
5. Test on mobile devices

## License

Private - All rights reserved
