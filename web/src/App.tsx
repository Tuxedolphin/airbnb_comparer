import { useState, useEffect, useCallback } from "react";
import type { Listing, ColumnConfig } from "./types/listing";
import ColumnSelector from "./components/ColumnSelector";
import ListingTable from "./components/ListingTable";
import AddListingModal from "./components/AddListingModal";
import EelService from "./services/eel";
import "./App.css";

const DEFAULT_COLUMNS: ColumnConfig[] = [
  { id: "id", label: "ID", enabled: false },
  { id: "rating", label: "Rating", enabled: true },
  { id: "url", label: "URL", enabled: false },
  { id: "duration", label: "Duration", enabled: false },
  { id: "location", label: "Location", enabled: true },
  { id: "getting-around", label: "Getting Around", enabled: false },
  { id: "check-in-out", label: "Check In/ Out Timing", enabled: false },
  { id: "layout", label: "Layout", enabled: false },
  { id: "capacity", label: "Capacity", enabled: true },
  { id: "cost", label: "Cost", enabled: true },
  { id: "super-host", label: "Super Host", enabled: false },
  { id: "amenities", label: "Amenities", enabled: false },
  { id: "highlights", label: "Highlights", enabled: false },
  { id: "reviews-summary", label: "Reviews Summary", enabled: false },
  { id: "house-rules", label: "House Rules", enabled: false },
  { id: "property-details", label: "Property Details", enabled: false },
  { id: "notes", label: "Notes", enabled: false },
  { id: "images", label: "Images", enabled: false },
];

function App() {
  const [searchLocation, setSearchLocation] = useState("");
  const [columns, setColumns] = useState<ColumnConfig[]>(DEFAULT_COLUMNS);
  const [listings, setListings] = useState<Listing[]>([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const eelService = EelService.getInstance();

  // Initialize Eel when component mounts
  useEffect(() => {
    try {
      // Expose the generateTable function to Eel
      eelService.expose((...args: unknown[]) => {
        const listingDicts = args[0] as Listing[];
        setListings(listingDicts);
        setIsLoading(false);
      }, "generateTable");

      // Expose error handler
      eelService.expose((...args: unknown[]) => {
        const errorMessage = args[0] as string;
        setError(errorMessage);
        setIsLoading(false);
      }, "handleError");
    } catch (err) {
      console.error("Failed to initialize Eel:", err);
      setError("Failed to connect to backend");
    }
  }, [eelService]);

  const handleColumnToggle = useCallback((id: string) => {
    setColumns((prev) =>
      prev.map((col) =>
        col.id === id ? { ...col, enabled: !col.enabled } : col
      )
    );
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!searchLocation.trim()) {
      setError("Please enter a location");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await eelService.updateLocation(searchLocation.toLowerCase().trim());
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to update location"
      );
      setIsLoading(false);
    }
  }, [searchLocation, eelService]);

  const handleAddListing = useCallback(
    async (link: string) => {
      if (!link.trim()) {
        setError("Please enter a valid listing URL");
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        await eelService.addListing(link.trim());
        setIsAddModalOpen(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to add listing");
        setIsLoading(false);
      }
    },
    [eelService]
  );

  const toggleSettings = useCallback(() => {
    setShowSettings(!showSettings);
  }, [showSettings]);

  if (showSettings) {
    return (
      <div className="settings">
        <h1>Settings</h1>
        <button onClick={toggleSettings}>Back to Main</button>
        <form>
          <div className="settings-section">
            <h2>Display Preferences</h2>
            <p>Customize your table columns and display options here.</p>

            <h3>Default Visible Columns</h3>
            <ColumnSelector
              columns={columns}
              onColumnToggle={handleColumnToggle}
            />
          </div>
        </form>
      </div>
    );
  }

  return (
    <>
      <div className="menu">
        <h1>Airbnb Comparer</h1>

        {error && (
          <div className="error-banner">
            <span>{error}</span>
            <button onClick={() => setError(null)}>×</button>
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <div className="search-section">
            <input
              autoComplete="off"
              id="search-location"
              name="search-location"
              type="text"
              placeholder="Insert location"
              value={searchLocation}
              onChange={(e) => setSearchLocation(e.target.value)}
              disabled={isLoading}
            />
          </div>

          <ColumnSelector
            columns={columns}
            onColumnToggle={handleColumnToggle}
          />
        </form>

        <div className="button-group">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isLoading || !searchLocation.trim()}
          >
            {isLoading ? "Loading..." : "Submit"}
          </button>
          <button
            type="button"
            onClick={() => setIsAddModalOpen(true)}
            disabled={isLoading}
          >
            Add Listing
          </button>
          <button type="button" onClick={toggleSettings} disabled={isLoading}>
            Settings
          </button>
        </div>
      </div>

      <div className="table-background">
        {isLoading ? (
          <div className="loading-state">
            <p>Loading listings...</p>
          </div>
        ) : (
          <ListingTable listings={listings} selectedColumns={columns} />
        )}
      </div>

      <AddListingModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAddListing={handleAddListing}
      />
    </>
  );
}

export default App;
