import { useState } from "react";

interface AddListingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddListing: (link: string) => void;
}

const AddListingModal = ({
  isOpen,
  onClose,
  onAddListing,
}: AddListingModalProps) => {
  const [link, setLink] = useState("");
  const [dailyPrice, setDailyPrice] = useState("");
  const [miscPrice, setMiscPrice] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (link.trim()) {
      onAddListing(link.trim());
      handleClose();
    }
  };

  const handleClose = () => {
    setLink("");
    setDailyPrice("");
    setMiscPrice("");
    onClose();
  };

  if (!isOpen) return null;

  return (
    <dialog open className="add-listing-modal">
      <h1 className="add-header">Add a Listing</h1>
      <form className="add-listing" onSubmit={handleSubmit}>
        <label htmlFor="link">Link:</label>
        <input
          id="link"
          type="url"
          value={link}
          onChange={(e) => setLink(e.target.value)}
          required
        />

        <label htmlFor="dailyPrice">Daily Price:</label>
        <input
          id="dailyPrice"
          type="number"
          value={dailyPrice}
          onChange={(e) => setDailyPrice(e.target.value)}
        />

        <label htmlFor="miscPrice">Misc Price:</label>
        <input
          id="miscPrice"
          type="number"
          value={miscPrice}
          onChange={(e) => setMiscPrice(e.target.value)}
        />

        <div className="modal-buttons">
          <button type="submit">Add</button>
          <button type="button" onClick={handleClose}>
            Cancel
          </button>
        </div>
      </form>
    </dialog>
  );
};

export default AddListingModal;
