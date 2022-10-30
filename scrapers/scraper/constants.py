from enum import Enum


brand = "(?P<brand>huggies|pampers|babysec|estrella)"
size_only = "(?P<size>pr|rn\+|rn|p|m|g|xg|xxg)"
size = f"\s(pr|rn|p|m|g|xg|xxg)*\s*(\\\/|\-)*\s*{size_only}"
units_label_1 = "x\s*(?P<units>[0-9]+)"
units_label_2 = "\[(?P<units>[0-9]+)\s*uni\.{0,1}\]"
units_label_3 = "\s+(?P<units>[0-9]+)\s*(u|uni|unid){1}\.{0,1}"
units_label_4 = "(\(|\u00d7)\s*(?P<units>[0-9]+).*"
units_label_5 = "\s(?P<units>[0-9]+)\spa"
units_label_6 = "\s(?P<units>[0-9]+)$"
DIAPERS_REGEX = [
    f".*{brand}.*{size}.*{units_label_1}",
    f".*{brand}.*{size}.*{units_label_2}",
    f".*{brand}.*{size}.*{units_label_3}",
    f".*{size}.*{brand}.*{units_label_3}",
    f".*{brand}.*{size}.*{units_label_4}",
    f".*{brand}.*{size}.*{units_label_5}",
    f".*{brand}.*{size}.*{units_label_6}",
    f".*{brand}.*{units_label_1}.*(mega)*{size}(mega)*",
    f".*{brand}.*",
]

DIAPERS_NO_BRAND_REGEX = [
    f"{size_only}.*{units_label_1}",
    f"{size_only}.*{units_label_2}",
    f"{size_only}.*{units_label_3}",
    f"{size_only}.*{units_label_4}",
    f"{size_only}.*{units_label_5}",
    f"{size_only}.*{units_label_6}",
]

class DiaperBrand(Enum):
    BABYSEC = "babysec"
    HUGGIES = "huggies"
    PAMPERS = "pampers"
    ESTRELLA = "estrella"

    @classmethod
    def brands(self):
        return [e.value for e in DiaperBrand.__members__.values()]


DIAPER_SIZES = {
    DiaperBrand.HUGGIES.value: {
        "pr": {"min": 0, "max": 2.2},
        "rn": {"min": 0, "max": 4},
        "p": {"min": 3.5, "max": 6},
        "m": {"min": 5.5, "max": 9.5},
        "g": {"min": 9, "max": 12.5},
        "xg": {"min": 12, "max": 15},
        "xxg": {"min": 14, "max": 20},
    },
    DiaperBrand.PAMPERS.value: {
        "rn": {"min": 0, "max": 4.5},
        "rn+": {"min": 3, "max": 6},
        "p": {"min": 5, "max": 7.5},
        "m": {"min": 6, "max": 9.5},
        "g": {"min": 9, "max": 12},
        "xg": {"min": 12, "max": 15},
        "xxg": {"min": 14, "max": 20},
    },
    DiaperBrand.BABYSEC.value: {
        "rn": {"min": 0, "max": 4.5},
        "p": {"min": 0, "max": 6},
        "m": {"min": 5, "max": 9.5},
        "g": {"min": 8.5, "max": 12},
        "xg": {"min": 11, "max": 15},
        "xxg": {"min": 13, "max": 20},
    },
    DiaperBrand.ESTRELLA.value: {
        "p": {"min": 5, "max": 7.5},
        "m": {"min": 6, "max": 9.5},
        "g": {"min": 9, "max": 12},
        "xg": {"min": 12, "max": 15},
        "xxg": {"min": 14, "max": 20},
    },
}


ROSARIO = [('82084', 'Rosario')]
SAN_JUAN = [('82084', 'Rosario')]
SANTA_ROSA = [('42021', 'Capital')]
BAHIA_BLANCA = [('06056', 'Bahía Blanca')]
SANTA_CRUZ = [
    ("26077", "Rawson"),
    ("26021", "Escalante"),
    ("26007", "Biedma"),
]
GBA = [
    ('06028', 'Almirante Brown'),
    ('06035', 'Avellaneda'),
    ('06091', 'Berazategui'),
    ('06252', 'Escobar'),
    ('06260', 'Esteban Echeverría'),
    ('06270', 'José M. Ezeiza'),
    ('06274', 'Florencio Varela'),
    ('06371', 'Ciudad Libertador San Martín'),
    ('06408', 'Hurlingham'),
    ('06410', 'Ituzaingó'),
    ('06412', 'José C. Paz'),
    ('06427', 'La Matanza'),
    ('06434', 'Lanús'),
    ('06490', 'Lomas de Zamora'),
    ('06515', 'Malvinas Argentinas'),
    ('06539', 'Merlo'),
    ('06560', 'Moreno'),
    ('06568', 'Morón'),
    ('06638', 'Pilar'),
    ('06648', 'Presidente Perón'),
    ('06658', 'Quilmes'),
    ('06749', 'San Fernando'),
    ('06756', 'San Isidro'),
    ('06760', 'San Miguel'),
    ('06805', 'Tigre'),
    ('06840', 'Tres de Febrero'),
    ('06861', 'Vicente López')
]

CABA = [
    ('02014', 'Comuna 2'),
    ('02056', 'Comuna 8'),
    ('02098', 'Comuna 14'),
    ('02021', 'Comuna 3'),
    ('02063', 'Comuna 9'),
    ('02049', 'Comuna 7'),
    ('02070', 'Comuna 10'),
    ('02077', 'Comuna 11'),
    ('02042', 'Comuna 6'),
    ('02091', 'Comuna 13'),
    ('02007', 'Comuna 1'),
    ('02028', 'Comuna 4'),
    ('02035', 'Comuna 5'),
    ('02084', 'Comuna 12'),
    ('02105', 'Comuna 15')
]