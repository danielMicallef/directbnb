import disposable_email_domains as ded

from urllib.parse import urlparse


def get_domain(url):
    """
    Extracts the domain from a given URL.
    """
    if not url:
        return ""
    return urlparse(url).netloc


def is_email_blacklisted(email):
    if "@" not in email:
        raise ValueError("Invalid email address %s" % email)

    black_list_domains = set(ded.blocklist)
    domain = email.split("@")[-1].lower()
    return domain in black_list_domains


# Currency symbols mapping for popular currencies
CURRENCY_SYMBOLS = {
    "USD": "$",           # US Dollar
    "EUR": "€",           # Euro
    "GBP": "£",           # British Pound
    "JPY": "¥",           # Japanese Yen
    "CNY": "¥",           # Chinese Yuan
    "AUD": "A$",          # Australian Dollar
    "CAD": "C$",          # Canadian Dollar
    "CHF": "CHF",         # Swiss Franc
    "INR": "₹",           # Indian Rupee
    "RUB": "₽",           # Russian Ruble
    "BRL": "R$",          # Brazilian Real
    "ZAR": "R",           # South African Rand
    "MXN": "$",           # Mexican Peso
    "SEK": "kr",          # Swedish Krona
    "NOK": "kr",          # Norwegian Krone
    "DKK": "kr",          # Danish Krone
    "PLN": "zł",          # Polish Zloty
    "TRY": "₺",           # Turkish Lira
    "SGD": "S$",          # Singapore Dollar
    "HKD": "HK$",         # Hong Kong Dollar
    "NZD": "NZ$",         # New Zealand Dollar
    "KRW": "₩",           # South Korean Won
    "THB": "฿",           # Thai Baht
}
