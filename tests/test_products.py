import pytest

from review_reality.products import clean_listing_name, product_family


@pytest.mark.parametrize(
    "name, family",
    [
        ("AmazonBasics AAA Performance Alkaline Batteries (36 Count)", "AmazonBasics AAA Batteries"),
        ("AmazonBasics AA Performance Alkaline Batteries (48 Count) - Packaging May Vary", "AmazonBasics AA Batteries"),
        # Colour variants of one tablet must land in the same family.
        ("All-New Fire HD 8 Tablet, 8 HD Display, Wi-Fi, 16 GB - Includes Special Offers, Black", "Fire HD 8 Tablet"),
        ("Fire HD 8 Tablet with Alexa, 8 HD Display, 16 GB, Tangerine - with Special Offers", "Fire HD 8 Tablet"),
        # "Kid-Proof Case" is part of a tablet name, not an accessory.
        ("Fire Kids Edition Tablet, 7 Display, Wi-Fi, 16 GB, Pink Kid-Proof Case", "Fire Kids Edition Tablet"),
        # "Charging Cover" is part of an e-reader name, not an accessory.
        ("Kindle Oasis E-reader with Leather Charging Cover - Merlot, 6 High-Resolution Display", "Kindle Oasis"),
        # A charger that mentions devices is still a charger.
        ("Amazon Echo and Fire TV Power Adapter", "Chargers & Cables"),
        ("Amazon Fire Hd 6 Standing Protective Case(4th Generation - 2014 Release), Cayenne Red", "Other Accessories"),
        ("Amazon Kindle Fire Hd (3rd Generation) 8gb", "Fire HD (other models)"),
        ("Echo (White),,,\r\nEcho (White),,,", "Echo"),
        ("Amazon Echo Show Alexa-enabled Bluetooth Speaker with 7\" Screen", "Echo Show"),
        ("Cat Litter Box Covered Tray Kitten Extra Large Enclosed Hooded Hidden Toilet", "Other (non-electronics)"),
        ("Something we have never seen", "Other (uncategorised)"),
    ],
)
def test_product_family(name, family):
    assert product_family(name)[0] == family


def test_clean_listing_name_removes_repeated_line_and_commas():
    assert clean_listing_name("Echo (White),,,\r\nEcho (White),,,") == "Echo (White)"


def test_clean_listing_name_handles_missing():
    assert clean_listing_name(None) == ""
