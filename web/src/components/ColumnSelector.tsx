import type { ColumnConfig } from "../types/listing";

interface ColumnSelectorProps {
  columns: ColumnConfig[];
  onColumnToggle: (id: string) => void;
}

const ColumnSelector = ({ columns, onColumnToggle }: ColumnSelectorProps) => {
  return (
    <fieldset>
      <legend>Show:</legend>
      {columns.map((column) => (
        <div key={column.id} className="input-group">
          <input
            type="checkbox"
            name={column.id}
            id={column.id}
            checked={column.enabled}
            onChange={() => onColumnToggle(column.id)}
          />
          <label htmlFor={column.id}>{column.label}</label>
        </div>
      ))}
    </fieldset>
  );
};

export default ColumnSelector;
