export interface Review {
  comment: string;
  rating: number;
  date: string;
}

export interface ReviewsSummary {
  total_reviews: number;
  recent_reviews: Review[];
}

export interface HouseRules {
  additional_rules: string[];
  general_rules: Array<{
    category: string;
    rules: string[];
  }>;
  check_in_out: string[];
}

export interface PropertyDetails {
  room_type: string;
  is_guest_favorite: boolean;
  is_super_host: boolean;
  layout: string[];
}

export interface Listing {
  id: number;
  url: string;
  duration: number;
  cost: number;
  coordinates: string;
  super_host: boolean;
  capacity: number;
  average_rating: number;
  check_in_out: string[];
  amenities: Record<string, string[]>;
  images: string[];
  location: string;
  getting_around: string;
  highlights: string[];
  reviews_summary: ReviewsSummary;
  house_rules: HouseRules;
  property_details: PropertyDetails;
  notes?: string;
}

export interface ColumnConfig {
  id: string;
  label: string;
  enabled: boolean;
}

export type ColumnType =
  | "Cover"
  | "ID"
  | "Rating"
  | "URL"
  | "Duration"
  | "Location"
  | "Getting Around"
  | "Check In/ Out Timing"
  | "Layout"
  | "Capacity"
  | "Cost"
  | "Super Host"
  | "Amenities"
  | "Highlights"
  | "Reviews Summary"
  | "House Rules"
  | "Property Details"
  | "Notes"
  | "Images";

// Eel types
declare global {
  interface Window {
    eel: {
      update_location: (location: string) => void;
      add_listing: (link: string) => void;
      get_row: (columns: string[], listing: Listing) => void;
      expose: (func: (...args: unknown[]) => unknown, name?: string) => void;
    };
  }
}

export {};
