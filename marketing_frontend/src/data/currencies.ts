export const currencySymbols: { [key: string]: string } = {
  USD: "$",
  EUR: "€",
  GBP: "£",
  JPY: "¥",
  AUD: "A$",
  CAD: "C$",
  CHF: "CHF",
  CNY: "¥",
  SEK: "kr",
  NZD: "NZ$",
};

export const getCurrencySymbol = (currencyCode: string, fallback: string = "$") => {
  return currencySymbols[currencyCode] || fallback;
};
