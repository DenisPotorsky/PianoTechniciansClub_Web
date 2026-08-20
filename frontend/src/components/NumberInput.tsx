import React, { useState, useEffect } from 'react';

interface NumberInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  placeholder?: string;
}

const NumberInput: React.FC<NumberInputProps> = ({
  label,
  value,
  onChange,
  placeholder = ''
}) => {
  const [displayValue, setDisplayValue] = useState<string>(String(value));

  useEffect(() => {
    setDisplayValue(String(value));
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const raw = e.target.value;
    setDisplayValue(raw);

    const normalized = raw.replace(',', '.');
    const num = parseFloat(normalized);

    if (!isNaN(num) && normalized !== '') {
      onChange(num);
    } else if (raw === '' || raw === '-' || raw === '.') {
      onChange(0);
    }
  };

  const handleBlur = () => {
    if (displayValue === '' || displayValue === '-' || displayValue === '.') {
      setDisplayValue('0');
      onChange(0);
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <input
        type="text"
        inputMode="decimal"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder={placeholder}
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
      />
    </div>
  );
};

export default NumberInput;