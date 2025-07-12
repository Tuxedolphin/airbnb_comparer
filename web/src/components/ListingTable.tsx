import type { Listing, ColumnConfig, ColumnType } from "../types/listing";
import {
  CoverCell,
  RatingCell,
  URLCell,
  DurationCell,
  CapacityCell,
  CheckInOutCell,
  LayoutCell,
  CostCell,
  SuperHostCell,
  AmenitiesCell,
  HighlightsCell,
  ReviewsSummaryCell,
  HouseRulesCell,
  PropertyDetailsCell,
  ImagesCell,
} from "./TableCells";

interface ListingTableProps {
  listings: Listing[];
  selectedColumns: ColumnConfig[];
}

const ListingTable = ({ listings, selectedColumns }: ListingTableProps) => {
  const enabledColumns = selectedColumns.filter((col) => col.enabled);

  const renderCell = (type: ColumnType, content: unknown, listing: Listing) => {
    switch (type) {
      case "Cover":
        return <CoverCell src={listing.images[0] || ""} />;
      case "ID":
        return <span>{listing.id}</span>;
      case "Rating":
        return <RatingCell rating={listing.average_rating} />;
      case "URL":
        return <URLCell url={listing.url} />;
      case "Duration":
        return <DurationCell duration={listing.duration} />;
      case "Location":
        return <span>{listing.location}</span>;
      case "Getting Around":
        return <span>{listing.getting_around}</span>;
      case "Check In/ Out Timing":
        return <CheckInOutCell checkInOut={listing.check_in_out} />;
      case "Layout":
        return <LayoutCell layout={listing.property_details.layout} />;
      case "Capacity":
        return <CapacityCell capacity={listing.capacity} />;
      case "Cost":
        return <CostCell cost={listing.cost} />;
      case "Super Host":
        return <SuperHostCell isSuperHost={listing.super_host} />;
      case "Amenities":
        return <AmenitiesCell amenities={listing.amenities} />;
      case "Highlights":
        return <HighlightsCell highlights={listing.highlights} />;
      case "Reviews Summary":
        return <ReviewsSummaryCell reviewsSummary={listing.reviews_summary} />;
      case "House Rules":
        return <HouseRulesCell houseRules={listing.house_rules} />;
      case "Property Details":
        return (
          <PropertyDetailsCell propertyDetails={listing.property_details} />
        );
      case "Notes":
        return <span>{listing.notes || ""}</span>;
      case "Images":
        return <ImagesCell images={listing.images} />;
      default:
        return <span>{String(content)}</span>;
    }
  };

  return (
    <div className="table-container">
      <table id="listing-table">
        <thead>
          <tr>
            <th>Cover</th>
            {enabledColumns.map((column) => (
              <th key={column.id}>{column.label}</th>
            ))}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {listings.map((listing) => (
            <tr key={listing.id}>
              <td>
                <CoverCell src={listing.images[0] || ""} />
              </td>
              {enabledColumns.map((column) => (
                <td key={column.id}>
                  {renderCell(column.label as ColumnType, null, listing)}
                </td>
              ))}
              <td>
                <button type="button" className="edit" title="Edit listing">
                  <i className="fa fa-edit" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ListingTable;
