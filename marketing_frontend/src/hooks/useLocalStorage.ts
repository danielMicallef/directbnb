import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T, expirationDays: number): [T, React.Dispatch<React.SetStateAction<T>>] {
  const getStoredValue = (): T => {
    try {
      const item = window.localStorage.getItem(key);
      if (item) {
        const { value, timestamp } = JSON.parse(item);
        const expirationMs = expirationDays * 24 * 60 * 60 * 1000;
        if (new Date().getTime() - timestamp < expirationMs) {
          return value;
        }
      }
      window.localStorage.removeItem(key);
      return initialValue;
    } catch (error) {
      console.error('Error reading from localStorage', error);
      return initialValue;
    }
  };

  const [storedValue, setStoredValue] = useState<T>(getStoredValue);

  useEffect(() => {
    try {
      const item = {
        value: storedValue,
        timestamp: new Date().getTime(),
      };
      window.localStorage.setItem(key, JSON.stringify(item));
    } catch (error) {
      console.error('Error writing to localStorage', error);
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue];
}
