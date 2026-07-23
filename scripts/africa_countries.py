"""Reference table of African countries and territories.

Source of truth for the ``afriso`` country dimension. Each entry maps an
ISO 3166-1 alpha-2 code to its alpha-3 code, English short name, and region.

Regions use the five common groupings ("North Africa", "West Africa",
"Central Africa", "East Africa", "Southern Africa"), which map onto the
UN M49 subregions (Northern / Western / Middle / Eastern / Southern Africa).
"""

# code2: (code3, name, region)
AFRICA = {
    # North Africa (UN: Northern Africa)
    "DZ": ("DZA", "Algeria", "North Africa"),
    "EG": ("EGY", "Egypt", "North Africa"),
    "LY": ("LBY", "Libya", "North Africa"),
    "MA": ("MAR", "Morocco", "North Africa"),
    "SD": ("SDN", "Sudan", "North Africa"),
    "TN": ("TUN", "Tunisia", "North Africa"),
    "EH": ("ESH", "Western Sahara", "North Africa"),
    # West Africa (UN: Western Africa)
    "BJ": ("BEN", "Benin", "West Africa"),
    "BF": ("BFA", "Burkina Faso", "West Africa"),
    "CV": ("CPV", "Cabo Verde", "West Africa"),
    "CI": ("CIV", "Côte d'Ivoire", "West Africa"),
    "GM": ("GMB", "Gambia", "West Africa"),
    "GH": ("GHA", "Ghana", "West Africa"),
    "GN": ("GIN", "Guinea", "West Africa"),
    "GW": ("GNB", "Guinea-Bissau", "West Africa"),
    "LR": ("LBR", "Liberia", "West Africa"),
    "ML": ("MLI", "Mali", "West Africa"),
    "MR": ("MRT", "Mauritania", "West Africa"),
    "NE": ("NER", "Niger", "West Africa"),
    "NG": ("NGA", "Nigeria", "West Africa"),
    "SH": ("SHN", "Saint Helena", "West Africa"),
    "SN": ("SEN", "Senegal", "West Africa"),
    "SL": ("SLE", "Sierra Leone", "West Africa"),
    "TG": ("TGO", "Togo", "West Africa"),
    # Central Africa (UN: Middle Africa)
    "AO": ("AGO", "Angola", "Central Africa"),
    "CM": ("CMR", "Cameroon", "Central Africa"),
    "CF": ("CAF", "Central African Republic", "Central Africa"),
    "TD": ("TCD", "Chad", "Central Africa"),
    "CG": ("COG", "Republic of the Congo", "Central Africa"),
    "CD": ("COD", "Democratic Republic of the Congo", "Central Africa"),
    "GQ": ("GNQ", "Equatorial Guinea", "Central Africa"),
    "GA": ("GAB", "Gabon", "Central Africa"),
    "ST": ("STP", "São Tomé and Príncipe", "Central Africa"),
    # East Africa (UN: Eastern Africa)
    "BI": ("BDI", "Burundi", "East Africa"),
    "KM": ("COM", "Comoros", "East Africa"),
    "DJ": ("DJI", "Djibouti", "East Africa"),
    "ER": ("ERI", "Eritrea", "East Africa"),
    "ET": ("ETH", "Ethiopia", "East Africa"),
    "KE": ("KEN", "Kenya", "East Africa"),
    "MG": ("MDG", "Madagascar", "East Africa"),
    "MW": ("MWI", "Malawi", "East Africa"),
    "MU": ("MUS", "Mauritius", "East Africa"),
    "YT": ("MYT", "Mayotte", "East Africa"),
    "MZ": ("MOZ", "Mozambique", "East Africa"),
    "RE": ("REU", "Réunion", "East Africa"),
    "RW": ("RWA", "Rwanda", "East Africa"),
    "SC": ("SYC", "Seychelles", "East Africa"),
    "SO": ("SOM", "Somalia", "East Africa"),
    "SS": ("SSD", "South Sudan", "East Africa"),
    "TZ": ("TZA", "Tanzania", "East Africa"),
    "UG": ("UGA", "Uganda", "East Africa"),
    "ZM": ("ZMB", "Zambia", "East Africa"),
    "ZW": ("ZWE", "Zimbabwe", "East Africa"),
    # Southern Africa
    "BW": ("BWA", "Botswana", "Southern Africa"),
    "SZ": ("SWZ", "Eswatini", "Southern Africa"),
    "LS": ("LSO", "Lesotho", "Southern Africa"),
    "NA": ("NAM", "Namibia", "Southern Africa"),
    "ZA": ("ZAF", "South Africa", "Southern Africa"),
}

# Accepted aliases for region names (normalised lower-case -> canonical).
REGION_ALIASES = {
    "north africa": "North Africa",
    "northern africa": "North Africa",
    "west africa": "West Africa",
    "western africa": "West Africa",
    "central africa": "Central Africa",
    "middle africa": "Central Africa",
    "east africa": "East Africa",
    "eastern africa": "East Africa",
    "southern africa": "Southern Africa",
    "south africa (region)": "Southern Africa",
}
