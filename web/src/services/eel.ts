import type { Listing } from "../types/listing";

/**
 * Eel integration service for communication with Python backend
 * Implements singleton pattern for consistent state management
 */
export class EelService {
  private static instance: EelService;

  private constructor() {}

  public static getInstance(): EelService {
    if (!EelService.instance) {
      EelService.instance = new EelService();
    }
    return EelService.instance;
  }

  /**
   * Check if Eel is available in the current environment
   */
  public isAvailable(): boolean {
    return typeof window !== "undefined" && Boolean(window.eel);
  }

  /**
   * Update search location in the backend
   * @param location - The location to search for listings
   */
  public async updateLocation(location: string): Promise<void> {
    if (this.isAvailable()) {
      try {
        await window.eel.update_location(location);
      } catch (error) {
        console.error("Error updating location:", error);
        throw error;
      }
    } else {
      const message = "Eel not available - updateLocation";
      console.warn(message);
      throw new Error(message);
    }
  }

  /**
   * Add a new listing via URL
   * @param link - The Airbnb listing URL to add
   */
  public async addListing(link: string): Promise<void> {
    if (this.isAvailable()) {
      try {
        await window.eel.add_listing(link);
      } catch (error) {
        console.error("Error adding listing:", error);
        throw error;
      }
    } else {
      const message = "Eel not available - addListing";
      console.warn(message);
      throw new Error(message);
    }
  }

  /**
   * Get row data for table display
   * @param columns - Array of column names to retrieve
   * @param listing - The listing object to extract data from
   */
  public async getRow(columns: string[], listing: Listing): Promise<void> {
    if (this.isAvailable()) {
      try {
        await window.eel.get_row(columns, listing);
      } catch (error) {
        console.error("Error getting row data:", error);
        throw error;
      }
    } else {
      const message = "Eel not available - getRow";
      console.warn(message);
      throw new Error(message);
    }
  }

  /**
   * Expose functions to Eel for callback from Python
   * @param func - The function to expose
   * @param name - Optional name for the exposed function
   */
  public expose(func: (...args: unknown[]) => unknown, name?: string): void {
    if (this.isAvailable()) {
      try {
        window.eel.expose(func, name);
      } catch (error) {
        console.error("Error exposing function:", error);
      }
    } else {
      console.warn("Eel not available - expose");
    }
  }
}

export default EelService;
