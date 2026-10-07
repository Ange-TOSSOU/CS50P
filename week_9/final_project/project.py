# --- Imports ---

import argparse
import math
import sys
import textwrap
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import lru_cache

# --- Errors Handling ---


class ConverterError(Exception):
    """Base class for every error raised by the conversion engine."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidNumberError(ConverterError):
    """Raised when the value to convert cannot be read as a finite number."""

    def __init__(self, value: object = None) -> None:
        self.value = value

        message = "InvalidNumberError"

        # If possible, specify which data is in fault.
        if value is not None:
            message += f": '{value}' is not a valid number"

        super().__init__(message + ".")


class UnknownUnitError(ConverterError):
    """Raised when a unit name matches no unit known to the registry.

    ``name`` is the text the user typed. ``suggestions`` holds the closest
    known names (possibly none).
    """

    def __init__(
        self, name: None | str = None, suggestions: None | list[str] = None
    ) -> None:
        self.name = name
        # Make suggestions immutable.
        if suggestions:
            self.suggestions = tuple(suggestions)
        else:
            self.suggestions = ()

        message = "UnknownUnitError"

        # If possible, specify which unit is not recognized and give suggestions.
        if self.name is not None:
            message += f": unknown unit '{self.name}'."

            # Add suggestions if provided.
            if self.suggestions:
                options = ", ".join(
                    f"'{suggestion}'" for suggestion in self.suggestions
                )
                message += f" Did you mean {options}?"
        else:
            message += "."

        super().__init__(message)


class IncompatibleUnitsError(ConverterError):
    """Raised when two units belong to different categories."""

    def __init__(
        self, from_category: None | str = None, to_category: None | str = None
    ) -> None:
        self.from_category = from_category
        self.to_category = to_category

        message = "IncompatibleUnitsError"

        # If possible, specify which type of conversion is in fault.
        if (from_category is not None) and (to_category is not None):
            message += f": cannot convert from '{from_category}' to '{to_category}'"

        super().__init__(message + ".")


class RegistryError(Exception):
    """Raised when unit data is invalid (a developer error, not a user error)."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        self.message = f"RegistryError: {detail}"
        super().__init__(self.message)


class UnsupportedUnitError(ConverterError):
    """Raised when a unit name is recognized but deliberately not supported.

    Used for units without a single worldwide definition (for example the
    gallon, whose size differs between countries). ``name`` is the text the
    user typed.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"UnsupportedUnitError: '{name}' is not supported.")


# --- Models ---

""" Data types describing units, categories and conversion results. """


@dataclass
class Unit:
    """A unit of measurement, defined relative to its category's base unit.

    A value converts to the base unit with ``value * factor + offset``.
    For purely proportional units the offset is 0.
    """

    id: str
    name: str
    symbol: str
    factor: float
    aliases: tuple[str, ...] = ()
    offset: float = 0.0


@dataclass
class Category:
    """A group of units that can be converted into one another."""

    name: str
    base_unit_id: str
    units: tuple[Unit, ...]


@dataclass
class Quantity:
    """A numeric value expressed in a given unit, at full precision."""

    value: float
    unit: Unit


# --- Factors ---

"""Units factors: decimal multiples and sub-multiples.

Source: SI Brochure (BIPM) for the metric units.
"""

FACTORS: dict[str, float] = {
    "deca": 1e1,
    "hecto": 1e2,
    "kilo": 1e3,
    "mega": 1e6,
    "giga": 1e9,
    "tera": 1e12,
    "peta": 1e15,
    "exa": 1e18,
    "zetta": 1e21,
    "yotta": 1e24,
    "ronna": 1e27,
    "quetta": 1e30,
    "deci": 1e-1,
    "centi": 1e-2,
    "milli": 1e-3,
    "micro": 1e-6,
    "nano": 1e-9,
    "pico": 1e-12,
    "femto": 1e-15,
    "atto": 1e-18,
    "zepto": 1e-21,
    "yocto": 1e-24,
    "ronto": 1e-27,
    "quecto": 1e-30,
}


# --- Data ---

"""Time units. Base unit: second.

The module is called "duration" (the category is still named "time") so that
it cannot be confused with the standard-library module of the same name.
Months and years are excluded because their length varies.

All units are filed under METRIC (decision D39), although minute, hour, day
and week are not strictly metric: they are non-SI units accepted for use with
the SI (SI Brochure, BIPM).
"""

DURATION = Category(
    name="time",
    base_unit_id="second",
    units=(
        Unit(
            id="millisecond",
            name="millisecond",
            symbol="ms",
            factor=0.001,
            aliases=("milliseconds",),
        ),
        Unit(
            id="second",
            name="second",
            symbol="s",
            factor=1,
            aliases=("seconds", "sec", "secs"),
        ),
        Unit(
            id="minute",
            name="minute",
            symbol="min",
            factor=60,  # 60 seconds
            aliases=("minutes", "mins"),
        ),
        Unit(
            id="hour",
            name="hour",
            symbol="h",
            factor=60 * 60,  # 60 minutes
            aliases=("hours", "hr", "hrs"),
        ),
        Unit(
            id="day",
            name="day",
            symbol="d",
            factor=60 * 60 * 24,  # 24 hours
            aliases=("days",),
        ),
        Unit(
            id="week",
            name="week",
            symbol="wk",
            factor=60 * 60 * 24 * 7,  # 7 days
            aliases=("weeks", "wks"),
        ),
    ),
)


"""Length units. Base unit: meter.

Sources: SI Brochure (BIPM) for the metric units; the international yard and
pound agreement (1959) for inch, foot, yard and mile; the International
Hydrographic Conference (1929) for the nautical mile.
"""

LENGTH = Category(
    name="length",
    base_unit_id="meter",
    units=(
        Unit(
            id="millimeter",
            name="millimeter",
            symbol="mm",
            factor=FACTORS["milli"],
            aliases=("millimeters", "millimetre", "millimetres"),
        ),
        Unit(
            id="centimeter",
            name="centimeter",
            symbol="cm",
            factor=FACTORS["centi"],
            aliases=("centimeters", "centimetre", "centimetres"),
        ),
        Unit(
            id="decimeter",
            name="decimeter",
            symbol="dm",
            factor=FACTORS["deci"],
            aliases=("decimeters", "decimetre", "decimetres"),
        ),
        Unit(
            id="meter",
            name="meter",
            symbol="m",
            factor=1,
            aliases=("meters", "metre", "metres"),
        ),
        Unit(
            id="kilometer",
            name="kilometer",
            symbol="km",
            factor=FACTORS["kilo"],
            aliases=("kilometers", "kilometre", "kilometres"),
        ),
        Unit(
            id="inch",
            name="inch",
            symbol="in",
            factor=0.0254,
            aliases=("inches",),
        ),
        Unit(
            id="foot",
            name="foot",
            symbol="ft",
            factor=0.3048006096,
            aliases=("feet",),
        ),
        Unit(
            id="yard",
            name="yard",
            symbol="yd",
            factor=0.91440183,
            aliases=("yards",),
        ),
        Unit(
            id="mile",
            name="mile",
            symbol="mi",
            factor=1609.344,  # exact by definition (international mile)
            aliases=("miles",),
        ),
        Unit(
            id="nautical_mile",
            name="nautical mile",
            symbol="nmi",
            factor=1852,
            aliases=("nautical miles",),
        ),
    ),
)


"""Mass units. Base unit: kilogram.

Sources: SI Brochure (BIPM) for the metric units; the international yard and
pound agreement (1959) for the pound, from which the ounce and the stone are
derived (1/16 and 14 pounds). The ounce is the avoirdupois ounce.
"""

_POUND_IN_KG = 0.45359237
_SCALE = 1e-3

MASS = Category(
    name="mass",
    base_unit_id="kilogram",
    units=(
        Unit(
            id="milligram",
            name="milligram",
            symbol="mg",
            factor=FACTORS["milli"] * _SCALE,
            aliases=("milligrams", "milligramme", "milligrammes"),
        ),
        Unit(
            id="gram",
            name="gram",
            symbol="g",
            factor=_SCALE,
            aliases=("grams", "gramme", "grammes"),
        ),
        Unit(
            id="kilogram",
            name="kilogram",
            symbol="kg",
            factor=FACTORS["kilo"] * _SCALE,
            aliases=("kilograms", "kilogramme", "kilogrammes", "kilo", "kilos"),
        ),
        Unit(
            id="metric_ton",
            name="metric ton",
            symbol="t",
            factor=1000,
            aliases=("metric tons", "tonne", "tonnes"),
        ),
        Unit(
            id="ounce",
            name="ounce",
            symbol="oz",
            factor=_POUND_IN_KG / 16,
            aliases=("ounces",),
        ),
        Unit(
            id="pound",
            name="pound",
            symbol="lb",
            factor=_POUND_IN_KG,
            aliases=("pounds", "lbs"),
        ),
        Unit(
            id="stone",
            name="stone",
            symbol="st",
            factor=_POUND_IN_KG * 14,
            aliases=("stones",),
        ),
    ),
)


"""Temperature units (absolute temperatures only). Base unit: kelvin.

A temperature converts to kelvin with ``value * factor + offset``.

Sources: SI Brochure (BIPM): 0 degrees Celsius = 273.15 K. Fahrenheit is
defined from Celsius: F = C * 9/5 + 32, so K = (F + 459.67) * 5/9.

Symbols are plain text (C, F, K), and input is plain text too (decision D43):
"celsius" works, the degree sign is not accepted.
"""

TEMPERATURE = Category(
    name="temperature",
    base_unit_id="kelvin",
    units=(
        Unit(
            id="kelvin",
            name="kelvin",
            symbol="K",
            factor=1,
            aliases=("kelvins",),
        ),
        Unit(
            id="celsius",
            name="celsius",
            symbol="C",
            factor=1,
            offset=273.15,
            aliases=("degree celsius", "degrees celsius", "centigrade"),
        ),
        Unit(
            id="fahrenheit",
            name="fahrenheit",
            symbol="F",
            factor=5 / 9,
            offset=459.67,
            aliases=("degree fahrenheit", "degrees fahrenheit"),
        ),
    ),
)


"""Volume units. Base unit: liter.

Only units with a single worldwide definition are included. Gallons, pints,
fluid ounces, cups and spoons are excluded on purpose: their size differs
between countries.

Sources: SI Brochure (BIPM) for the metric units. The cubic inch and cubic
foot follow from the exact inch (0.0254 m) and foot (0.3048 m):
0.0254 ** 3 m3 = 0.016387064 L and 0.3048 ** 3 m3 = 28.316846592 L.
"""

VOLUME = Category(
    name="volume",
    base_unit_id="liter",
    units=(
        Unit(
            id="milliliter",
            name="milliliter",
            symbol="ml",
            factor=FACTORS["milli"],
            aliases=("milliliters", "millilitre", "millilitres"),
        ),
        Unit(
            id="cubic_centimeter",
            name="cubic centimeter",
            symbol="cm3",
            factor=FACTORS["milli"],  # 1 cm3 = 1 mL
            aliases=(
                "cubic centimeters",
                "cubic centimetre",
                "cubic centimetres",
                "cc",
            ),
        ),
        Unit(
            id="liter",
            name="liter",
            symbol="l",
            factor=1,
            aliases=("liters", "litre", "litres"),
        ),
        Unit(
            id="cubic_meter",
            name="cubic meter",
            symbol="m3",
            factor=FACTORS["kilo"],  # 1 m3 = 1000 L
            aliases=("cubic meters", "cubic metre", "cubic metres"),
        ),
        Unit(
            id="cubic_inch",
            name="cubic inch",
            symbol="in3",
            factor=0.016387064,  # 0.0254 ** 3 m3, in liters
            aliases=("cubic inches",),
        ),
        Unit(
            id="cubic_foot",
            name="cubic foot",
            symbol="ft3",
            factor=28.316846592,  # 0.3048 ** 3 m3, in liters
            aliases=("cubic feet",),
        ),
    ),
)


"""Unit names that are recognized but deliberately not supported.

These units have no single worldwide definition: their size differs between
countries (gallon, pint, ton, fluid ounce, cup, tablespoon, teaspoon) or
varies over time (month, year). A user who types one of them gets a clear
message, not a generic "unknown unit" error.

Plurals and common abbreviations are listed explicitly. The registry checks
that none of these names is also a supported name.
"""

UNSUPPORTED: tuple[str, ...] = (
    # Not integrated yet
    "decameter",
    "decameters",
    "decametre",
    "decametres",
    "decasecond",
    "decaseconds",
    "decagram",
    "decagrams",
    "decagramme",
    "decagrammes",
    "decacelcius",
    "decadegree celsius",
    "decadegrees celsius",
    "decacentigrade",
    "decakelvin",
    "decakelvins",
    "decafahrenheit",
    "decadegree fahrenheit",
    "decadegrees fahrenheit",
    "decaliter",
    "decaliters",
    "decalitre",
    "decalitres",
    "kilosecond",
    "kiloseconds",
    "kilocelcius",
    "kilodegree celsius",
    "kilodegrees celsius",
    "kilocentigrade",
    "kilokelvin",
    "kilokelvins",
    "kilofahrenheit",
    "kilodegree fahrenheit",
    "kilodegrees fahrenheit",
    "kiloliter",
    "kiloliters",
    "kilolitre",
    "kilolitres",
    "megameter",
    "megameters",
    "megametre",
    "megametres",
    "megasecond",
    "megaseconds",
    "megagram",
    "megagrams",
    "megagramme",
    "megagrammes",
    "megacelcius",
    "megadegree celsius",
    "megadegrees celsius",
    "megacentigrade",
    "megakelvin",
    "megakelvins",
    "megafahrenheit",
    "megadegree fahrenheit",
    "megadegrees fahrenheit",
    "megaliter",
    "megaliters",
    "megalitre",
    "megalitres",
    "gigameter",
    "gigameters",
    "gigametre",
    "gigametres",
    "gigasecond",
    "gigaseconds",
    "gigagram",
    "gigagrams",
    "gigagramme",
    "gigagrammes",
    "gigacelcius",
    "gigadegree celsius",
    "gigadegrees celsius",
    "gigacentigrade",
    "gigakelvin",
    "gigakelvins",
    "gigafahrenheit",
    "gigadegree fahrenheit",
    "gigadegrees fahrenheit",
    "gigaliter",
    "gigaliters",
    "gigalitre",
    "gigalitres",
    "terameter",
    "terameters",
    "terametre",
    "terametres",
    "terasecond",
    "teraseconds",
    "teragram",
    "teragrams",
    "teragramme",
    "teragrammes",
    "teracelcius",
    "teradegree celsius",
    "teradegrees celsius",
    "teracentigrade",
    "terakelvin",
    "terakelvins",
    "terafahrenheit",
    "teradegree fahrenheit",
    "teradegrees fahrenheit",
    "teraliter",
    "teraliters",
    "teralitre",
    "teralitres",
    "petameter",
    "petameters",
    "petametre",
    "petametres",
    "petasecond",
    "petaseconds",
    "petagram",
    "petagrams",
    "petagramme",
    "petagrammes",
    "petacelcius",
    "petadegree celsius",
    "petadegrees celsius",
    "petacentigrade",
    "petakelvin",
    "petakelvins",
    "petafahrenheit",
    "petadegree fahrenheit",
    "petadegrees fahrenheit",
    "petaliter",
    "petaliters",
    "petalitre",
    "petalitres",
    "exameter",
    "exameters",
    "exametre",
    "exametres",
    "exasecond",
    "exaseconds",
    "exagram",
    "exagrams",
    "exagramme",
    "exagrammes",
    "exacelcius",
    "exadegree celsius",
    "exadegrees celsius",
    "exacentigrade",
    "exakelvin",
    "exakelvins",
    "exafahrenheit",
    "exadegree fahrenheit",
    "exadegrees fahrenheit",
    "exaliter",
    "exaliters",
    "exalitre",
    "exalitres",
    "zettameter",
    "zettameters",
    "zettametre",
    "zettametres",
    "zettasecond",
    "zettaseconds",
    "zettagram",
    "zettagrams",
    "zettagramme",
    "zettagrammes",
    "zettacelcius",
    "zettadegree celsius",
    "zettadegrees celsius",
    "zettacentigrade",
    "zettakelvin",
    "zettakelvins",
    "zettafahrenheit",
    "zettadegree fahrenheit",
    "zettadegrees fahrenheit",
    "zettaliter",
    "zettaliters",
    "zettalitre",
    "zettalitres",
    "yottameter",
    "yottameters",
    "yottametre",
    "yottametres",
    "yottasecond",
    "yottaseconds",
    "yottagram",
    "yottagrams",
    "yottagramme",
    "yottagrammes",
    "yottacelcius",
    "yottadegree celsius",
    "yottadegrees celsius",
    "yottacentigrade",
    "yottakelvin",
    "yottakelvins",
    "yottafahrenheit",
    "yottadegree fahrenheit",
    "yottadegrees fahrenheit",
    "yottaliter",
    "yottaliters",
    "yottalitre",
    "yottalitres",
    "ronnameter",
    "ronnameters",
    "ronnametre",
    "ronnametres",
    "ronnasecond",
    "ronnaseconds",
    "ronnagram",
    "ronnagrams",
    "ronnagramme",
    "ronnagrammes",
    "ronnacelcius",
    "ronnadegree celsius",
    "ronnadegrees celsius",
    "ronnacentigrade",
    "ronnakelvin",
    "ronnakelvins",
    "ronnafahrenheit",
    "ronnadegree fahrenheit",
    "ronnadegrees fahrenheit",
    "ronnaliter",
    "ronnaliters",
    "ronnalitre",
    "ronnalitres",
    "quettameter",
    "quettameters",
    "quettametre",
    "quettametres",
    "quettasecond",
    "quettaseconds",
    "quettagram",
    "quettagrams",
    "quettagramme",
    "quettagrammes",
    "quettacelcius",
    "quettadegree celsius",
    "quettadegrees celsius",
    "quettacentigrade",
    "quettakelvin",
    "quettakelvins",
    "quettafahrenheit",
    "quettadegree fahrenheit",
    "quettadegrees fahrenheit",
    "quettaliter",
    "quettaliters",
    "quettalitre",
    "quettalitres",
    "decisecond",
    "deciseconds",
    "decigram",
    "decigrams",
    "decigramme",
    "decigrammes",
    "decicelcius",
    "decidegree celsius",
    "decidegrees celsius",
    "decicentigrade",
    "decikelvin",
    "decikelvins",
    "decifahrenheit",
    "decidegree fahrenheit",
    "decidegrees fahrenheit",
    "deciliter",
    "deciliters",
    "decilitre",
    "decilitres",
    "centisecond",
    "centiseconds",
    "centigram",
    "centigrams",
    "centigramme",
    "centigrammes",
    "centicelcius",
    "centidegree celsius",
    "centidegrees celsius",
    "centicentigrade",
    "centikelvin",
    "centikelvins",
    "centifahrenheit",
    "centidegree fahrenheit",
    "centidegrees fahrenheit",
    "centiliter",
    "centiliters",
    "centilitre",
    "centilitres",
    "millicelcius",
    "millidegree celsius",
    "millidegrees celsius",
    "millicentigrade",
    "millikelvin",
    "millikelvins",
    "millifahrenheit",
    "millidegree fahrenheit",
    "millidegrees fahrenheit",
    "micrometer",
    "micrometers",
    "micrometre",
    "micrometres",
    "microsecond",
    "microseconds",
    "microgram",
    "micrograms",
    "microgramme",
    "microgrammes",
    "microcelcius",
    "microdegree celsius",
    "microdegrees celsius",
    "microcentigrade",
    "microkelvin",
    "microkelvins",
    "microfahrenheit",
    "microdegree fahrenheit",
    "microdegrees fahrenheit",
    "microliter",
    "microliters",
    "microlitre",
    "microlitres",
    "nanometer",
    "nanometers",
    "nanometre",
    "nanometres",
    "nanosecond",
    "nanoseconds",
    "nanogram",
    "nanograms",
    "nanogramme",
    "nanogrammes",
    "nanocelcius",
    "nanodegree celsius",
    "nanodegrees celsius",
    "nanocentigrade",
    "nanokelvin",
    "nanokelvins",
    "nanofahrenheit",
    "nanodegree fahrenheit",
    "nanodegrees fahrenheit",
    "nanoliter",
    "nanoliters",
    "nanolitre",
    "nanolitres",
    "picometer",
    "picometers",
    "picometre",
    "picometres",
    "picosecond",
    "picoseconds",
    "picogram",
    "picograms",
    "picogramme",
    "picogrammes",
    "picocelcius",
    "picodegree celsius",
    "picodegrees celsius",
    "picocentigrade",
    "picokelvin",
    "picokelvins",
    "picofahrenheit",
    "picodegree fahrenheit",
    "picodegrees fahrenheit",
    "picoliter",
    "picoliters",
    "picolitre",
    "picolitres",
    "femtometer",
    "femtometers",
    "femtometre",
    "femtometres",
    "femtosecond",
    "femtoseconds",
    "femtogram",
    "femtograms",
    "femtogramme",
    "femtogrammes",
    "femtocelcius",
    "femtodegree celsius",
    "femtodegrees celsius",
    "femtocentigrade",
    "femtokelvin",
    "femtokelvins",
    "femtofahrenheit",
    "femtodegree fahrenheit",
    "femtodegrees fahrenheit",
    "femtoliter",
    "femtoliters",
    "femtolitre",
    "femtolitres",
    "attometer",
    "attometers",
    "attometre",
    "attometres",
    "attosecond",
    "attoseconds",
    "attogram",
    "attograms",
    "attogramme",
    "attogrammes",
    "attocelcius",
    "attodegree celsius",
    "attodegrees celsius",
    "attocentigrade",
    "attokelvin",
    "attokelvins",
    "attofahrenheit",
    "attodegree fahrenheit",
    "attodegrees fahrenheit",
    "attoliter",
    "attoliters",
    "attolitre",
    "attolitres",
    "zeptometer",
    "zeptometers",
    "zeptometre",
    "zeptometres",
    "zeptosecond",
    "zeptoseconds",
    "zeptogram",
    "zeptograms",
    "zeptogramme",
    "zeptogrammes",
    "zeptocelcius",
    "zeptodegree celsius",
    "zeptodegrees celsius",
    "zeptocentigrade",
    "zeptokelvin",
    "zeptokelvins",
    "zeptofahrenheit",
    "zeptodegree fahrenheit",
    "zeptodegrees fahrenheit",
    "zeptoliter",
    "zeptoliters",
    "zeptolitre",
    "zeptolitres",
    "yoctometer",
    "yoctometers",
    "yoctometre",
    "yoctometres",
    "yoctosecond",
    "yoctoseconds",
    "yoctogram",
    "yoctograms",
    "yoctogramme",
    "yoctogrammes",
    "yoctocelcius",
    "yoctodegree celsius",
    "yoctodegrees celsius",
    "yoctocentigrade",
    "yoctokelvin",
    "yoctokelvins",
    "yoctofahrenheit",
    "yoctodegree fahrenheit",
    "yoctodegrees fahrenheit",
    "yoctoliter",
    "yoctoliters",
    "yoctolitre",
    "yoctolitres",
    "rontometer",
    "rontometers",
    "rontometre",
    "rontometres",
    "rontosecond",
    "rontoseconds",
    "rontogram",
    "rontograms",
    "rontogramme",
    "rontogrammes",
    "rontocelcius",
    "rontodegree celsius",
    "rontodegrees celsius",
    "rontocentigrade",
    "rontokelvin",
    "rontokelvins",
    "rontofahrenheit",
    "rontodegree fahrenheit",
    "rontodegrees fahrenheit",
    "rontoliter",
    "rontoliters",
    "rontolitre",
    "rontolitres",
    "quectometer",
    "quectometers",
    "quectometre",
    "quectometres",
    "quectosecond",
    "quectoseconds",
    "quectogram",
    "quectograms",
    "quectogramme",
    "quectogrammes",
    "quectocelcius",
    "quectodegree celsius",
    "quectodegrees celsius",
    "quectocentigrade",
    "quectokelvin",
    "quectokelvins",
    "quectofahrenheit",
    "quectodegree fahrenheit",
    "quectodegrees fahrenheit",
    "quectoliter",
    "quectoliters",
    "quectolitre",
    "quectolitres",
    "radian",
    "steradian",
    "hertz",
    "newton",
    "pascal",
    "joule",
    "watt",
    "coulomb",
    "volt",
    "farad",
    "ohm",
    "siemens",
    "weber",
    "tesla",
    "henry",
    "lumen",
    "lux",
    "becquerel",
    "gray",
    "sievert",
    "katal",
    "ampere",
    "mole",
    "candela",
    "degree",
    "are",
    "hectare",
    "barn",
    "angstrom",
    "bar",
    "dalton",
    "astronomical unit",
    "knot",
    "electronvolt",
    "neper",
    "bel",
    "decibel",
    "var",
    "square meter",
    "micron",
    "erg",
    "dyne",
    "calorie",
    "poise",
    "stilb",
    # Size differs between countries
    "gallon",
    "gallons",
    "gal",
    "pint",
    "pints",
    "ton",
    "tons",
    "fluid ounce",
    "fluid ounces",
    "fl oz",
    "cup",
    "cups",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "teaspoon",
    "teaspoons",
    "tsp",
    # Length varies
    "month",
    "months",
    "year",
    "years",
)


CATEGORIES: tuple[Category, ...] = (LENGTH, MASS, VOLUME, DURATION, TEMPERATURE)


# --- Registry ---

"""Registry of units: validates unit data and provides fast lookups."""


class Registry:
    """Holds every category and unit, and refuses to load invalid data.

    All validation happens in the constructor, before the registry exists,
    so a half-built registry can never be used. Lookups are by normalized
    name, symbol or alias. The registry only looks things up: deciding what
    a miss means (unknown, unsupported, suggestions) is the resolver's job.
    """

    def __init__(
        self,
        categories: Iterable[Category],
        unsupported: Iterable[str] = (),
    ) -> None:
        category_list = tuple(categories)
        category_names: set[str] = set()
        units_category_list: dict[str, Category] = {}
        keys_unit_list: dict[str, Unit] = {}

        for category in category_list:
            # Check there is no duplicate category ie no categories with same name.
            if category.name in category_names:
                raise RegistryError(f"duplicate category name '{category.name}'.")
            category_names.add(category.name)

            check_base_unit(category)

            for unit in category.units:
                # A unit can't belong to two different categories.
                # Also, check there is no duplicate units in one category.
                c = units_category_list.get(unit.id)
                if c:
                    if category == c:
                        raise RegistryError(
                            f"duplicate unit id '{unit.id}' "
                            f"found in category '{category.name}'."
                        )
                    else:
                        raise RegistryError(
                            f"duplicate unit id '{unit.id}' "
                            f"found in categories '{category.name}' and '{c.name}'."
                        )

                check_numbers(unit)

                # Check two different units can't share a same name, symbol or alias.
                for key in keys_of(unit):
                    owner = keys_unit_list.get(key)
                    if owner is not None and owner.id != unit.id:
                        raise RegistryError(
                            f"key '{key}' is used by both unit '{owner.id}' "
                            f"and unit '{unit.id}'."
                        )
                    # Keep track to which unit a key belongs.
                    keys_unit_list[key] = unit

                # Keep track to which category a unit belongs.
                units_category_list[unit.id] = category

        self._categories = category_list
        self._unsupported = check_unsupported(unsupported, keys_unit_list)
        self._units_category_list = units_category_list
        self._keys_unit_list = keys_unit_list
        self._aliases = tuple(keys_unit_list)

    @property
    def categories(self) -> tuple[Category, ...]:
        """All categories, in the order they were given."""
        return self._categories

    def aliases(self) -> tuple[str, ...]:
        """Every normalized lookup key, e.g. for "did you mean" suggestions."""
        return self._aliases

    def category_of(self, unit: Unit) -> Category | None:
        """Return the category of a unit, looked up by the unit's id."""
        try:
            return self._units_category_list[unit.id]
        except KeyError:
            return None
            # raise RegistryError(f"unit '{unit.id}' is not in this registry.")

    def find_unit(self, name: str) -> Unit | None:
        """Return the unit matching a name, symbol or alias, or None."""
        return self._keys_unit_list.get(normalize(name))

    def is_unsupported(self, name: str) -> bool:
        """Tell whether a name is recognized but deliberately not supported."""
        return normalize(name) in self._unsupported


def check_base_unit(category: Category) -> None:
    # Check the base_unit comes from the list of units.
    base: Unit | None = None
    for unit in category.units:
        if category.base_unit_id == unit.id:
            base = unit
            break

    if base is None:
        raise RegistryError(
            f"category '{category.name}' has no unit with its base id "
            f"'{category.base_unit_id}'."
        )

    # Check base factor and offset values.
    if base.factor != 1 or base.offset != 0:
        raise RegistryError(
            f"base unit '{base.id}' of category '{category.name}' must have "
            f"factor 1 and offset 0."
        )


def check_numbers(unit: Unit) -> None:
    # Check unit factor and offset values.
    if not (math.isfinite(unit.factor) and unit.factor > 0):
        raise RegistryError(
            f"unit '{unit.id}' has an invalid factor '{unit.factor}': "
            f"it must be positive and finite."
        )
    if not math.isfinite(unit.offset):
        raise RegistryError(
            f"unit '{unit.id}' has an invalid offset '{unit.offset}': "
            f"it must be finite."
        )


def keys_of(unit: Unit) -> list[str]:
    # Check that name, symbol and aliases fields are not empty.
    labelled = [("name", unit.name), ("symbol", unit.symbol)]
    labelled += [("alias", alias) for alias in unit.aliases]

    keys: list[str] = []
    for label, text in labelled:
        key = normalize(text)
        if key == "":
            raise RegistryError(f"unit '{unit.id}' has an empty {label}.")
        keys.append(key)

    return keys


def check_unsupported(
    names: Iterable[str], keys_unit_list: dict[str, Unit]
) -> set[str]:
    keys: set[str] = set()  # To keep track of unique unsupported names.
    for name in names:
        # Check the name is not a supported unit.
        key = normalize(name)
        if key == "":
            raise RegistryError(f"unsupported name '{name}' is empty.")
        owner = keys_unit_list.get(key)
        if owner is not None:
            raise RegistryError(
                f"unsupported name '{name}' is a supported name of unit '{owner.id}'."
            )
        keys.add(key)

    return set(keys)


# --- Formatter ---

_SCIENTIFIC_FROM = 1e6  # at or above this, use scientific notation
_SCIENTIFIC_BELOW = 1e-4  # below this, use scientific notation
_MIN_DECIMALS = 4
_SIGNIFICANT_DIGITS = 4


def format_number(x: float) -> str:
    """Format a number for display.

    Rules:
    - zero is ``0``
    - at or above 1e6, or below 1e-4: scientific notation with 4 significant
      digits and no padding, such as ``1.235e9`` or ``1.234e-5``
    - otherwise: fixed notation with at least 4 decimals and at least 4
      significant digits (so ``0.000123456`` is ``0.0001235``), with trailing
      zeros removed
    - ``inf`` and ``nan`` are shown as such
    """
    if not math.isfinite(x):
        return str(x)
    if x == 0:
        return "0"
    magnitude = abs(x)
    if magnitude < _SCIENTIFIC_BELOW or magnitude >= _SCIENTIFIC_FROM:
        return _scientific(x)
    decimals = max(
        _MIN_DECIMALS,
        _SIGNIFICANT_DIGITS - 1 - math.floor(math.log10(magnitude)),
    )
    text = f"{x:.{decimals}f}"
    if abs(float(text)) >= _SCIENTIFIC_FROM:
        # Rounding pushed the value over the threshold (999999.99996 -> 1e6).
        return _scientific(x)
    return _strip_zeros(text)


def format_quantity(quantity: Quantity) -> str:
    """Format a quantity as its number followed by the unit symbol."""
    return f"{format_number(quantity.value)} {quantity.unit.symbol}"


def _scientific(x: float) -> str:
    mantissa, exponent = f"{x:.{_SIGNIFICANT_DIGITS - 1}e}".split("e")
    return f"{_strip_zeros(mantissa)}e{int(exponent)}"


def _strip_zeros(text: str) -> str:
    """Remove trailing zeros after the decimal point (the text has one)."""
    return text.rstrip("0").rstrip(".")


# --- Resolver ---

"""Turn a name typed by a user into a unit, or into a helpful error."""

# At most this many unit names are suggested...
MAX_SUGGESTIONS = 3

# ...and only names at least this similar (0 to 1) to what the user typed.
# Tuned on realistic typos: 0.6 suggested unrelated units ("kilomter" also
# gave millimeter and kilogram, "ouncs" gave hour), while 0.8 missed real
# typos ("feat" for foot). 0.7 was the best balance.
SUGGESTION_CUTOFF = 0.7


def resolve(name: str, registry: Registry) -> Unit:
    """Return the unit a name refers to, or raise a helpful error.

    Raises:
        UnsupportedUnitError: the name is recognized but deliberately not
            supported (for example "gallon").
        UnknownUnitError: the name matches nothing, with suggestions when
            some unit names are close to it.
    """
    unit = registry.find_unit(name)
    if unit is not None:
        return unit
    if registry.is_unsupported(name):
        raise UnsupportedUnitError(name)
    raise UnknownUnitError(name, list(suggest_units(name, registry)))


def suggest_units(name: str, registry: Registry) -> tuple[str, ...]:
    """Return the names of the units closest to a misspelled name.

    Close matches are found among every lookup key, then mapped back to unit
    names, so a unit with several spellings is suggested only once. The best
    match comes first.
    """
    keys = registry.aliases()

    # Get keys close to name.
    close_keys = {}
    normalized_name = normalize(name)
    for key in keys:
        proximity = SequenceMatcher(None, key, normalized_name).ratio()
        if proximity < SUGGESTION_CUTOFF:
            continue

        close_keys[key] = proximity

    # Sorted best match keys by their proximity with name.
    suggestions = [
        k for k, _ in sorted(close_keys.items(), key=lambda item: item[1], reverse=True)
    ]

    return tuple(suggestions[:MAX_SUGGESTIONS])


# --- Converter ---


def parse(value: object, unit_name: str, registry: Registry) -> Quantity:
    """Build a quantity from a typed value and a typed unit name.

    The number is checked first, then the unit, so when both are wrong the
    error is about the number.

    Raises:
        InvalidNumberError: the value is not a finite number.
        UnsupportedUnitError: the unit is recognized but not supported.
        UnknownUnitError: the unit is not known.
    """
    number = parse_number(value)
    unit = resolve(unit_name, registry)
    return Quantity(number, unit)


def convert_(quantity: Quantity, target_unit: Unit, registry: Registry) -> Quantity:
    """Express a quantity in another unit of the same category.

    Every unit is defined relative to its category's base unit, so the value
    goes to the base unit and from there to the target unit. The original
    quantity is not modified. A value too large to represent after conversion
    becomes ``inf``.

    Raises:
        IncompatibleUnitsError: the units belong to different categories.
    """
    # Check the conversion is possible.
    from_category = registry.category_of(quantity.unit)
    to_category = registry.category_of(target_unit)

    # Check a category were found.
    if from_category is None:
        raise ConverterError(
            f"unit '{quantity.unit.id}' has no category in the registry."
        )
    if to_category is None:
        raise ConverterError(
            f"unit '{target_unit.id}' has no category in the registry."
        )

    # We convert in a same category.
    if from_category.name != to_category.name:
        raise IncompatibleUnitsError(from_category.name, to_category.name)

    if quantity.unit.id == target_unit.id:
        # Same unit: skip the arithmetic so the value comes back exactly.
        return Quantity(quantity.value, target_unit)

    # Perform the calculation.
    # First convert to the base unit.
    base_value = (quantity.value + quantity.unit.offset) * quantity.unit.factor
    # Then convert the value obtained above to the target unit.
    value = base_value / target_unit.factor - target_unit.offset
    return Quantity(value, target_unit)


# --- API ---

"""Public API: the only module the interfaces (CLI, GUI) need to import.

It builds the real registry from the unit data once, and hides the engine's
internals behind a few functions.
"""


@lru_cache(maxsize=1)
def get_registry() -> Registry:
    """Return the registry of all supported units, built on first use."""
    return Registry(CATEGORIES, unsupported=UNSUPPORTED)


def parse_quantity(value: object, unit_name: str) -> Quantity:
    """Build a quantity from a typed value and a typed unit name.

    Raises:
        ConverterError: a subclass describing what is wrong (invalid number,
            unknown or unsupported unit).
    """
    return parse(value, unit_name, get_registry())


def convert_quantity(quantity: Quantity, to_unit: str) -> Quantity:
    """Express a quantity in the unit a name refers to.

    Raises:
        ConverterError: a subclass describing what is wrong (unknown or
            unsupported unit, incompatible units).
    """
    registry = get_registry()
    target = resolve(to_unit, registry)
    return convert_(quantity, target, registry)


def convert(value: object, from_unit: str, to_unit: str) -> Quantity:
    """Convert a typed value between two typed unit names.

    The value is checked first, then the source unit, then the target unit.

    Raises:
        ConverterError: a subclass describing what is wrong (invalid number,
            unknown or unsupported unit, incompatible units).
    """
    return convert_quantity(parse_quantity(value, from_unit), to_unit)


def convert_and_format(value: object, from_unit: str, to_unit: str) -> str:
    """Convert and return display text such as ``6.2137 mi``."""
    return format_quantity(convert(value, from_unit, to_unit))


# --- Utils ---

"""Normalization of unit names, so that equivalent spellings compare equal."""


def normalize(name: str) -> str:
    """Return a canonical form of a unit name for matching.

    The result is case-insensitive and has leading, trailing and repeated
    whitespace removed. It does not remove plural endings or fix spelling:
    variants are listed explicitly as aliases in the unit data.

    Empty or whitespace-only input returns an empty string.
    """
    return " ".join(name.casefold().split())


def parse_number(value: object) -> float:
    """Return ``value`` as a finite float, or raise InvalidNumberError.

    Accepts ints and floats, and text in Python's float syntax (``5``,
    ``-2.5``, ``1e3``) with surrounding spaces ignored. Text must be plain
    ASCII with a decimal point: a decimal comma, thousands separators,
    underscores and non-ASCII digits are rejected, as are ``nan``, ``inf``
    and values too large for a float. Anything that is not text or a number
    (``None``, booleans, lists) is rejected too.

    The parameter is typed ``object`` on purpose: interfaces hand over raw
    user input, and rejecting bad input is this function's job.
    """
    if isinstance(value, bool) or not isinstance(value, str | int | float):
        raise InvalidNumberError(value)

    candidate = value.strip() if isinstance(value, str) else value

    if isinstance(candidate, str) and (not candidate.isascii() or "_" in candidate):
        raise InvalidNumberError(value)

    # Try to convert the number in float.
    try:
        number = float(candidate)
    except (ValueError, OverflowError):
        raise InvalidNumberError(value) from None

    if not math.isfinite(number):
        raise InvalidNumberError(value)

    return number


# --- MAIN ---

"""Command-line interface.

A thin layer over the public API: it reads arguments, calls the API, and
prints. Results go to standard output, errors to standard error.

Exit codes: 0 on success, 1 when the conversion fails (bad number, unknown or
unsupported unit, incompatible units), 2 for wrong command-line usage.
"""

_MARGIN = " " * 7
_USAGE = f"%(prog)s -v VALUE --from UNIT --to UNIT\n{_MARGIN}%(prog)s [-h | -l]"

_PROG_NAME = "python project.py"
_EXAMPLES = f"""\
examples:
  {_PROG_NAME} -v 10 --from km --to miles
  {_PROG_NAME} --value 100 --from celsius --to fahrenheit
  {_PROG_NAME} -v 5 --from "nautical mile" --to km
  {_PROG_NAME} -v=-1e3 --from m --to km

Unit names ignore case and accept symbols, plurals and British spellings.
Put names with spaces in quotes. And use the equality sign when dealing with
negative numbers.
"""

_LIST_WIDTH = 78


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog=f"{_PROG_NAME}",
        usage=_USAGE,
        description="Convert a value from one unit to another.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--value",
        help="the number to convert",
    )
    parser.add_argument(
        "--from",
        help="the unit of the number",
        metavar="UNIT",
    )
    parser.add_argument(
        "--to",
        help="the unit to convert to",
        metavar="UNIT",
    )

    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list the supported units and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface and return its exit code.

    Wrong usage (missing arguments, unknown options) makes argparse print a
    message and exit with code 2.
    """
    parser = build_parser()
    args = vars(parser.parse_args(argv))

    # If the -h or --help option is used, the code below won't execute.

    given = [args.get("value"), args.get("from"), args.get("to")]

    if args.get("list"):
        # Exclude the use of -l or --list option with the others.
        if any(item is not None for item in given):
            parser.error("-l or --list option must be used alone.")

        # List available units.
        print(_format_unit_list())
        return 0

    if any(item is None for item in given):
        parser.error("expected three arguments: value, from_unit and to_unit.")

    try:
        source = parse_quantity(args.get("value"), str(args.get("from")))
        result = convert_quantity(source, str(args.get("to")))
    except ConverterError as error:
        print(error.message, file=sys.stderr)
        return 1

    print(f"{format_quantity(source)} = {format_quantity(result)}")
    return 0


def list_units() -> dict[str, tuple[dict[str, str], ...]]:
    """Return the unit names of each category, for interface selectors."""
    return {
        category.name: tuple({unit.name: unit.symbol} for unit in category.units)
        for category in get_registry().categories
    }


def _format_unit_list() -> str:
    lines: list[str] = []
    for category, names in list_units().items():
        # Non-breaking spaces keep names like "nautical mile" on one line.
        text = ", ".join(
            f"{name} ({key})".replace(" ", "\u00a0")
            for name_key in names
            for name, key in name_key.items()
        )
        wrapped = textwrap.fill(
            text,
            width=_LIST_WIDTH,
            initial_indent="  ",
            subsequent_indent="  ",
        )
        lines.append(f"{category.capitalize()}:")
        lines.append(wrapped.replace("\u00a0", " "))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
