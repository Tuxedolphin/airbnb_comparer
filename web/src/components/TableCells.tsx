import type {
  ReviewsSummary,
  HouseRules,
  PropertyDetails,
} from "../types/listing";

interface CoverCellProps {
  src: string;
}

export const CoverCell = ({ src }: CoverCellProps) => (
  <img src={src} alt="Property cover" />
);

interface RatingCellProps {
  rating: number;
}

export const RatingCell = ({ rating }: RatingCellProps) => (
  <span>{Math.round(rating * 100) / 100}</span>
);

interface URLCellProps {
  url: string;
}

export const URLCell = ({ url }: URLCellProps) => (
  <a href={url} target="_blank" rel="noopener noreferrer">
    <button type="button">View Listing</button>
  </a>
);

interface DurationCellProps {
  duration: number;
}

export const DurationCell = ({ duration }: DurationCellProps) => (
  <span>{duration} days</span>
);

interface CapacityCellProps {
  capacity: number;
}

export const CapacityCell = ({ capacity }: CapacityCellProps) => (
  <span>{capacity} people</span>
);

interface CheckInOutCellProps {
  checkInOut: string[];
}

export const CheckInOutCell = ({ checkInOut }: CheckInOutCellProps) => (
  <div>
    {checkInOut.map((value, index) => (
      <p key={index}>{value}</p>
    ))}
  </div>
);

interface LayoutCellProps {
  layout: string[];
}

export const LayoutCell = ({ layout }: LayoutCellProps) => (
  <ul>
    {layout.map((item, index) => (
      <li key={index}>{item}</li>
    ))}
  </ul>
);

interface CostCellProps {
  cost: number;
}

export const CostCell = ({ cost }: CostCellProps) => <span>${cost}</span>;

interface SuperHostCellProps {
  isSuperHost: boolean;
}

export const SuperHostCell = ({ isSuperHost }: SuperHostCellProps) => (
  <span>{isSuperHost ? "Yes" : "No"}</span>
);

interface AmenitiesCellProps {
  amenities: Record<string, string[]>;
}

export const AmenitiesCell = ({ amenities }: AmenitiesCellProps) => (
  <div className="amenities">
    <ol>
      {Object.entries(amenities).map(([header, items]) => (
        <li key={header}>
          {header}
          <ul>
            {items.map((item, index) => (
              <li key={index}>{item}</li>
            ))}
          </ul>
        </li>
      ))}
    </ol>
  </div>
);

interface HighlightsCellProps {
  highlights: string[];
}

export const HighlightsCell = ({ highlights }: HighlightsCellProps) => (
  <ul>
    {highlights.map((highlight, index) => (
      <li key={index}>{highlight}</li>
    ))}
  </ul>
);

interface ReviewsSummaryCellProps {
  reviewsSummary: ReviewsSummary;
}

export const ReviewsSummaryCell = ({
  reviewsSummary,
}: ReviewsSummaryCellProps) => (
  <div className="reviews-summary">
    <p>Total Reviews: {reviewsSummary.total_reviews}</p>
    {reviewsSummary.recent_reviews &&
      reviewsSummary.recent_reviews.length > 0 && (
        <>
          <h4>Recent Reviews:</h4>
          {reviewsSummary.recent_reviews.map((review, index) => (
            <div key={index} className="review-item">
              <span className="review-rating">Rating: {review.rating}/5</span>
              <p className="review-comment">{review.comment}</p>
              <span className="review-date">{review.date}</span>
            </div>
          ))}
        </>
      )}
  </div>
);

interface HouseRulesCellProps {
  houseRules: HouseRules;
}

export const HouseRulesCell = ({ houseRules }: HouseRulesCellProps) => (
  <div className="house-rules">
    {houseRules.check_in_out && houseRules.check_in_out.length > 0 && (
      <>
        <h4>Check-in/Check-out:</h4>
        <ul>
          {houseRules.check_in_out.map((rule, index) => (
            <li key={index}>{rule}</li>
          ))}
        </ul>
      </>
    )}

    {houseRules.general_rules && houseRules.general_rules.length > 0 && (
      <>
        {houseRules.general_rules.map((ruleGroup, index) => (
          <div key={index}>
            <h4>{ruleGroup.category}:</h4>
            <ul>
              {ruleGroup.rules.map((rule, ruleIndex) => (
                <li key={ruleIndex}>{rule}</li>
              ))}
            </ul>
          </div>
        ))}
      </>
    )}

    {houseRules.additional_rules && houseRules.additional_rules.length > 0 && (
      <>
        <h4>Additional Rules:</h4>
        {houseRules.additional_rules.map((rule, index) => (
          <p key={index}>{rule}</p>
        ))}
      </>
    )}
  </div>
);

interface PropertyDetailsCellProps {
  propertyDetails: PropertyDetails;
}

export const PropertyDetailsCell = ({
  propertyDetails,
}: PropertyDetailsCellProps) => (
  <div className="property-details">
    <p>Room Type: {propertyDetails.room_type}</p>
    <p>Guest Favorite: {propertyDetails.is_guest_favorite ? "Yes" : "No"}</p>
    {propertyDetails.layout && propertyDetails.layout.length > 0 && (
      <>
        <h4>Layout:</h4>
        <ul>
          {propertyDetails.layout.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </>
    )}
  </div>
);

interface ImagesCellProps {
  images: string[];
}

export const ImagesCell = ({ images }: ImagesCellProps) => {
  const handleShowImages = () => {
    // We'll implement the modal functionality later
    console.log("Show images:", images);
  };

  return (
    <button type="button" onClick={handleShowImages}>
      See Images
    </button>
  );
};
