from enum import Enum


brand = "(?P<brand>huggies|pampers|babysec)"
size_only = "(?P<size>pr|rn|p|m|g|xg|xxg)"
size = f"\s(pr|rn|p|m|g|xg|xxg)*\s*(\\\/|\-)*\s*{size_only}"
units_label_1 = "x\s*(?P<units>[0-9]+)"
units_label_2 = "\[(?P<units>[0-9]+)\s*uni\.{0,1}\]"
units_label_3 = "\s+(?P<units>[0-9]+)\s*(u|uni|unid){1}\.{0,1}"
DIAPERS_REGEX = [
    f".*{brand}.*{size}.*{units_label_1}",
    f".*{brand}.*{size}.*{units_label_2}",
    f".*{brand}.*{size}.*{units_label_3}",
    f".*{size}.*{brand}.*{units_label_3}",
    f".*{brand}.*",
    f".*{brand}.*{units_label_1}.*{size}",
]

DIAPERS_NO_BRAND_REGEX = [
    f"{size_only}.*{units_label_1}",
    f"{size_only}.*{units_label_2}",
    f"{size_only}.*{units_label_3}",
]

class DiaperBrand(Enum):
    BABYSEC = "babysec"
    HUGGIES = "huggies"
    PAMPERS = "pampers"

    @classmethod
    def brands(self):
        return [e.value for e in DiaperBrand.__members__.values()]


DIAPER_SIZES = {
    DiaperBrand.HUGGIES.value: {
        "pr": {"min": None, "max": 2.2},
        "rn": {"min": None, "max": 4},
        "p": {"min": 3.5, "max": 6},
        "m": {"min": 5.5, "max": 9.5},
        "g": {"min": 9, "max": 12.5},
        "xg": {"min": 12, "max": 15},
        "xxg": {"min": 14, "max": None},
    },
    DiaperBrand.PAMPERS.value: {
        "rn": {"min": None, "max": 4.5},
        "rn+": {"min": 3, "max": 6},
        "p": {"min": 5, "max": 7.5},
        "m": {"min": 6, "max": 9.5},
        "g": {"min": 9, "max": 12},
        "xg": {"min": 12, "max": 15},
        "xxg": {"min": 14, "max": None},
    },
    DiaperBrand.BABYSEC.value: {
        "rn": {"min": None, "max": 4.5},
        "p": {"min": None, "max": 6},
        "m": {"min": 5, "max": 9.5},
        "g": {"min": 8.5, "max": 12},
        "xg": {"min": 11, "max": 15},
        "xxg": {"min": 13, "max": None},
    },
}
