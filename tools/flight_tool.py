import os
import re
import certifi
import airportsdata
import pycountry
from dotenv import load_dotenv
import requests

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# default origin when user says only destination eg. "Japan Trip"
# Change this if your default location is not Bangladesh/Dhaka
DEFAULT_ORIGIN_IATA= os.getenv("DEFAULT_ORIGIN_IATA", "NAG")

BASE_URL= "https://api.aviationstack.com/v1/flights"

AIRPORTS= airportsdata.load('IATA')

# ============================================================
# COUNTRY ALIASES
# ============================================================

COUNTRY_ALIASES = {
    # North America
    "usa": "US",
    "u.s.a": "US",
    "u.s.": "US",
    "us": "US",
    "america": "US",
    "united states": "US",
    "united states of america": "US",

    "canada": "CA",
    "ca": "CA",

    "mexico": "MX",
    "mex": "MX",

    # South America
    "brazil": "BR",
    "brasil": "BR",

    "argentina": "AR",
    "chile": "CL",
    "colombia": "CO",
    "peru": "PE",
    "ecuador": "EC",
    "bolivia": "BO",
    "uruguay": "UY",
    "paraguay": "PY",
    "venezuela": "VE",

    # Europe
    "uk": "GB",
    "u.k.": "GB",
    "britain": "GB",
    "great britain": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",
    "united kingdom": "GB",

    "ireland": "IE",
    "republic of ireland": "IE",

    "france": "FR",
    "germany": "DE",
    "italy": "IT",
    "spain": "ES",
    "portugal": "PT",

    "netherlands": "NL",
    "holland": "NL",

    "belgium": "BE",
    "switzerland": "CH",
    "austria": "AT",

    "greece": "GR",
    "denmark": "DK",
    "sweden": "SE",
    "norway": "NO",
    "finland": "FI",
    "iceland": "IS",

    "poland": "PL",
    "czech republic": "CZ",
    "czechia": "CZ",
    "hungary": "HU",
    "romania": "RO",
    "bulgaria": "BG",

    "croatia": "HR",
    "serbia": "RS",
    "slovakia": "SK",
    "slovenia": "SI",

    "ukraine": "UA",
    "russia": "RU",

    "estonia": "EE",
    "latvia": "LV",
    "lithuania": "LT",

    "luxembourg": "LU",
    "malta": "MT",
    "cyprus": "CY",

    # Middle East
    "uae": "AE",
    "u.a.e": "AE",
    "united arab emirates": "AE",
    "emirates": "AE",
    "dubai": "AE",
    "abu dhabi": "AE",

    "saudi arabia": "SA",
    "saudi": "SA",

    "qatar": "QA",
    "doha": "QA",

    "turkey": "TR",
    "türkiye": "TR",
    "turkiye": "TR",

    "israel": "IL",
    "jordan": "JO",
    "oman": "OM",
    "bahrain": "BH",
    "kuwait": "KW",
    "lebanon": "LB",

    # South Asia
    "india": "IN",
    "bharat": "IN",

    "pakistan": "PK",
    "bangladesh": "BD",
    "nepal": "NP",
    "sri lanka": "LK",
    "srilanka": "LK",
    "maldives": "MV",
    "bhutan": "BT",

    # East Asia
    "japan": "JP",
    "china": "CN",
    "mainland china": "CN",

    "south korea": "KR",
    "korea": "KR",
    "republic of korea": "KR",

    "north korea": "KP",
    "taiwan": "TW",

    # Southeast Asia
    "singapore": "SG",
    "malaysia": "MY",
    "thailand": "TH",
    "indonesia": "ID",
    "vietnam": "VN",
    "viet nam": "VN",
    "philippines": "PH",
    "philippine": "PH",
    "cambodia": "KH",
    "laos": "LA",
    "myanmar": "MM",
    "burma": "MM",
    "brunei": "BN",

    # Central Asia
    "kazakhstan": "KZ",
    "uzbekistan": "UZ",
    "kyrgyzstan": "KG",
    "tajikistan": "TJ",
    "turkmenistan": "TM",

    # Oceania
    "australia": "AU",
    "new zealand": "NZ",
    "fiji": "FJ",

    # Africa
    "south africa": "ZA",
    "egypt": "EG",
    "morocco": "MA",
    "tunisia": "TN",
    "algeria": "DZ",

    "kenya": "KE",
    "tanzania": "TZ",
    "ethiopia": "ET",
    "nigeria": "NG",
    "ghana": "GH",

    "mauritius": "MU",
    "seychelles": "SC",
    "uganda": "UG",
    "rwanda": "RW",
    "zambia": "ZM",
    "zimbabwe": "ZW",
    "namibia": "NA",
    "botswana": "BW",
}


# ============================================================
# PREFERRED MAIN AIRPORT FOR COUNTRY-LEVEL SEARCH
# ============================================================

COUNTRY_MAIN_AIRPORT = {

    # South Asia
    "IN": "DEL",
    "PK": "KHI",
    "BD": "DAC",
    "NP": "KTM",
    "LK": "CMB",
    "MV": "MLE",
    "BT": "PBH",

    # East Asia
    "JP": "NRT",
    "CN": "PEK",
    "KR": "ICN",
    "KP": "FNJ",
    "TW": "TPE",

    # Southeast Asia
    "SG": "SIN",
    "MY": "KUL",
    "TH": "BKK",
    "ID": "CGK",
    "VN": "SGN",
    "PH": "MNL",
    "KH": "PNH",
    "LA": "VTE",
    "MM": "RGN",
    "BN": "BWN",

    # Middle East
    "AE": "DXB",
    "SA": "JED",
    "QA": "DOH",
    "TR": "IST",
    "IL": "TLV",
    "JO": "AMM",
    "OM": "MCT",
    "BH": "BAH",
    "KW": "KWI",
    "LB": "BEY",

    # Europe
    "GB": "LHR",
    "IE": "DUB",
    "FR": "CDG",
    "DE": "FRA",
    "IT": "FCO",
    "ES": "MAD",
    "PT": "LIS",
    "NL": "AMS",
    "BE": "BRU",
    "CH": "ZRH",
    "AT": "VIE",
    "GR": "ATH",
    "DK": "CPH",
    "SE": "ARN",
    "NO": "OSL",
    "FI": "HEL",
    "IS": "KEF",
    "PL": "WAW",
    "CZ": "PRG",
    "HU": "BUD",
    "RO": "OTP",
    "BG": "SOF",
    "HR": "ZAG",
    "RS": "BEG",
    "SK": "BTS",
    "SI": "LJU",
    "UA": "KBP",
    "RU": "SVO",
    "EE": "TLL",
    "LV": "RIX",
    "LT": "VNO",
    "LU": "LUX",
    "MT": "MLA",
    "CY": "LCA",

    # North America
    "US": "JFK",
    "CA": "YYZ",
    "MX": "MEX",

    # South America
    "BR": "GRU",
    "AR": "EZE",
    "CL": "SCL",
    "CO": "BOG",
    "PE": "LIM",
    "EC": "UIO",
    "BO": "VVI",
    "UY": "MVD",
    "PY": "ASU",
    "VE": "CCS",

    # Oceania
    "AU": "SYD",
    "NZ": "AKL",
    "FJ": "NAN",

    # Africa
    "ZA": "JNB",
    "EG": "CAI",
    "MA": "CMN",
    "TN": "TUN",
    "DZ": "ALG",
    "KE": "NBO",
    "TZ": "DAR",
    "ET": "ADD",
    "NG": "LOS",
    "GH": "ACC",
    "MU": "MRU",
    "SC": "SEZ",
    "UG": "EBB",
    "RW": "KGL",
    "ZM": "LUN",
    "ZW": "HRE",
    "NA": "WDH",
    "BW": "GBE",

    # Central Asia
    "KZ": "ALA",
    "UZ": "TAS",
    "KG": "FRU",
    "TJ": "DYU",
    "TM": "ASB",
}


# ============================================================
# CITY -> MAIN AIRPORT
# ============================================================

CITY_MAIN_AIRPORT = {

    # ---------------- INDIA ----------------
    "delhi": "DEL",
    "new delhi": "DEL",

    "mumbai": "BOM",
    "bombay": "BOM",

    "pune": "PNQ",
    "bangalore": "BLR",
    "bengaluru": "BLR",

    "hyderabad": "HYD",
    "chennai": "MAA",
    "madras": "MAA",

    "kolkata": "CCU",
    "calcutta": "CCU",

    "ahmedabad": "AMD",
    "jaipur": "JAI",
    "goa": "GOI",
    "panaji": "GOI",
    "dabolim": "GOI",

    "kochi": "COK",
    "cochin": "COK",

    "thiruvananthapuram": "TRV",
    "trivandrum": "TRV",

    "lucknow": "LKO",
    "varanasi": "VNS",
    "indore": "IDR",
    "nagpur": "NAG",
    "bhubaneswar": "BBI",
    "patna": "PAT",
    "ranchi": "IXR",
    "surat": "STV",
    "chandigarh": "IXC",
    "amritsar": "ATQ",
    "srinagar": "SXR",
    "leh": "IXL",
    "guwahati": "GAU",
    "coimbatore": "CJB",
    "madurai": "IXM",
    "visakhapatnam": "VTZ",
    "vishakhapatnam": "VTZ",
    "mangalore": "IXE",
    "mangaluru": "IXE",
    "tiruchirappalli": "TRZ",
    "trichy": "TRZ",
    "udaipur": "UDR",
    "jodhpur": "JDH",
    "aurangabad": "IXU",
    "chhatrapati sambhajinagar": "IXU",
    "nashik": "ISK",
    "dehradun": "DED",
    "agra": "AGR",
    "amritsar": "ATQ",
    "rajkot": "HSR",
    "vadodara": "BDQ",
    "goa": "GOI",
    "port blair": "IXZ",

    # ---------------- BANGLADESH ----------------
    "dhaka": "DAC",
    "chittagong": "CGP",
    "chattogram": "CGP",
    "sylhet": "ZYL",
    "cox's bazar": "CXB",

    # ---------------- JAPAN ----------------
    "tokyo": "NRT",
    "narita": "NRT",
    "haneda": "HND",

    "osaka": "KIX",
    "kyoto": "KIX",

    "nagoya": "NGO",
    "sapporo": "CTS",
    "fukuoka": "FUK",
    "okinawa": "OKA",
    "naha": "OKA",
    "hiroshima": "HIJ",

    # ---------------- CHINA ----------------
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "chengdu": "CTU",
    "chongqing": "CKG",
    "xian": "XIY",
    "xi'an": "XIY",
    "hangzhou": "HGH",
    "nanjing": "NKG",
    "wuhan": "WUH",
    "qingdao": "TAO",
    "tianjin": "TSN",
    "kunming": "KMG",
    "xiamen": "XMN",
    "harbin": "HRB",

    # ---------------- SOUTH KOREA ----------------
    "seoul": "ICN",
    "incheon": "ICN",
    "busan": "PUS",
    "jeju": "CJU",
    "daegu": "TAE",
    "gwangju": "KWJ",

    # ---------------- SINGAPORE ----------------
    "singapore": "SIN",

    # ---------------- MALAYSIA ----------------
    "kuala lumpur": "KUL",
    "kl": "KUL",
    "penang": "PEN",
    "george town": "PEN",
    "langkawi": "LGK",
    "johor bahru": "JHB",
    "kota kinabalu": "BKI",
    "kuching": "KCH",

    # ---------------- THAILAND ----------------
    "bangkok": "BKK",
    "phuket": "HKT",
    "chiang mai": "CNX",
    "krabi": "KBV",
    "pattaya": "UTP",
    "koh samui": "USM",

    # ---------------- INDONESIA ----------------
    "jakarta": "CGK",
    "bali": "DPS",
    "denpasar": "DPS",
    "surabaya": "SUB",
    "bandung": "BDO",
    "medan": "KNO",
    "yogyakarta": "YIA",
    "makassar": "UPG",

    # ---------------- VIETNAM ----------------
    "ho chi minh city": "SGN",
    "ho chi minh": "SGN",
    "saigon": "SGN",
    "hanoi": "HAN",
    "da nang": "DAD",
    "danang": "DAD",
    "phu quoc": "PQC",
    "nha trang": "CXR",
    "haiphong": "HPH",

    # ---------------- PHILIPPINES ----------------
    "manila": "MNL",
    "cebu": "CEB",
    "davao": "DVO",
    "boracay": "MPH",
    "palawan": "PPS",

    # ---------------- NEPAL ----------------
    "kathmandu": "KTM",
    "pokhara": "PKR",
    "bhairahawa": "BWA",

    # ---------------- SRI LANKA ----------------
    "colombo": "CMB",
    "kandy": "CMB",
    "galle": "CMB",

    # ---------------- MALDIVES ----------------
    "male": "MLE",
    "malé": "MLE",

    # ---------------- UAE ----------------
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",
    "ras al khaimah": "RKT",
    "al ain": "AAN",

    # ---------------- SAUDI ARABIA ----------------
    "riyadh": "RUH",
    "jeddah": "JED",
    "medina": "MED",
    "makkah": "JED",
    "mecca": "JED",
    "dammam": "DMM",
    "taif": "TIF",

    # ---------------- QATAR ----------------
    "doha": "DOH",

    # ---------------- TURKEY ----------------
    "istanbul": "IST",
    "ankara": "ESB",
    "antalya": "AYT",
    "izmir": "ADB",
    "bodrum": "BJV",
    "cappadocia": "NAV",

    # ---------------- ISRAEL ----------------
    "tel aviv": "TLV",
    "jerusalem": "TLV",
    "eilat": "ETM",

    # ---------------- OMAN ----------------
    "muscat": "MCT",
    "salalah": "SLL",

    # ---------------- UK ----------------
    "london": "LHR",
    "manchester": "MAN",
    "birmingham": "BHX",
    "edinburgh": "EDI",
    "glasgow": "GLA",
    "liverpool": "LPL",
    "bristol": "BRS",
    "leeds": "LBA",
    "newcastle": "NCL",
    "belfast": "BFS",

    # ---------------- FRANCE ----------------
    "paris": "CDG",
    "nice": "NCE",
    "lyon": "LYS",
    "marseille": "MRS",
    "toulouse": "TLS",
    "bordeaux": "BOD",
    "strasbourg": "SXB",

    # ---------------- GERMANY ----------------
    "frankfurt": "FRA",
    "berlin": "BER",
    "munich": "MUC",
    "hamburg": "HAM",
    "dusseldorf": "DUS",
    "düsseldorf": "DUS",
    "cologne": "CGN",
    "stuttgart": "STR",

    # ---------------- ITALY ----------------
    "rome": "FCO",
    "milan": "MXP",
    "venice": "VCE",
    "florence": "FLR",
    "naples": "NAP",
    "bologna": "BLQ",
    "turin": "TRN",

    # ---------------- SPAIN ----------------
    "madrid": "MAD",
    "barcelona": "BCN",
    "seville": "SVQ",
    "malaga": "AGP",
    "valencia": "VLC",
    "ibiza": "IBZ",
    "palma de mallorca": "PMI",

    # ---------------- PORTUGAL ----------------
    "lisbon": "LIS",
    "porto": "OPO",
    "faro": "FAO",
    "madeira": "FNC",

    # ---------------- NETHERLANDS ----------------
    "amsterdam": "AMS",
    "rotterdam": "RTM",
    "eindhoven": "EIN",

    # ---------------- SWITZERLAND ----------------
    "zurich": "ZRH",
    "geneva": "GVA",
    "basel": "BSL",
    "bern": "BRN",

    # ---------------- AUSTRIA ----------------
    "vienna": "VIE",
    "salzburg": "SZG",
    "innsbruck": "INN",

    # ---------------- GREECE ----------------
    "athens": "ATH",
    "santorini": "JTR",
    "mykonos": "JMK",
    "crete": "HER",
    "heraklion": "HER",

    # ---------------- DENMARK ----------------
    "copenhagen": "CPH",

    # ---------------- SWEDEN ----------------
    "stockholm": "ARN",
    "gothenburg": "GOT",

    # ---------------- NORWAY ----------------
    "oslo": "OSL",
    "bergen": "BGO",
    "tromso": "TOS",

    # ---------------- FINLAND ----------------
    "helsinki": "HEL",
    "rovaniemi": "RVN",

    # ---------------- POLAND ----------------
    "warsaw": "WAW",
    "krakow": "KRK",
    "gdansk": "GDN",
    "wroclaw": "WRO",

    # ---------------- CZECHIA ----------------
    "prague": "PRG",

    # ---------------- HUNGARY ----------------
    "budapest": "BUD",

    # ---------------- CROATIA ----------------
    "zagreb": "ZAG",
    "dubrovnik": "DBV",
    "split": "SPU",

    # ---------------- RUSSIA ----------------
    "moscow": "SVO",
    "st petersburg": "LED",
    "saint petersburg": "LED",
    "sochi": "AER",
    "kazan": "KZN",

    # ---------------- USA ----------------
    "new york": "JFK",
    "new york city": "JFK",
    "nyc": "JFK",

    "los angeles": "LAX",
    "la": "LAX",

    "san francisco": "SFO",
    "chicago": "ORD",
    "boston": "BOS",
    "washington": "IAD",
    "washington dc": "IAD",
    "miami": "MIA",
    "las vegas": "LAS",
    "orlando": "MCO",
    "seattle": "SEA",
    "houston": "IAH",
    "dallas": "DFW",
    "atlanta": "ATL",
    "denver": "DEN",
    "phoenix": "PHX",
    "philadelphia": "PHL",
    "san diego": "SAN",
    "detroit": "DTW",
    "minneapolis": "MSP",
    "honolulu": "HNL",
    "austin": "AUS",
    "charlotte": "CLT",
    "newark": "EWR",
    "portland": "PDX",

    # ---------------- CANADA ----------------
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",
    "ottawa": "YOW",
    "edmonton": "YEG",
    "winnipeg": "YWG",
    "quebec city": "YQB",

    # ---------------- MEXICO ----------------
    "mexico city": "MEX",
    "cancun": "CUN",
    "guadalajara": "GDL",
    "monterrey": "MTY",
    "tijuana": "TIJ",
    "los cabos": "SJD",

    # ---------------- BRAZIL ----------------
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",
    "brasilia": "BSB",
    "salvador": "SSA",
    "fortaleza": "FOR",
    "recife": "REC",

    # ---------------- ARGENTINA ----------------
    "buenos aires": "EZE",
    "cordoba": "COR",
    "mendoza": "MDZ",

    # ---------------- AUSTRALIA ----------------
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "adelaide": "ADL",
    "gold coast": "OOL",
    "cairns": "CNS",
    "canberra": "CBR",
    "darwin": "DRW",
    "hobart": "HBA",

    # ---------------- NEW ZEALAND ----------------
    "auckland": "AKL",
    "wellington": "WLG",
    "christchurch": "CHC",
    "queenstown": "ZQN",
    "dunedin": "DUD",

    # ---------------- SOUTH AFRICA ----------------
    "johannesburg": "JNB",
    "cape town": "CPT",
    "durban": "DUR",
    "pretoria": "JNB",

    # ---------------- EGYPT ----------------
    "cairo": "CAI",
    "luxor": "LXR",
    "alexandria": "HBE",
    "sharm el sheikh": "SSH",
    "hurghada": "HRG",

    # ---------------- MOROCCO ----------------
    "casablanca": "CMN",
    "marrakech": "RAK",
    "rabat": "RBA",
    "fes": "FEZ",
    "tangier": "TNG",

    # ---------------- KENYA ----------------
    "nairobi": "NBO",
    "mombasa": "MBA",

    # ---------------- TANZANIA ----------------
    "dar es salaam": "DAR",
    "zanzibar": "ZNZ",
    "arusha": "ARK",

    # ---------------- ETHIOPIA ----------------
    "addis ababa": "ADD",

    # ---------------- NIGERIA ----------------
    "lagos": "LOS",
    "abuja": "ABV",

    # ---------------- CENTRAL ASIA ----------------
    "almaty": "ALA",
    "astana": "NQZ",

    "tashkent": "TAS",
    "samarkand": "SKD",

    "bishkek": "FRU",

    "dushanbe": "DYU",

    "ashgabat": "ASB",
}

def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    stop_words = [
        "flight", "flights", "ticket", "tickets", "trip", "travel",
        "plan", "complete", "days", "day", "including", "hotel",
        "hotels", "sightseeing", "under", "budget", "info", "information"
    ]
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words).strip()

def country_name_to_code(country_name: str):
    country_name = clean_text(country_name)
    if country_name in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[country_name]
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except LookupError:
        pass

    # detect country name inside longer text
    for country in pycountry.countries:
        if country.name.lower() in country_name:
            return country.alpha_2

    for alias,code in COUNTRY_ALIASES.items():
        if alias in country_name:
            return code

    return None



def airport_country_matches(airport: dict, country_code: str) -> bool:
    airport_country = str(airport.get("country", "")).upper().strip()

    if airport_country == country_code:
        return True

    try:
        country = pycountry.countries.get(alpha_2=country_code)
        if country and airport_country.lower() == country.name.lower():
            return True
    except Exception:
        pass

    return False

def get_best_airport_for_country(country_code: str):
    preferred = COUNTRY_MAIN_AIRPORT.get(country_code)

    if preferred and preferred in AIRPORTS:
        return preferred

    candidates = []

    for iata, airport in AIRPORTS.items():
        if not iata:
            continue

        if airport_country_matches(airport, country_code):
            name = str(airport.get("name", "")).lower()
            city = str(airport.get("city", "")).lower()

            score = 0

            if "international" in name:
                score += 50
            if "intl" in name:
                score += 40
            if "capital" in name:
                score += 20
            if city:
                score += 5

            candidates.append((score, iata))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]

def resolve_location_to_iata(location: str):
    """
    Converts country/city/airport/IATA into IATA code.

    Examples:
    Bangladesh -> DAC
    Japan -> NRT
    Dhaka -> DAC
    Tokyo -> NRT
    DAC -> DAC
    """

    if not location:
        return None

    raw_location = location.strip()

    # Direct IATA code
    if re.fullmatch(r"[A-Za-z]{3}", raw_location):
        code = raw_location.upper()
        if code in AIRPORTS:
            return code

    location_clean = clean_text(raw_location)

    if not location_clean:
        return None

    # City preferred airport
    if location_clean in CITY_MAIN_AIRPORT:
        return CITY_MAIN_AIRPORT[location_clean]

    # Country preferred airport
    country_code = country_name_to_code(location_clean)
    if country_code:
        airport = get_best_airport_for_country(country_code)
        if airport:
            return airport

    # Exact city match from airport database
    city_matches = []

    for iata, airport in AIRPORTS.items():
        city = str(airport.get("city", "")).lower().strip()
        name = str(airport.get("name", "")).lower().strip()

        score = 0

        if city == location_clean:
            score += 100
        elif location_clean in city:
            score += 70

        if location_clean in name:
            score += 50

        if "international" in name:
            score += 10

        if score > 0:
            city_matches.append((score, iata))

    if city_matches:
        city_matches.sort(reverse=True)
        return city_matches[0][1]

    return None




def find_location_mentions(query: str):
    """
    Finds country or city names inside a natural language query.
    """

    q = query.lower()
    mentions = []

    # Country aliases
    for alias in COUNTRY_ALIASES:
        if re.search(rf"\b{re.escape(alias)}\b", q):
            mentions.append(alias)

    # Country names from pycountry
    for country in pycountry.countries:
        name = country.name.lower()
        if len(name) >= 4 and re.search(rf"\b{re.escape(name)}\b", q):
            mentions.append(name)

    # City names from our preferred city map
    for city in CITY_MAIN_AIRPORT:
        if re.search(rf"\b{re.escape(city)}\b", q):
            mentions.append(city)

    # Remove duplicate while keeping order
    unique_mentions = []
    for item in mentions:
        if item not in unique_mentions:
            unique_mentions.append(item)

    return unique_mentions


def parse_route(query: str):
    """
    Returns:
    dep_iata, arr_iata

    Can return:
    None, None  -> global live flights
    DAC, NRT    -> filtered route
    DAC, None   -> all flights from DAC
    None, NRT   -> all flights to NRT
    """

    q = query.strip()
    q_lower = q.lower()

    # Global / all-country query
    global_keywords = [
        "all country",
        "all countries",
        "global flight",
        "global flights",
        "all flight",
        "all flights",
        "worldwide flight",
        "worldwide flights",
    ]

    if any(keyword in q_lower for keyword in global_keywords):
        return None, None

    # Direct IATA code route: DAC to NRT
    codes = re.findall(r"\b[A-Z]{3}\b", q)

    if len(codes) >= 2:
        dep = codes[0].upper()
        arr = codes[1].upper()
        return dep, arr

    # Pattern: from X to Y
    match = re.search(
        r"\bfrom\s+(.+?)\s+\bto\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        origin_text = match.group(1)
        dest_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: to Y from X
    match = re.search(
        r"\bto\s+(.+?)\s+\bfrom\s+(.+?)(?:\s+(?:on|for|under|including|with|in|at)\b|[.!?]|$)",
        q_lower,
    )

    if match:
        dest_text = match.group(1)
        origin_text = match.group(2)

        dep_iata = resolve_location_to_iata(origin_text)
        arr_iata = resolve_location_to_iata(dest_text)

        return dep_iata, arr_iata

    # Pattern: flights from X
    match = re.search(r"\bfrom\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        origin_text = match.group(1)
        dep_iata = resolve_location_to_iata(origin_text)
        return dep_iata, None

    # Pattern: flights to X
    match = re.search(r"\bto\s+(.+?)(?:[.!?]|$)", q_lower)

    if match:
        dest_text = match.group(1)
        arr_iata = resolve_location_to_iata(dest_text)
        return None, arr_iata

    # Fallback: find country/city mentions
    mentions = find_location_mentions(q)

    if len(mentions) >= 2:
        dep_iata = resolve_location_to_iata(mentions[0])
        arr_iata = resolve_location_to_iata(mentions[1])
        return dep_iata, arr_iata

    if len(mentions) == 1:
        arr_iata = resolve_location_to_iata(mentions[0])
        return DEFAULT_ORIGIN_IATA, arr_iata

    return None, None


def format_flight(flight: dict):
    airline = flight.get("airline", {}).get("name") or "Unknown airline"
    flight_number = flight.get("flight", {}).get("iata") or "Unknown flight number"
    status = flight.get("flight_status") or "Unknown"

    dep = flight.get("departure", {}) or {}
    arr = flight.get("arrival", {}) or {}

    dep_airport = dep.get("airport") or "Unknown departure airport"
    dep_iata = dep.get("iata") or "Unknown"
    dep_terminal = dep.get("terminal") or "N/A"
    dep_gate = dep.get("gate") or "N/A"
    dep_scheduled = dep.get("scheduled") or "Unknown"
    dep_delay = dep.get("delay")
    dep_delay_text = f"{dep_delay} minutes" if dep_delay is not None else "N/A"

    arr_airport = arr.get("airport") or "Unknown arrival airport"
    arr_iata = arr.get("iata") or "Unknown"
    arr_terminal = arr.get("terminal") or "N/A"
    arr_gate = arr.get("gate") or "N/A"
    arr_scheduled = arr.get("scheduled") or "Unknown"
    arr_delay = arr.get("delay")
    arr_delay_text = f"{arr_delay} minutes" if arr_delay is not None else "N/A"

    return f"""
Airline: {airline}
Flight: {flight_number}
Status: {status}

Departure:
- Airport: {dep_airport}
- IATA: {dep_iata}
- Terminal: {dep_terminal}
- Gate: {dep_gate}
- Scheduled: {dep_scheduled}
- Delay: {dep_delay_text}

Arrival:
- Airport: {arr_airport}
- IATA: {arr_iata}
- Terminal: {arr_terminal}
- Gate: {arr_gate}
- Scheduled: {arr_scheduled}
- Delay: {arr_delay_text}
""".strip()


def search_flights(query: str, limit: int = 10):
    if not API_KEY:
        return (
            "Flight API error: AVIATIONSTACK_API_KEY is missing.\n"
            "Please add this in your .env file:\n"
            "AVIATIONSTACK_API_KEY=your_api_key_here"
        )

    dep_iata, arr_iata = parse_route(query)

    params = {
        "access_key": API_KEY,
        "limit": min(limit, 100),
    }

    if dep_iata:
        params["dep_iata"] = dep_iata

    if arr_iata:
        params["arr_iata"] = arr_iata

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Flight API request failed: {e}"
    except ValueError:
        return "Flight API returned invalid JSON."

    if "error" in data:
        error = data["error"]
        return (
            "Flight API error:\n"
            f"Code: {error.get('code', 'Unknown')}\n"
            f"Message: {error.get('message', 'Unknown error')}"
        )

    flight_data = data.get("data", [])

    if not flight_data:
        route_text = ""

        if dep_iata and arr_iata:
            route_text = f" for route {dep_iata} to {arr_iata}"
        elif dep_iata:
            route_text = f" from {dep_iata}"
        elif arr_iata:
            route_text = f" to {arr_iata}"

        return (
            f"No live flight data found{route_text}.\n\n"
            "Note: AviationStack provides live/status flight data, not ticket prices. "
            "For actual fare prices, use a flight-pricing API such as Amadeus."
        )

    route_info = "Global live flights"

    if dep_iata and arr_iata:
        route_info = f"Live flights from {dep_iata} to {arr_iata}"
    elif dep_iata:
        route_info = f"Live flights from {dep_iata}"
    elif arr_iata:
        route_info = f"Live flights to {arr_iata}"

    formatted_flights = [format_flight(flight) for flight in flight_data[:limit]]

    return f"{route_info}\n\n" + "\n\n---\n\n".join(formatted_flights)


if __name__ == "__main__":
    print(search_flights("Plan a 7 days Japan trip from Bangladesh"))
    print("\n" + "=" * 80 + "\n")
    print(search_flights("all country flight info"))