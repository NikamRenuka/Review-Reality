"""Group raw product listings into product families.

Why: the same review is often copied onto every colour or size of a product
(for example, a Fire HD 8 in Black and in Tangerine). If we treated each
listing as a separate product, one review would be counted many times.
So we group listings into families, then remove the copies inside a family.

Rules are checked from top to bottom; the first matching rule wins.
Order matters: chargers first (their names mention the devices they charge),
then devices, then other accessories (so "Kid-Proof Case" stays a tablet).
"""
import re

# (regular expression, product family, category)
FAMILY_RULES = [
    (r"charger|adapter|charging kit|usb cable|micro-usb cable", "Chargers & Cables", "Accessories"),
    (r"hot handle|litter box|dog crate|kennel|nespresso|coconut water|file folder", "Other (non-electronics)", "Other"),
    (r"\baaa\b.*batter", "AmazonBasics AAA Batteries", "Batteries"),
    (r"\baa\b.*batter", "AmazonBasics AA Batteries", "Batteries"),
    (r"kids edition", "Fire Kids Edition Tablet", "Tablets"),
    (r"fire tv", "Fire TV", "Streaming Media"),
    (r"echo show", "Echo Show", "Smart Speakers"),
    (r"echo plus", "Echo Plus", "Smart Speakers"),
    (r"echo dot|echo spot", "Echo Dot & Spot", "Smart Speakers"),
    (r"\btap\b", "Amazon Tap", "Smart Speakers"),
    (r"\becho\b", "Echo", "Smart Speakers"),
    (r"fire hd 10", "Fire HD 10 Tablet", "Tablets"),
    (r"fire hd 8", "Fire HD 8 Tablet", "Tablets"),
    (r"fire tablet.*\b7\b|fire 7|kindle fire 16gb 7|fire 16gb \(5th gen", "Fire 7 Tablet", "Tablets"),
    (r"kindle fire hd \(", "Fire HD (other models)", "Tablets"),
    (r"kindle oasis", "Kindle Oasis", "E-readers"),
    (r"kindle voyage", "Kindle Voyage", "E-readers"),
    (r"paperwhite", "Kindle Paperwhite", "E-readers"),
    (r"kindle e-reader|kindle keyboard", "Kindle E-reader", "E-readers"),
    (r"\bcase\b|\bcover\b|sleeve|laptop|keyboard for android|speaker wire|usb 3\.0 cable|cd/dvd binder",
     "Other Accessories", "Accessories"),
]

OTHER_FAMILY = ("Other (uncategorised)", "Other")

# A few rows in the oldest file have no product name, and no other row with the
# same ASIN has one either. These names were read from the product "slug" in
# the raw `keys` column (for example "amazonfiretvstreamingmediaplayer/b00u3fpn4u").
ASIN_NAMES = {
    "B00U3FPN4U": "Amazon Fire TV Streaming Media Player (2015)",
    "B00X4WHP5E": "Echo (Black)",
    "B018Y23P7K": "Fire Tablet, 7 Display, Wi-Fi, 8 GB - Includes Special Offers, Tangerine",
    "B002Y27P6Y": "Kindle DX Leather Cover, Black",
    "B00LW9XOJM": "Amazon Fire HD 6 Standing Protective Case, Cayenne Red",
    "B006GWO5NE": "Amazon Kindle Fire 5ft USB to Micro-USB Cable",
    "B006GWO5WK": "Amazon Kindle Fire HD 9W PowerFast Adapter Charger",
    "B00QL1ZN3G": "Amazon 5W USB Official OEM Charger and Power Adapter",
    "B00BFJAHF8": "Coconut Water Red Tea 16.5 Oz (pack of 12)",
}

_COMPILED = [(re.compile(pattern, re.IGNORECASE), family, category) for pattern, family, category in FAMILY_RULES]


def clean_listing_name(name):
    """Tidy a raw listing name: some names in the oldest file end with ',,,' and repeat on a new line."""
    if not isinstance(name, str):
        return ""
    first_line = re.split(r"[\r\n]+", name.strip())[0]
    return first_line.rstrip(", ").strip()


def product_family(name):
    """Return (family, category) for a listing name."""
    text = clean_listing_name(name)
    for pattern, family, category in _COMPILED:
        if pattern.search(text):
            return family, category
    return OTHER_FAMILY
