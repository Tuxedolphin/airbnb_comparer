# Airbnb Comparer - React TypeScript Frontend

This is the modern React TypeScript frontend for the Airbnb Comparer application, integrated with Python Eel for desktop app functionality.

## Features

- ✅ **Modern React + TypeScript**: Type-safe component development
- ✅ **Vite**: Fast development server and optimized builds
- ✅ **Eel Integration**: Seamless communication with Python backend
- ✅ **Responsive Design**: Works on desktop and mobile devices
- ✅ **Component-based Architecture**: Modular and maintainable code

## Project Structure

```
src/
├── components/          # React components
│   ├── ColumnSelector.tsx
│   ├── ListingTable.tsx
│   ├── AddListingModal.tsx
│   └── TableCells.tsx
├── services/           # Service layers
│   └── eel.ts         # Eel integration service
├── types/             # TypeScript type definitions
│   └── listing.ts     # Listing data types
├── App.tsx            # Main application component
├── App.css            # Application styles
└── main.tsx          # Application entry point
```

## Development

### Prerequisites

- Node.js 18+ and pnpm
- Python with Eel library

### Getting Started

1. **Install dependencies:**

   ```bash
   pnpm install
   ```

2. **Development server:**

   ```bash
   pnpm run dev
   ```

3. **Build for production:**

   ```bash
   pnpm run build
   ```

4. **Preview production build:**
   ```bash
   pnpm run preview
   ```

### Integration with Python Eel

The frontend communicates with the Python backend through Eel:

- **Exposed Functions**: The React app exposes `generateTable` function to receive listing data
- **Backend Calls**: Uses `EelService` to call Python functions like `update_location` and `add_listing`
- **Type Safety**: Full TypeScript support for all data structures

### Key Components

- **App**: Main application component with state management
- **ColumnSelector**: Checkbox interface for selecting table columns
- **ListingTable**: Displays listing data in a responsive table
- **TableCells**: Specialized cell components for different data types
- **AddListingModal**: Modal dialog for adding new listings

## Migration from Vanilla JS

This React TypeScript version replaces the previous vanilla JavaScript implementation with:

- **Better maintainability** through component architecture
- **Type safety** with comprehensive TypeScript interfaces
- **Modern development tools** with Vite and ESLint
- **Improved user experience** with React's reactive updates
- **Enhanced code organization** with clear separation of concerns

## Available Scripts

- `pnpm run dev` - Start development server
- `pnpm run build` - Build for production
- `pnpm run lint` - Run ESLint
- `pnpm run preview` - Preview production build
- `pnpm run serve` - Serve build with network access

## Browser Support

- Chrome/Edge 88+
- Firefox 78+
- Safari 14+
