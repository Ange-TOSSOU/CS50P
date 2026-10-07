# --- Imports ---

import math
import re
import sys
from collections.abc import Callable

import pytest

from project import *

# --- Errors Handling ---


def test_converter_error_is_an_exception() -> None:
    assert issubclass(ConverterError, Exception)


def test_converter_error_can_be_raised_and_caught() -> None:
    with pytest.raises(ConverterError):
        raise ConverterError("something went wrong")


def test_converter_error_exposes_message() -> None:
    error = ConverterError("something went wrong")
    assert error.message == "something went wrong"


def test_converter_error_str_matches_message() -> None:
    error = ConverterError("something went wrong")
    assert str(error) == "something went wrong"


# --- InvalidNumberError ---


def test_invalid_number_error_keeps_value() -> None:
    error = InvalidNumberError("abc")
    assert error.value == "abc"


@pytest.mark.parametrize("value", ["abc", "1,5", "12abc", "--3"])
def test_invalid_number_error_message_with_value(value: str) -> None:
    error = InvalidNumberError(value)
    assert error.message == f"InvalidNumberError: '{value}' is not a valid number."


def test_invalid_number_error_empty_string_is_shown() -> None:
    error = InvalidNumberError("")
    assert error.message == "InvalidNumberError: '' is not a valid number."


def test_invalid_number_error_none_has_useful_message() -> None:
    error = InvalidNumberError(None)
    assert error.value is None
    assert error.message == "InvalidNumberError."


def test_invalid_number_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise InvalidNumberError("abc")


# --- UnknownUnitError ---


def test_unknown_unit_error_keeps_name() -> None:
    error = UnknownUnitError("kilometre")
    assert error.name == "kilometre"


def test_unknown_unit_error_defaults_to_no_suggestions() -> None:
    error = UnknownUnitError("blorp")
    assert error.suggestions == ()


def test_unknown_unit_error_suggestions_are_stored_as_tuple() -> None:
    error = UnknownUnitError("kilometre", ["kilometer", "kilometers"])
    assert isinstance(error.suggestions, tuple)


def test_unknown_unit_error_suggestions_keep_order() -> None:
    error = UnknownUnitError("kilometre", ["kilometer", "kilometers"])
    assert error.suggestions == ("kilometer", "kilometers")


def test_unknown_unit_error_without_suggestions_has_no_hint() -> None:
    error = UnknownUnitError("blorp")
    assert error.message == "UnknownUnitError: unknown unit 'blorp'."


def test_unknown_unit_error_without_empty_suggestions_has_no_hint() -> None:
    error = UnknownUnitError("blorp", [])
    assert error.message == "UnknownUnitError: unknown unit 'blorp'."


def test_unknown_unit_error_with_one_suggestion() -> None:
    error = UnknownUnitError("kilometre", ["kilometer"])
    assert (
        error.message
        == "UnknownUnitError: unknown unit 'kilometre'. Did you mean 'kilometer'?"
    )


def test_unknown_unit_error_with_several_suggestions() -> None:
    error = UnknownUnitError("mter", ["meter", "metre", "miter"])
    assert error.message == (
        "UnknownUnitError: unknown unit 'mter'. Did you mean 'meter', 'metre', 'miter'?"
    )


def test_unknown_unit_error_bypass_suggestions_when_no_name() -> None:
    error = UnknownUnitError(suggestions=["kilometer"])
    assert error.message == "UnknownUnitError."


def test_unknown_unit_error_message_when_no_name_nor_suggestions() -> None:
    error = UnknownUnitError()
    assert error.message == "UnknownUnitError."


def test_unknown_unit_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise UnknownUnitError("blorp")


# --- IncompatibleUnitsError ---


def test_incompatible_units_error_keeps_categories() -> None:
    error = IncompatibleUnitsError("mass", "length")
    assert error.from_category == "mass"
    assert error.to_category == "length"


def test_incompatible_units_error_message_mentions_both_in_order() -> None:
    error = IncompatibleUnitsError("mass", "length")
    assert (
        error.message
        == "IncompatibleUnitsError: cannot convert from 'mass' to 'length'."
    )


def test_incompatible_units_error_message_with_from_category_omitted() -> None:
    error = IncompatibleUnitsError(to_category="length")
    assert error.message == "IncompatibleUnitsError."


def test_incompatible_units_error_message_with_to_category_omitted() -> None:
    error = IncompatibleUnitsError(from_category="mass")
    assert error.message == "IncompatibleUnitsError."


def test_incompatible_units_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise IncompatibleUnitsError("mass", "length")


# --- Shared behaviour ---

ALL_ERRORS: list[ConverterError] = [
    ConverterError("base"),
    InvalidNumberError("abc"),
    UnknownUnitError("blorp", ["meter"]),
    IncompatibleUnitsError("mass", "length"),
]

SUBCLASS_ERRORS: list[ConverterError] = ALL_ERRORS[1:]


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_every_error_is_a_converter_error(error: ConverterError) -> None:
    assert isinstance(error, ConverterError)


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_every_error_str_matches_message(error: ConverterError) -> None:
    assert str(error) == error.message


@pytest.mark.parametrize("error", ALL_ERRORS)
def test_every_error_message_is_not_empty(error: ConverterError) -> None:
    assert error.message.strip() != ""


# --- RegistryError ---


def test_registry_error_is_an_exception() -> None:
    assert issubclass(RegistryError, Exception)


def test_registry_error_can_be_raised_and_caught() -> None:
    with pytest.raises(RegistryError):
        raise RegistryError("Bad data.")


def test_registry_error_keeps_detail() -> None:
    assert RegistryError("Bad data.").detail == "Bad data."


def test_registry_error_message() -> None:
    assert RegistryError("Bad data.").message == "RegistryError: Bad data."


def test_registry_error_str_matches_message() -> None:
    error = RegistryError("Bad data.")
    assert str(error) == error.message


def test_registry_error_is_not_a_converter_error() -> None:
    # A data bug must not be hidden behind the friendly,
    # user-facing ConverterError family.
    assert not issubclass(RegistryError, ConverterError)


def test_registry_error_is_not_caught_by_converter_error_handlers() -> None:
    caught_as_converter_error = False
    try:
        raise RegistryError("Bad data.")
    except ConverterError:
        caught_as_converter_error = True
    except RegistryError:
        pass
    assert not caught_as_converter_error


# --- UnsupportedUnitError ---


def test_unsupported_unit_error_keeps_name() -> None:
    assert UnsupportedUnitError("gallon").name == "gallon"


def test_unsupported_unit_error_message() -> None:
    error = UnsupportedUnitError("gallon")
    assert error.message == ("UnsupportedUnitError: 'gallon' is not supported.")


def test_unsupported_unit_error_keeps_the_text_as_typed() -> None:
    error = UnsupportedUnitError("Gallons")
    assert error.message == ("UnsupportedUnitError: 'Gallons' is not supported.")


def test_unsupported_unit_error_str_matches_message() -> None:
    error = UnsupportedUnitError("gallon")
    assert str(error) == error.message


def test_unsupported_unit_error_is_caught_as_converter_error() -> None:
    with pytest.raises(ConverterError):
        raise UnsupportedUnitError("gallon")


# --- Models ---


def make_meter() -> Unit:
    return Unit(
        id="meter",
        name="meter",
        symbol="m",
        factor=1,
    )


def make_kilometer() -> Unit:
    return Unit(
        id="kilometer",
        name="kilometer",
        symbol="km",
        factor=1000,
        aliases=("kilometre", "kilometers", "kilometres"),
    )


# --- Unit ---


def test_unit_holds_the_fields_it_was_given() -> None:
    unit = make_kilometer()
    assert unit.id == "kilometer"
    assert unit.name == "kilometer"
    assert unit.symbol == "km"
    assert unit.factor == 1000
    assert unit.aliases == ("kilometre", "kilometers", "kilometres")


def test_unit_defaults_to_no_aliases_and_no_offset() -> None:
    unit = make_meter()
    assert unit.aliases == ()
    assert unit.offset == 0.0


def test_unit_accepts_an_offset() -> None:
    celsius = Unit(
        id="celsius",
        name="celsius",
        symbol="°C",
        factor=1,
        offset=273.15,
    )
    assert celsius.offset == 273.15


def test_units_with_identical_fields_are_equal() -> None:
    assert make_kilometer() == make_kilometer()


def test_units_differing_in_one_field_are_not_equal() -> None:
    other = make_kilometer()
    other.factor = 999
    assert make_kilometer() != other


def test_unit_requires_its_mandatory_fields() -> None:
    with pytest.raises(TypeError):
        Unit(id="meter", name="meter")  # type: ignore[call-arg]


# --- Category ---


def test_category_holds_the_fields_it_was_given() -> None:
    meter = make_meter()
    kilometer = make_kilometer()
    category = Category(
        name="length",
        base_unit_id="meter",
        units=(meter, kilometer),
    )
    assert category.name == "length"
    assert category.base_unit_id == "meter"
    assert category.units == (meter, kilometer)


def test_categories_with_identical_fields_are_equal() -> None:
    first = Category(name="length", base_unit_id="meter", units=(make_meter(),))
    second = Category(name="length", base_unit_id="meter", units=(make_meter(),))
    assert first == second


def test_category_requires_arguments() -> None:
    with pytest.raises(TypeError):
        Category("length", "meter")  # type: ignore[call-arg]


# --- Quantity ---


def test_quantity_holds_its_value_and_unit() -> None:
    kilometer = make_kilometer()
    quantity = Quantity(5.0, kilometer)
    assert quantity.value == 5.0
    assert quantity.unit is kilometer


def test_quantity_can_be_built_with_keywords() -> None:
    kilometer = make_kilometer()
    assert Quantity(value=5.0, unit=kilometer) == Quantity(5.0, kilometer)


def test_quantities_with_same_value_and_unit_are_equal() -> None:
    assert Quantity(5.0, make_kilometer()) == Quantity(5.0, make_kilometer())


def test_quantities_with_different_values_are_not_equal() -> None:
    assert Quantity(5.0, make_kilometer()) != Quantity(6.0, make_kilometer())


def test_quantities_with_different_units_are_not_equal() -> None:
    assert Quantity(5.0, make_kilometer()) != Quantity(5.0, make_meter())


def test_physically_equal_quantities_in_different_units_are_not_equal() -> None:
    assert Quantity(1.0, make_kilometer()) != Quantity(1000.0, make_meter())


def test_quantity_requires_both_fields() -> None:
    with pytest.raises(TypeError):
        Quantity(5.0)  # type: ignore[call-arg]


# --- Factors ---

EXPECTED_FACTORS: dict[str, float] = {
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


def test_units_factors_are_exactly_the_expected_ones() -> None:
    assert FACTORS == EXPECTED_FACTORS


# --- Data ---

REGISTRY = Registry(CATEGORIES, UNSUPPORTED)


def get_unit(name: str) -> Unit:
    unit = REGISTRY.find_unit(name)
    assert unit is not None
    return unit


# --- Catalog structure ---

EXPECTED_UNIT_IDS = {
    "length": (
        "millimeter",
        "centimeter",
        "decimeter",
        "meter",
        "kilometer",
        "inch",
        "foot",
        "yard",
        "mile",
        "nautical_mile",
    ),
    "mass": (
        "milligram",
        "gram",
        "kilogram",
        "metric_ton",
        "ounce",
        "pound",
        "stone",
    ),
    "volume": (
        "milliliter",
        "cubic_centimeter",
        "liter",
        "cubic_meter",
        "cubic_inch",
        "cubic_foot",
    ),
    "time": ("millisecond", "second", "minute", "hour", "day", "week"),
    "temperature": ("kelvin", "celsius", "fahrenheit"),
}

EXPECTED_BASE_IDS = {
    "length": "meter",
    "mass": "kilogram",
    "volume": "liter",
    "time": "second",
    "temperature": "kelvin",
}


def test_catalog_loads_into_a_registry() -> None:
    Registry(CATEGORIES)  # raises RegistryError if the data is invalid


def test_the_five_categories_are_present_in_order() -> None:
    names = [category.name for category in CATEGORIES]
    assert names == ["length", "mass", "volume", "time", "temperature"]


@pytest.mark.parametrize("category", CATEGORIES)
def test_category_contains_exactly_the_expected_units(category: Category) -> None:
    ids = tuple(unit.id for unit in category.units)
    assert sorted(ids) == sorted(EXPECTED_UNIT_IDS[category.name])


@pytest.mark.parametrize("category", CATEGORIES)
def test_category_has_the_expected_base_unit(category: Category) -> None:
    assert category.base_unit_id == EXPECTED_BASE_IDS[category.name]
    base = get_unit(category.base_unit_id)
    assert base.factor == 1
    assert base.offset == 0


def test_unit_ids_are_lowercase_snake_case() -> None:
    pattern = re.compile(r"^[a-z]+(_[a-z]+)*$")
    for category in CATEGORIES:
        for unit in category.units:
            assert pattern.match(unit.id)


def test_every_name_symbol_and_alias_is_plain_ascii() -> None:
    for category in CATEGORIES:
        for unit in category.units:
            for text in (unit.name, unit.symbol, *unit.aliases):
                assert text.isascii()


# --- Symbols and aliases ---

EXPECTED_SYMBOLS = {
    "millimeter": "mm",
    "centimeter": "cm",
    "decimeter": "dm",
    "meter": "m",
    "kilometer": "km",
    "inch": "in",
    "foot": "ft",
    "yard": "yd",
    "mile": "mi",
    "nautical_mile": "nmi",
    "milligram": "mg",
    "gram": "g",
    "kilogram": "kg",
    "metric_ton": "t",
    "ounce": "oz",
    "pound": "lb",
    "stone": "st",
    "milliliter": "ml",
    "cubic_centimeter": "cm3",
    "liter": "l",
    "cubic_meter": "m3",
    "cubic_inch": "in3",
    "cubic_foot": "ft3",
    "millisecond": "ms",
    "second": "s",
    "minute": "min",
    "hour": "h",
    "day": "d",
    "week": "wk",
    "kelvin": "K",
    "celsius": "C",
    "fahrenheit": "F",
}

EXPECTED_ALIASES = {
    "millimeter": ("millimeters", "millimetre", "millimetres"),
    "centimeter": ("centimeters", "centimetre", "centimetres"),
    "decimeter": ("decimeters", "decimetre", "decimetres"),
    "meter": ("meters", "metre", "metres"),
    "kilometer": ("kilometers", "kilometre", "kilometres"),
    "inch": ("inches",),
    "foot": ("feet",),
    "yard": ("yards",),
    "mile": ("miles",),
    "nautical_mile": ("nautical miles",),
    "milligram": ("milligrams", "milligramme", "milligrammes"),
    "gram": ("grams", "gramme", "grammes"),
    "kilogram": ("kilograms", "kilogramme", "kilogrammes", "kilo", "kilos"),
    "metric_ton": ("metric tons", "tonne", "tonnes"),
    "ounce": ("ounces",),
    "pound": ("pounds", "lbs"),
    "stone": ("stones",),
    "milliliter": ("milliliters", "millilitre", "millilitres"),
    "cubic_centimeter": (
        "cubic centimeters",
        "cubic centimetre",
        "cubic centimetres",
        "cc",
    ),
    "liter": ("liters", "litre", "litres"),
    "cubic_meter": ("cubic meters", "cubic metre", "cubic metres"),
    "cubic_inch": ("cubic inches",),
    "cubic_foot": ("cubic feet",),
    "millisecond": ("milliseconds",),
    "second": ("seconds", "sec", "secs"),
    "minute": ("minutes", "mins"),
    "hour": ("hours", "hr", "hrs"),
    "day": ("days",),
    "week": ("weeks", "wks"),
    "kelvin": ("kelvins",),
    "celsius": ("degree celsius", "degrees celsius", "centigrade"),
    "fahrenheit": ("degree fahrenheit", "degrees fahrenheit"),
}

ALIAS_CASES = [
    (alias, unit_id)
    for unit_id, aliases in EXPECTED_ALIASES.items()
    for alias in aliases
]


def test_symbol_table_covers_every_unit() -> None:
    all_ids = {unit.id for category in CATEGORIES for unit in category.units}
    assert set(EXPECTED_SYMBOLS) == all_ids
    assert set(EXPECTED_ALIASES) == all_ids


@pytest.mark.parametrize(("unit_id", "symbol"), EXPECTED_SYMBOLS.items())
def test_symbol_finds_its_unit(unit_id: str, symbol: str) -> None:
    unit = get_unit(symbol)
    assert unit.id == unit_id
    assert unit.symbol == symbol


@pytest.mark.parametrize("unit_id", EXPECTED_SYMBOLS)
def test_unit_id_name_finds_its_unit(unit_id: str) -> None:
    name = unit_id.replace("_", " ")
    assert get_unit(name).id == unit_id


@pytest.mark.parametrize(("alias", "unit_id"), ALIAS_CASES)
def test_alias_finds_its_unit(alias: str, unit_id: str) -> None:
    assert get_unit(alias).id == unit_id


def test_lookup_ignores_case_and_spacing() -> None:
    assert get_unit("  Degrees   CELSIUS ").id == "celsius"
    assert get_unit("NAUTICAL  Miles").id == "nautical_mile"


# --- Reference factors and offsets ---

# (offset, unit name, factor in the category's base unit)
REFERENCE_FO = [
    # Length, in meters
    (0, "millimeter", 0.001),
    (0, "centimeter", 0.01),
    (0, "decimeter", 0.1),
    (0, "meter", 1),
    (0, "kilometer", 1000),
    (0, "inch", 0.0254),
    (0, "foot", 0.3048006096),
    (0, "yard", 0.91440183),
    (0, "mile", 1609.344),
    (0, "nautical mile", 1852),
    # Mass, in kilograms
    (0, "milligram", 1e-6),
    (0, "gram", 0.001),
    (0, "kilogram", 1),
    (0, "metric ton", 1000),
    (0, "pound", 0.45359237),
    (0, "ounce", 0.028349523125),
    (0, "stone", 6.35029318),
    # Volume, in liters
    (0, "milliliter", 0.001),
    (0, "cubic centimeter", 0.001),
    (0, "liter", 1),
    (0, "cubic meter", 1000),
    (0, "cubic inch", 0.016387064),
    (0, "cubic foot", 28.316846592),
    # Time, in seconds
    (0, "millisecond", 0.001),
    (0, "second", 1),
    (0, "minute", 60),
    (0, "hour", 3600),
    (0, "day", 86400),
    (0, "week", 604800),
    # Temperature, in kelvin
    (273.15, "celsius", 1),
    (0, "kelvin", 1),
    (459.67, "fahrenheit", 5 / 9),
]


@pytest.mark.parametrize(("offset", "name", "factor"), REFERENCE_FO)
def test_reference_factors_and_offsets(factor: float, name: str, offset: float) -> None:
    unit = get_unit(name)
    assert unit.factor == factor and unit.offset == offset


# --- Units that must NOT exist ---


@pytest.mark.parametrize(
    "name",
    [
        "gallon",
        "pint",
        "ton",
        "cup",
        "tablespoon",
        "teaspoon",
        "fluid ounce",
        "tbsp",
        "tsp",
        "month",
        "year",
    ],
)
def test_regionally_ambiguous_or_variable_units_are_absent(name: str) -> None:
    assert REGISTRY.find_unit(name) is None


# --- Unsupported names ---


EXPECTED_UNSUPPORTED = (
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


def test_unsupported_names_are_exactly_the_expected_ones() -> None:
    assert set(UNSUPPORTED) == set(EXPECTED_UNSUPPORTED)


def test_unsupported_names_have_no_repeats() -> None:
    assert len(set(UNSUPPORTED)) == len(UNSUPPORTED)


@pytest.mark.parametrize("name", EXPECTED_UNSUPPORTED)
def test_expected_names_are_reported_as_unsupported(name: str) -> None:
    assert REGISTRY.is_unsupported(name)
    assert REGISTRY.find_unit(name) is None


@pytest.mark.parametrize("name", ["Gallons", "  FL   OZ ", "TBSP"])
def test_unsupported_lookup_ignores_case_and_spacing(name: str) -> None:
    assert REGISTRY.is_unsupported(name)


@pytest.mark.parametrize("name", ["tonne", "tonnes", "metric ton", "kilogram", "t"])
def test_supported_look_alikes_are_not_unsupported(name: str) -> None:
    # "ton" is unsupported but "tonne" and the metric ton are fine.
    assert not REGISTRY.is_unsupported(name)
    assert REGISTRY.find_unit(name) is not None


def test_unsupported_names_are_plain_ascii() -> None:
    assert all(name.isascii() for name in UNSUPPORTED)


# --- Supported names and aliases ---

SUPPORTED_NAMES_AND_ALIASES = []
SUPPORTED_NAMES_AND_ALIASES.extend([name for name in EXPECTED_ALIASES])
for category in CATEGORIES:
    for unit in category.units:
        name_and_aliases = [unit.name]
        name_and_aliases.extend(list(unit.aliases))
        SUPPORTED_NAMES_AND_ALIASES.extend(name_and_aliases)


@pytest.mark.parametrize("name", SUPPORTED_NAMES_AND_ALIASES)
def test_no_supported_units_is_also_unsupported(name: str) -> None:
    assert not REGISTRY.is_unsupported(name)


# --- Registry ---


def make_unit(
    id: str = "a",
    name: str = "a",
    symbol: str = "a",
    factor: float = 1,
    aliases: tuple[str, ...] = (),
    offset: float = 0.0,
) -> Unit:
    return Unit(id, name, symbol, factor, aliases, offset)


def make_category(*units: Unit, base_id: str = "a", name: str = "x") -> Category:
    return Category(name=name, base_unit_id=base_id, units=tuple(units))


METER = Unit(
    id="meter",
    name="meter",
    symbol="m",
    factor=1,
    aliases=("metre", "meters", "metres"),
)
KILOMETER = Unit(
    id="kilometer",
    name="kilometer",
    symbol="km",
    factor=1000,
    aliases=("kilometre", "kilometers", "kilometres"),
)

KELVIN = Unit(
    id="kelvin",
    name="kelvin",
    symbol="K",
    factor=1,
)
CELSIUS = Unit(
    id="celsius",
    name="celsius",
    symbol="C",
    factor=1,
    aliases=("degree celsius", "degrees celsius"),
    offset=273.15,
)

LENGTH = make_category(METER, KILOMETER, base_id="meter", name="length")
TEMPERATURE = make_category(KELVIN, CELSIUS, base_id="kelvin", name="temperature")


def make_registry() -> Registry:
    return Registry([LENGTH, TEMPERATURE])


# --- Lookups: happy path ---


def test_find_unit_by_name() -> None:
    assert make_registry().find_unit("kilometer") is KILOMETER


def test_find_unit_by_name_ignoring_case() -> None:
    assert make_registry().find_unit("KiloMeter") is KILOMETER


def test_find_unit_by_symbol() -> None:
    assert make_registry().find_unit("km") is KILOMETER


def test_find_unit_by_symbol_ignoring_case() -> None:
    assert make_registry().find_unit("kM") is KILOMETER


def test_find_unit_by_alias() -> None:
    assert make_registry().find_unit("kilometres") is KILOMETER


def test_find_unit_by_alias_ignoring_case() -> None:
    assert make_registry().find_unit("KiloMetrES") is KILOMETER


def test_find_unit_ignores_surrounding_and_repeated_spaces() -> None:
    assert make_registry().find_unit("  Degrees   Celsius ") is CELSIUS


def test_find_unit_matches_symbols_case_insensitively() -> None:
    assert make_registry().find_unit("k") is KELVIN


def test_categories_keep_the_given_order() -> None:
    assert make_registry().categories == (LENGTH, TEMPERATURE)


def test_category_of_returns_the_unit_category() -> None:
    registry = make_registry()
    assert registry.category_of(KILOMETER) is LENGTH
    assert registry.category_of(CELSIUS) is TEMPERATURE


def test_category_of_returns_none_for_unknown_unit() -> None:
    registry = make_registry()
    assert registry.category_of(make_unit()) is None


def test_aliases_contains_normalized_keys() -> None:
    aliases = make_registry().aliases()
    expected_aliases = (
        "meter",
        "m",
        "metre",
        "meters",
        "metres",
        "kilometer",
        "km",
        "kilometre",
        "kilometers",
        "kilometres",
        "kelvin",
        "k",
        "celsius",
        "c",
        "degree celsius",
        "degrees celsius",
    )
    assert sorted(aliases) == sorted(expected_aliases)


def test_aliases_are_all_normalized() -> None:
    for key in make_registry().aliases():
        assert key == normalize(key)


def test_registry_accepts_any_iterable_of_categories() -> None:
    registry = Registry(category for category in (LENGTH, TEMPERATURE))
    assert registry.categories == (LENGTH, TEMPERATURE)


def test_unit_with_an_offset_loads() -> None:
    assert make_registry().find_unit("celsius") is CELSIUS


# --- Lookups: misses ---


@pytest.mark.parametrize("name", ["blorp", "gallon", "", "   "])
def test_find_unit_returns_none_for_unknown_names(name: str) -> None:
    assert make_registry().find_unit(name) is None


# --- Repeated names inside one unit ---


def test_repeating_a_name_inside_one_unit_is_ignored() -> None:
    unit = make_unit(aliases=("a", "A", "a"))
    registry = Registry([make_category(unit)])
    assert registry.aliases() == ("a",)
    assert registry.find_unit("A") is unit


# --- Validation: categories ---


def test_duplicate_category_name_is_rejected() -> None:
    with pytest.raises(
        RegistryError,
        match="^RegistryError: duplicate category name 'length'.$",
    ):
        Registry([LENGTH, LENGTH])


def test_category_without_its_base_unit_is_rejected() -> None:
    category = make_category(make_unit(), base_id="zz")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: category 'x' has no unit with its base id 'zz'.$",
    ):
        Registry([category])


def test_category_without_units_is_rejected() -> None:
    with pytest.raises(
        RegistryError,
        match="^RegistryError: category 'z' has no unit with its base id 'a'.$",
    ):
        Registry([make_category(name="z")])


def test_base_unit_with_wrong_factor_is_rejected() -> None:
    category = make_category(make_unit(factor=2))
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: base unit 'a' of category 'x' "
            r"must have factor 1 and offset 0\.$"
        ),
    ):
        Registry([category])


def test_base_unit_with_an_offset_is_rejected() -> None:
    category = make_category(make_unit(offset=1.0))
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: base unit 'a' of category 'x' "
            r"must have factor 1 and offset 0\.$"
        ),
    ):
        Registry([category])


# --- Validation: units ---


def test_duplicate_unit_id_in_one_category_is_rejected() -> None:
    category = make_category(make_unit(), make_unit(name="b", symbol="b"))
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: duplicate unit id 'a' "
            r"found in category 'x'\.$"
        ),
    ):
        Registry([category])


def test_duplicate_unit_id_across_categories_is_rejected() -> None:
    first = make_category(make_unit(), name="first")
    second = make_category(make_unit(name="b", symbol="b"), name="second")
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: duplicate unit id 'a' "
            r"found in categories ('first' and 'second'|'second' and 'first')\.$"
        ),
    ):
        Registry([first, second])


@pytest.mark.parametrize(
    "factor", [0, -1, -0.5, float("nan"), float("inf"), float("-inf")]
)
def test_invalid_factor_is_rejected(factor: float) -> None:
    category = make_category(
        make_unit(), make_unit(id="b", name="b", symbol="b", factor=factor)
    )
    with pytest.raises(
        RegistryError,
        match=(
            f"^RegistryError: unit 'b' has an invalid factor '{factor}': "
            f"it must be positive and finite.$"
        ),
    ):
        Registry([category])


@pytest.mark.parametrize("offset", [float("nan"), float("inf"), float("-inf")])
def test_invalid_offset_is_rejected(offset: float) -> None:
    category = make_category(
        make_unit(), make_unit(id="b", name="b", symbol="b", offset=offset)
    )
    with pytest.raises(
        RegistryError,
        match=(
            f"^RegistryError: unit 'b' has an invalid offset '{offset}': "
            f"it must be finite.$"
        ),
    ):
        Registry([category])


# --- Validation: names, symbols and aliases ---


def test_empty_name_is_rejected() -> None:
    category = make_category(make_unit(name=" "))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: unit 'a' has an empty name.$",
    ):
        Registry([category])


def test_empty_symbol_is_rejected() -> None:
    category = make_category(make_unit(symbol=""))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: unit 'a' has an empty symbol.$",
    ):
        Registry([category])


def test_empty_alias_is_rejected() -> None:
    category = make_category(make_unit(aliases=("ok", "  ")))
    with pytest.raises(
        RegistryError,
        match="^RegistryError: unit 'a' has an empty alias.$",
    ):
        Registry([category])


def test_alias_shared_by_two_units_in_one_category_is_rejected() -> None:
    second = make_unit(id="b", name="b", symbol="b", aliases=("A",))
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: key 'a' is used by "
            r"both unit ('a' and unit 'b'|'b' and unit 'a')\.$"
        ),
    ):
        Registry([make_category(make_unit(), second)])


def test_alias_shared_across_categories_is_rejected() -> None:
    first = make_category(make_unit(), name="first")
    other_base = make_unit(id="b", name="b", symbol="b", aliases=("a",))
    second = make_category(other_base, base_id="b", name="second")
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: key 'a' is used by "
            r"both unit ('a' and unit 'b'|'b' and unit 'a')\.$"
        ),
    ):
        Registry([first, second])


def test_name_colliding_with_another_units_symbol_is_rejected() -> None:
    second = make_unit(id="b", name="a", symbol="b")
    with pytest.raises(
        RegistryError,
        match="^RegistryError: .*is used by both unit",
    ):
        Registry([make_category(make_unit(), second)])


def test_symbols_differing_only_by_case_are_rejected() -> None:
    first = make_unit(id="m1", name="m1", symbol="mm")
    second = make_unit(id="m2", name="m2", symbol="Mm")
    with pytest.raises(
        RegistryError,
        match=(
            r"^RegistryError: key 'mm' is used by "
            r"both unit ('m1' and unit 'm2'|'m2' and unit 'm1')\.$"
        ),
    ):
        Registry([make_category(first, second, base_id="m1")])


# --- Unsupported names ---


UNSUPPORTED_TEST = ("gallon", "Pint", "fl oz")


def make_registry_with_unsupported() -> Registry:
    return Registry([LENGTH, TEMPERATURE], unsupported=UNSUPPORTED_TEST)


def test_no_name_is_unsupported_by_default() -> None:
    assert not make_registry().is_unsupported("gallon")


@pytest.mark.parametrize(
    "name",
    ["gallon", "GALLON", "  Gallon  ", "pint", "Pint", "fl oz", "FL   OZ"],
)
def test_listed_names_are_unsupported(name: str) -> None:
    assert make_registry_with_unsupported().is_unsupported(name)


@pytest.mark.parametrize("name", ["meter", "km", "Celsius", "blorp", "", "   "])
def test_other_names_are_not_unsupported(name: str) -> None:
    assert not make_registry_with_unsupported().is_unsupported(name)


def test_unsupported_names_accept_any_iterable() -> None:
    registry = Registry(
        [LENGTH, TEMPERATURE], unsupported=(name for name in UNSUPPORTED_TEST)
    )
    assert registry.is_unsupported("gallon")


def test_repeated_unsupported_names_are_ignored() -> None:
    registry = Registry(
        [LENGTH, TEMPERATURE], unsupported=["gallon", "Gallon", "  GALLON "]
    )
    assert registry.is_unsupported("gallon")


@pytest.mark.parametrize("name", ["", "   "])
def test_empty_unsupported_name_is_rejected(name: str) -> None:
    with pytest.raises(
        RegistryError,
        match=f"^RegistryError: unsupported name '{name}' is empty.$",
    ):
        Registry([LENGTH, TEMPERATURE], unsupported=["gallon", name])


@pytest.mark.parametrize(
    ("name", "unit_id"),
    [
        ("Kilometer", "kilometer"),
        ("km", "kilometer"),
        ("metres", "meter"),
        ("  CELSIUS ", "celsius"),
    ],
)
def test_unsupported_name_that_is_also_supported_is_rejected(
    name: str, unit_id: str
) -> None:
    with pytest.raises(
        RegistryError,
        match=(
            f"^RegistryError: unsupported name '{name}' is a supported name "
            f"of unit '{unit_id}'.$"
        ),
    ):
        Registry([LENGTH, TEMPERATURE], unsupported=[name])


def test_unsupported_names_are_not_found_as_units() -> None:
    assert make_registry_with_unsupported().find_unit("gallon") is None


def test_unsupported_names_are_not_suggestion_keys() -> None:
    assert "gallon" not in make_registry_with_unsupported().aliases()


def test_unsupported_names_do_not_change_the_aliases() -> None:
    assert make_registry().aliases() == make_registry_with_unsupported().aliases()


# --- Formatter ---


@pytest.mark.parametrize("x", [0, 0.0, -0.0])
def test_zero_is_shown_as_zero(x: float) -> None:
    assert format_number(x) == "0"


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (5, "5"),
        (5.0, "5"),
        (5.5, "5.5"),
        (100, "100"),
        (100000, "100000"),
        (999999, "999999"),
        (0.5, "0.5"),
        (0.1, "0.1"),
        (1234.5678, "1234.5678"),
        (123456.789, "123456.789"),
        (12.345678, "12.3457"),
        (6.21371192, "6.2137"),
        (999999.5, "999999.5"),
    ],
)
def test_ordinary_values_use_up_to_four_decimals(x: float, expected: str) -> None:
    assert format_number(x) == expected


def test_trailing_zeros_are_removed() -> None:
    assert format_number(2.5000) == "2.5"
    assert format_number(1.00001) == "1"


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (-5, "-5"),
        (-0.5, "-0.5"),
        (-1234.5678, "-1234.5678"),
        (-0.00001234, "-1.234e-5"),
        (-1e6, "-1e6"),
    ],
)
def test_negative_values_keep_their_sign(x: float, expected: str) -> None:
    assert format_number(x) == expected


# --- Small values: at least 4 significant digits ---


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (0.123456, "0.1235"),
        (0.012345678, "0.01235"),
        (0.0012345678, "0.001235"),
        (0.000123456, "0.0001235"),
        (0.00015, "0.00015"),
        (0.0001, "0.0001"),
    ],
)
def test_small_values_keep_four_significant_digits(x: float, expected: str) -> None:
    assert format_number(x) == expected


# --- Scientific notation ---


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (1e6, "1e6"),
        (2e7, "2e7"),
        (1234567890, "1.235e9"),
        (1.5e12, "1.5e12"),
        (0.00009999, "9.999e-5"),
        (0.00001234, "1.234e-5"),
        (1e-10, "1e-10"),
    ],
)
def test_extreme_values_use_scientific_notation(x: float, expected: str) -> None:
    assert format_number(x) == expected


def test_scientific_notation_has_no_plus_sign_or_padding() -> None:
    for x in (1e6, 2.5e9, 1.2e-5, 3e-10, 4e100):
        text = format_number(x)
        assert "e+" not in text
        assert "e0" not in text
        assert "e-0" not in text


# --- Thresholds ---


def test_the_upper_threshold_is_one_million() -> None:
    assert format_number(999999) == "999999"
    assert format_number(1000000) == "1e6"


def test_the_lower_threshold_is_one_ten_thousandth() -> None:
    assert format_number(0.0001) == "0.0001"
    assert format_number(0.00009999) == "9.999e-5"


def test_rounding_across_the_upper_threshold_switches_notation() -> None:
    # Fixed notation would show 1000000.0000, which is not allowed.
    assert format_number(999999.99996) == "1e6"


def test_rounding_up_to_the_next_power_of_ten_is_clean() -> None:
    assert format_number(0.99996) == "1"
    assert format_number(0.00099999) == "0.001"


def test_just_below_the_lower_threshold_can_round_up_to_it() -> None:
    assert format_number(0.000099999) == "1e-4"


# --- Properties ---


@pytest.mark.parametrize(
    "x",
    [5, 5.5, 0.5, 1234.5678, 12.345678, 0.000123456, 1e6, 1e-10, -3.25, 123456.789],
)
def test_output_never_ends_with_a_decimal_point_or_zero_decimals(x: float) -> None:
    text = format_number(x)
    mantissa = text.split("e")[0]
    if "." in mantissa:
        assert not mantissa.endswith("0")
        assert not mantissa.endswith(".")


@pytest.mark.parametrize("x", [0.1, 12.5, 999.999, 0.00123, 123456.7])
def test_fixed_output_reads_back_close_to_the_input(x: float) -> None:
    assert float(format_number(x)) == pytest.approx(x, rel=1e-3)


@pytest.mark.parametrize("x", [1e6, 1.234e8, 5.5e-5, 9e-9, -2e12])
def test_scientific_output_reads_back_close_to_the_input(x: float) -> None:
    assert float(format_number(x)) == pytest.approx(x, rel=1e-3)


# --- Non-finite values ---


def test_infinities_are_shown_as_such() -> None:
    assert format_number(math.inf) == "inf"
    assert format_number(-math.inf) == "-inf"


def test_nan_is_shown_as_nan() -> None:
    assert format_number(math.nan) == "nan"


# --- format_quantity ---


def make_unit_(symbol: str) -> Unit:
    return Unit(id="u", name="u", symbol=symbol, factor=1)


@pytest.mark.parametrize(
    ("value", "symbol", "expected"),
    [
        (6.21371192, "mi", "6.2137 mi"),
        (0, "C", "0 C"),
        (2e7, "m", "2e7 m"),
        (-40, "F", "-40 F"),
        (0.000123456, "kg", "0.0001235 kg"),
    ],
)
def test_quantity_is_shown_as_number_and_symbol(
    value: float, symbol: str, expected: str
) -> None:
    assert format_quantity(Quantity(value, make_unit_(symbol))) == expected


# --- Resolver ---


def make_registry_(*units: Unit, base_id: str) -> Registry:
    """Build a small registry, to test the mechanics on controlled data."""
    category = Category(name="x", base_unit_id=base_id, units=units)
    return Registry([category])


# --- Names that resolve ---


@pytest.mark.parametrize(
    ("name", "unit_id"),
    [
        ("kilometer", "kilometer"),
        ("km", "kilometer"),
        ("Kilometres", "kilometer"),
        ("  FEET ", "foot"),
        ("degrees   celsius", "celsius"),
        ("K", "kelvin"),
    ],
)
def test_resolve_finds_the_unit(name: str, unit_id: str) -> None:
    assert resolve(name, REGISTRY).id == unit_id


def test_resolve_returns_the_registry_unit() -> None:
    assert resolve("miles", REGISTRY) is REGISTRY.find_unit("miles")


# --- Unsupported names ---


@pytest.mark.parametrize("name", ["gallon", "Gallons", "  PINT ", "fl oz", "year"])
def test_resolve_rejects_unsupported_names(name: str) -> None:
    with pytest.raises(UnsupportedUnitError) as info:
        resolve(name, REGISTRY)
    assert info.value.name == name


# --- Unknown names ---


def test_resolve_rejects_unknown_names_and_keeps_the_text() -> None:
    with pytest.raises(UnknownUnitError) as info:
        resolve("Blorp", REGISTRY)
    assert info.value.name == "Blorp"


@pytest.mark.parametrize("name", ["", "   "])
def test_resolve_rejects_empty_names_without_suggestions(name: str) -> None:
    with pytest.raises(UnknownUnitError) as info:
        resolve(name, REGISTRY)
    assert info.value.suggestions == ()


def test_unknown_unit_error_carries_the_suggestions() -> None:
    with pytest.raises(UnknownUnitError) as info:
        resolve("kilomter", REGISTRY)
    assert sorted(info.value.suggestions) == sorted(suggest_units("kilomter", REGISTRY))
    assert "kilometer" in info.value.suggestions


# --- Suggestions ---

# (typo, the unit that should be suggested first)
TYPOS = [
    ("metr", "meter"),
    ("kilomter", "kilometer"),
    ("KILOMTER", "kilometer"),
    ("kilogam", "kilogram"),
    ("milimeter", "millimeter"),
    ("litr", "liter"),
    ("pund", "pound"),
    ("wek", "week"),
    ("secnd", "second"),
    ("celcius", "celsius"),
    ("farenheit", "fahrenheit"),
    ("kelvn", "kelvin"),
    ("nauticalmile", "nautical mile"),
    ("nautical mil", "nautical mile"),
]


@pytest.mark.parametrize(("typo", "expected"), TYPOS)
def test_a_typo_suggests_the_right_unit_first(typo: str, expected: str) -> None:
    assert suggest_units(typo, REGISTRY)[0] == expected


@pytest.mark.parametrize(
    "name", ["blorp", "xyz", "abc", "galon", "miles per hour", "m2", ""]
)
def test_nothing_close_gives_no_suggestions(name: str) -> None:
    assert suggest_units(name, REGISTRY) == ()


def test_suggestions_are_limited() -> None:
    units = tuple(
        Unit(id=f"abcd{i}", name=f"abcd{i}", symbol=f"s{i}", factor=1)
        for i in range(1, 6)
    )
    registry = make_registry_(*units, base_id="abcd1")
    suggestions = suggest_units("abcd", registry)
    assert len(suggestions) == MAX_SUGGESTIONS


def test_suggestions_are_a_tuple_of_strings() -> None:
    suggestions = suggest_units("kilomter", REGISTRY)
    assert isinstance(suggestions, tuple)
    assert all(isinstance(s, str) for s in suggestions)


def test_suggestions_never_include_unsupported_names() -> None:
    for name in ("gallo", "tonn", "yeer", "pin"):
        assert not set(suggest_units(name, REGISTRY)) & set(UNSUPPORTED)


# --- Converter ---


def unit_(unit_id: str) -> Unit:
    found = REGISTRY.find_unit(unit_id.replace("_", " "))
    assert found is not None, f"unit '{unit_id}' not found"
    return found


def converted(value: float, from_id: str, to_id: str) -> float:
    return convert_(Quantity(value, unit_(from_id)), unit_(to_id), REGISTRY).value


# --- Parse ---


def test_parse_builds_a_quantity() -> None:
    quantity = parse("10", "km", REGISTRY)
    assert quantity.value == 10.0
    assert quantity.unit is unit_("kilometer")


@pytest.mark.parametrize("value", ["10", " 10 ", 10, 10.0])
def test_parse_accepts_text_and_numbers(value: str | float) -> None:
    assert parse(value, "meter", REGISTRY).value == 10.0


def test_parse_accepts_flexible_unit_names() -> None:
    assert parse("1", "  KILOMETRES ", REGISTRY).unit is unit_("kilometer")


def test_parse_rejects_an_invalid_number() -> None:
    with pytest.raises(InvalidNumberError):
        parse("abc", "km", REGISTRY)


def test_parse_rejects_an_unknown_unit() -> None:
    with pytest.raises(UnknownUnitError):
        parse("1", "blorp", REGISTRY)


def test_parse_rejects_an_unsupported_unit() -> None:
    with pytest.raises(UnsupportedUnitError):
        parse("1", "gallon", REGISTRY)


def test_parse_reports_the_number_first_when_both_are_wrong() -> None:
    with pytest.raises(InvalidNumberError):
        parse("abc", "blorp", REGISTRY)


# --- Reference SI conversions to base unit ---


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [
        # Length, in meters
        (1, "millimeter", "meter", 0.001),
        (1, "centimeter", "meter", 0.01),
        (1, "decimeter", "meter", 0.1),
        (1, "meter", "meter", 1),
        (1, "kilometer", "meter", 1000),
        (1, "inch", "meter", 0.0254),
        (1, "foot", "meter", 0.3048006096),
        (1, "yard", "meter", 0.91440183),
        (1, "mile", "meter", 1609.344),
        (1, "nautical mile", "meter", 1852),
        # Mass, in kilograms
        (1, "milligram", "kilogram", 1e-6),
        (1, "gram", "kilogram", 0.001),
        (1, "kilogram", "kilogram", 1),
        (1, "metric ton", "kilogram", 1000),
        (1, "ounce", "kilogram", 0.028349523125),
        (1, "pound", "kilogram", 0.45359237),
        (1, "stone", "kilogram", 6.35029318),
        # Volume, in liters
        (1, "milliliter", "liter", 0.001),
        (1, "cubic centimeter", "liter", 0.001),
        (1, "liter", "liter", 1),
        (1, "cubic meter", "liter", 1000),
        (1, "cubic inch", "liter", 0.016387064),
        (1, "cubic foot", "liter", 28.316846592),
        # Time, in seconds
        (1, "millisecond", "second", 0.001),
        (1, "second", "second", 1),
        (1, "minute", "second", 60),
        (1, "hour", "second", 3600),
        (1, "day", "second", 86400),
        (1, "week", "second", 604800),
        # Temperature, in kelvin
        (0, "celsius", "kelvin", 273.15),
        (1, "kelvin", "kelvin", 1),
        (32, "fahrenheit", "kelvin", 273.15),
    ],
)
def test_reference_conversion_to_base_unit(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


# --- Reference conversions ---


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [
        (10, "kilometer", "mile", 6.2137119224),
        (1, "mile", "kilometer", 1.609344),
        (1, "inch", "centimeter", 2.54),
        (1, "foot", "inch", 12),
        (1, "nautical_mile", "meter", 1852),
        (1, "pound", "gram", 453.59237),
        (16, "ounce", "pound", 1),
        (1, "stone", "pound", 14),
        (1, "metric_ton", "kilogram", 1000),
        (1, "liter", "cubic_centimeter", 1000),
        (1, "cubic_foot", "liter", 28.316846592),
        (1, "cubic_meter", "liter", 1000),
        (1, "week", "hour", 168),
        (1, "day", "minute", 1440),
        (90, "minute", "hour", 1.5),
        (100, "celsius", "fahrenheit", 212),
        (32, "fahrenheit", "celsius", 0),
        (0, "kelvin", "celsius", -273.15),
        (0, "celsius", "kelvin", 273.15),
        (-40, "celsius", "fahrenheit", -40),
        (98.6, "fahrenheit", "celsius", 37),
    ],
)
def test_reference_conversion(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-5, abs=1e-9
    )


# --- Every pair of units in a category ---

# Size of each linear unit in its category's base unit, typed here
# independently of the data modules.
LINEAR_FACTORS: dict[str, dict[str, float]] = {
    "length": {
        "millimeter": 0.001,
        "centimeter": 0.01,
        "decimeter": 0.1,
        "meter": 1,
        "kilometer": 1000,
        "inch": 0.0254,
        "foot": 0.3048,
        "yard": 0.9144,
        "mile": 1609.344,
        "nautical_mile": 1852,
    },
    "mass": {
        "milligram": 1e-6,
        "gram": 0.001,
        "kilogram": 1,
        "metric_ton": 1000,
        "ounce": 0.028349523125,
        "pound": 0.45359237,
        "stone": 6.35029318,
    },
    "volume": {
        "milliliter": 0.001,
        "cubic_centimeter": 0.001,
        "liter": 1,
        "cubic_meter": 1000,
        "cubic_inch": 0.016387064,
        "cubic_foot": 28.316846592,
    },
    "time": {
        "millisecond": 0.001,
        "second": 1,
        "minute": 60,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
    },
}


# --- Test temperature cross-conversions ---

TO_KELVIN: dict[str, Callable[[float], float]] = {
    "kelvin": lambda t: t,
    "celsius": lambda t: t + 273.15,
    "fahrenheit": lambda t: (t + 459.67) * 5 / 9,
}


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [(7, from_id, "kelvin", f(7)) for from_id, f in TO_KELVIN.items()],
)
def test_conversion_to_kelvin(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


TO_CELCIUS: dict[str, Callable[[float], float]] = {
    "kelvin": lambda t: t - 273.15,
    "celsius": lambda t: t,
    "fahrenheit": lambda t: (t - 32) * 5 / 9,
}


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [(7, from_id, "celsius", f(7)) for from_id, f in TO_CELCIUS.items()],
)
def test_conversion_to_celcius(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


TO_FAHRENHEIT: dict[str, Callable[[float], float]] = {
    "kelvin": lambda t: t * 9 / 5 - 459.67,
    "celsius": lambda t: t * 9 / 5 + 32,
    "fahrenheit": lambda t: t,
}


@pytest.mark.parametrize(
    ("value", "from_id", "to_id", "expected"),
    [(7, from_id, "fahrenheit", f(7)) for from_id, f in TO_FAHRENHEIT.items()],
)
def test_conversion_to_fahrenheit(
    value: float, from_id: str, to_id: str, expected: float
) -> None:
    assert converted(value, from_id, to_id) == pytest.approx(
        expected, rel=1e-6, abs=1e-9
    )


# --- Result and inputs ---


def test_the_result_is_a_quantity_in_the_target_unit() -> None:
    result = convert_(Quantity(10, unit_("kilometer")), unit_("mile"), REGISTRY)
    assert isinstance(result, Quantity)
    assert result.unit is unit_("mile")


def test_the_original_quantity_is_not_modified() -> None:
    original = Quantity(10, unit_("kilometer"))
    convert_(original, unit_("mile"), REGISTRY)
    assert original.value == 10
    assert original.unit is unit_("kilometer")


def test_converting_to_the_same_unit_returns_the_exact_value() -> None:
    # No arithmetic, so no floating-point noise (0.1 C would not survive it).
    assert converted(0.1, "celsius", "celsius") == 0.1
    assert converted(123.456, "mile", "mile") == 123.456


# --- Edge cases ---


def test_zero_converts_to_zero_for_linear_units() -> None:
    assert converted(0, "kilometer", "mile") == 0


def test_negative_values_convert() -> None:
    assert converted(-5, "kilometer", "meter") == pytest.approx(-5000)


def test_very_large_values_convert() -> None:
    assert converted(1e300, "meter", "kilometer") == pytest.approx(1e297)


def test_very_small_values_convert() -> None:
    assert converted(1e-300, "kilometer", "meter") == pytest.approx(1e-297)


def test_a_result_too_large_to_represent_becomes_infinity() -> None:
    # Known limitation: float overflow, documented in convert_().
    assert math.isinf(converted(1e308, "kilometer", "millimeter"))


def test_absolute_zero_is_the_same_in_every_scale() -> None:
    assert converted(0, "kelvin", "fahrenheit") == pytest.approx(-459.67)
    assert converted(-273.15, "celsius", "kelvin") == pytest.approx(0, abs=1e-9)


# --- Errors ---


def test_units_of_different_categories_are_rejected() -> None:
    with pytest.raises(IncompatibleUnitsError) as info:
        convert_(Quantity(1, unit_("kilogram")), unit_("meter"), REGISTRY)
    assert info.value.from_category == "mass"
    assert info.value.to_category == "length"


@pytest.mark.parametrize(
    ("from_id", "to_id"),
    [
        ("celsius", "kilogram"),
        ("second", "liter"),
        ("liter", "celsius"),
        ("meter", "second"),
    ],
)
def test_other_cross_category_conversions_are_rejected(
    from_id: str, to_id: str
) -> None:
    with pytest.raises(IncompatibleUnitsError):
        converted(1, from_id, to_id)


def test_incompatible_units_are_a_converter_error() -> None:
    with pytest.raises(ConverterError):
        converted(1, "kilogram", "meter")


def test_a_unit_from_another_registry_is_rejected() -> None:
    stranger = Unit(id="furlong", name="furlong", symbol="fur", factor=201.168)
    with pytest.raises(ConverterError):
        convert_(Quantity(1, stranger), unit_("meter"), REGISTRY)


# --- API ---


def test_convert_returns_a_quantity_in_the_target_unit() -> None:
    result = convert("10", "km", "miles")
    assert isinstance(result, Quantity)
    assert result.unit.id == "mile"
    assert result.value == pytest.approx(6.2137119223733395, rel=1e-6)


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit", "expected"),
    [
        ("100", "celsius", "fahrenheit", 212),
        (" 32 ", "Fahrenheit", "CELSIUS", 0),
        (1, "KILOMETRES", "  metres ", 1000),
        (2.5, "kg", "grams", 2500),
        ("1e3", "m", "km", 1),
        ("90", "minutes", "hours", 1.5),
    ],
)
def test_convert_accepts_flexible_input(
    value: str | float, from_unit: str, to_unit: str, expected: float
) -> None:
    result = convert(value, from_unit, to_unit)
    assert result.value == pytest.approx(expected, rel=1e-6, abs=1e-9)


# --- convert_and_format ---


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit", "expected"),
    [
        ("10", "km", "miles", "6.2137 mi"),
        ("100", "celsius", "fahrenheit", "212 F"),
        ("0", "kelvin", "celsius", "-273.15 C"),
        ("1", "mile", "kilometer", "1.6093 km"),
        ("5", "km", "mm", "5e6 mm"),
        ("1", "mm", "km", "1e-6 km"),
        ("0", "m", "km", "0 km"),
    ],
)
def test_convert_and_format_returns_display_text(
    value: str, from_unit: str, to_unit: str, expected: str
) -> None:
    assert convert_and_format(value, from_unit, to_unit) == expected


# --- Errors ---


def test_an_invalid_number_is_reported() -> None:
    with pytest.raises(InvalidNumberError):
        convert("abc", "km", "miles")


def test_an_unknown_source_unit_is_reported() -> None:
    with pytest.raises(UnknownUnitError) as info:
        convert("1", "kilomter", "miles")
    assert "kilometer" in info.value.suggestions


def test_an_unknown_target_unit_is_reported() -> None:
    with pytest.raises(UnknownUnitError) as info:
        convert("1", "km", "mils")
    assert info.value.name == "mils"


@pytest.mark.parametrize(
    ("from_unit", "to_unit"), [("gallon", "liter"), ("liter", "pints")]
)
def test_an_unsupported_unit_is_reported(from_unit: str, to_unit: str) -> None:
    with pytest.raises(UnsupportedUnitError):
        convert("1", from_unit, to_unit)


def test_units_of_different_categories_are_reported() -> None:
    with pytest.raises(IncompatibleUnitsError):
        convert("1", "kg", "meter")


def test_the_number_is_checked_first() -> None:
    with pytest.raises(InvalidNumberError):
        convert("abc", "blorp", "blorp")


def test_the_source_unit_is_checked_before_the_target_unit() -> None:
    with pytest.raises(UnknownUnitError) as info:
        convert("1", "blorp", "gallon")
    assert info.value.name == "blorp"


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit"),
    [
        ("abc", "km", "miles"),
        ("1", "blorp", "miles"),
        ("1", "gallon", "liter"),
        ("1", "kg", "meter"),
    ],
)
def test_every_user_error_is_a_converter_error(
    value: str, from_unit: str, to_unit: str
) -> None:
    with pytest.raises(ConverterError):
        convert_and_format(value, from_unit, to_unit)


# --- Registry and unit list ---


def test_the_registry_is_built_only_once() -> None:
    assert get_registry() is get_registry()


def test_list_units_returns_the_five_categories() -> None:
    assert list(list_units()) == [
        "length",
        "mass",
        "volume",
        "time",
        "temperature",
    ]


def test_list_units_returns_readable_unit_names() -> None:
    units = list_units()
    assert {"kilometer": "km"} in units["length"]
    assert {"nautical mile": "nmi"} in units["length"]
    assert units["temperature"] == (
        {"kelvin": "K"},
        {"celsius": "C"},
        {"fahrenheit": "F"},
    )


def test_every_listed_unit_name_can_be_converted_from() -> None:
    for names in list_units().values():
        for name_key in names:
            keys = [n for n in name_key]
            assert len(keys) == 1
            name = keys[0]
            assert convert("1", name, name).value == 1


# --- Building blocks: parse_quantity and convert_quantity ---


def test_parse_quantity_builds_a_quantity() -> None:
    quantity = parse_quantity("10", "Kilometres")
    assert quantity.value == 10.0
    assert quantity.unit.symbol == "km"


def test_parse_quantity_reports_the_number_first() -> None:
    with pytest.raises(InvalidNumberError):
        parse_quantity("abc", "blorp")


def test_parse_quantity_reports_an_unknown_unit() -> None:
    with pytest.raises(UnknownUnitError):
        parse_quantity("1", "blorp")


def test_convert_quantity_converts_to_a_named_unit() -> None:
    result = convert_quantity(parse_quantity("10", "km"), "miles")
    assert result.unit.symbol == "mi"
    assert result.value == pytest.approx(6.2137119223733395, rel=1e-6)


def test_convert_quantity_does_not_modify_its_input() -> None:
    quantity = parse_quantity("10", "km")
    convert_quantity(quantity, "miles")
    assert quantity.value == 10.0
    assert quantity.unit.symbol == "km"


def test_convert_quantity_rejects_an_unsupported_target() -> None:
    with pytest.raises(UnsupportedUnitError):
        convert_quantity(parse_quantity("1", "liter"), "gallon")


def test_convert_quantity_rejects_incompatible_units() -> None:
    with pytest.raises(IncompatibleUnitsError):
        convert_quantity(parse_quantity("1", "kg"), "meter")


def test_convert_is_parse_then_convert() -> None:
    direct = convert("10", "km", "miles")
    composed = convert_quantity(parse_quantity("10", "km"), "miles")
    assert direct == composed


# --- Utils ---


@pytest.mark.parametrize("name", ["celsius", "Celsius", "CELSIUS", "cElSiUs"])
def test_case_is_ignored(name: str) -> None:
    assert normalize(name) == "celsius"


def test_casefold_handles_non_english_letters() -> None:
    # casefold (not lower) so that "ß" and "SS" compare equal.
    assert normalize("Straße") == normalize("STRASSE")


# --- Whitespace ---


def test_leading_and_trailing_whitespace_is_removed() -> None:
    assert normalize("  celsius  ") == "celsius"


def test_repeated_inner_spaces_are_collapsed() -> None:
    assert normalize("degrees    celsius") == "degrees celsius"


def test_tabs_and_newlines_count_as_whitespace() -> None:
    assert normalize("\tdegrees\n celsius\t") == "degrees celsius"


def test_non_breaking_space_counts_as_whitespace() -> None:
    # Written as an escape so the exact character is visible.
    assert normalize("nautical\u00a0 mile") == "nautical mile"


# --- Empty input ---


@pytest.mark.parametrize("name", ["", " ", "   ", "\t\n"])
def test_empty_and_whitespace_only_input_returns_empty_string(name: str) -> None:
    assert normalize(name) == ""


# --- What normalize must not do ---


@pytest.mark.parametrize("name", ["feet", "inches", "metres", "kilometers"])
def test_plurals_are_left_untouched(name: str) -> None:
    assert normalize(name) == name


def test_spelling_is_not_corrected() -> None:
    assert normalize("Kilometre") == "kilometre"


# --- Properties ---


@pytest.mark.parametrize(
    "name",
    [
        "Celsius",
        "  DEGREES   Celsius ",
        "nautical\u00a0 MILE",
        "Straße",
        "",
        "   ",
        "km",
    ],
)
def test_normalize_is_idempotent(name: str) -> None:
    once = normalize(name)
    assert normalize(once) == once


def test_non_ascii_input_does_not_crash() -> None:
    assert normalize("  Ünït ñame 单位 ") == "ünït ñame 单位"


# --- MAIN ---


def run(capsys: pytest.CaptureFixture[str], argv: list[str]) -> tuple[int, str, str]:
    """Run the CLI, returning its exit code, standard output and standard error."""
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def run_expecting_exit(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> tuple[int, str, str]:
    """Run the CLI when argparse is expected to exit (usage errors, help)."""
    with pytest.raises(SystemExit) as info:
        main(argv)
    captured = capsys.readouterr()
    assert isinstance(info.value.code, int)
    return info.value.code, captured.out, captured.err


# --- Successful conversions ---


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        (["-v", "10", "--from", "km", "--to", "miles"], "10 km = 6.2137 mi"),
        (["-v", "100", "--from", "celsius", "--to", "fahrenheit"], "100 C = 212 F"),
        (["-v", "-40", "--from", "celsius", "--to", "fahrenheit"], "-40 C = -40 F"),
        (["-v", "-2.5", "--from", "m", "--to", "cm"], "-2.5 m = -250 cm"),
        (["-v", "0", "--from", "kelvin", "--to", "celsius"], "0 K = -273.15 C"),
        (["-v", "5", "--from", "km", "--to", "mm"], "5 km = 5e6 mm"),
        (["-v", "1e3", "--from", "m", "--to", "km"], "1000 m = 1 km"),
        (["-v", "1", "--from", "KILOMETRES", "--to", "  Metres "], "1 km = 1000 m"),
        (["-v", "5", "--from", "nautical mile", "--to", "km"], "5 nmi = 9.26 km"),
        (["-v", "2", "--from", "lb", "--to", "oz"], "2 lb = 32 oz"),
    ],
)
def test_conversion_prints_source_and_result(
    capsys: pytest.CaptureFixture[str], argv: list[str], expected: str
) -> None:
    code, out, err = run(capsys, argv)
    assert code == 0
    assert out == expected + "\n"
    assert err == ""


def test_a_unit_symbol_is_shown_canonically(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # "Kilometres" typed by the user is shown as the symbol "km".
    _, out, _ = run(capsys, ["-v", "3", "--from", "Kilometres", "--to", "Meters"])
    assert out == "3 km = 3000 m\n"


def test_main_reads_sys_argv_when_given_no_arguments(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        sys, "argv", ["python project.py", "-v", "10", "--from", "km", "--to", "miles"]
    )
    assert main() == 0
    assert capsys.readouterr().out == "10 km = 6.2137 mi\n"


# --- Conversion errors ---


@pytest.mark.parametrize(
    ("argv", "expected_in_message"),
    [
        (["-v", "abc", "--from", "km", "--to", "miles"], "InvalidNumberError"),
        (["-v", "1,5", "--from", "km", "--to", "miles"], "InvalidNumberError"),
        (["-v", "nan", "--from", "km", "--to", "miles"], "InvalidNumberError"),
        (["-v", "1", "--from", "kilomter", "--to", "miles"], "UnknownUnitError"),
        (["-v", "1", "--from", "km", "--to", "mils"], "UnknownUnitError"),
        (["-v", "1", "--from", "gallon", "--to", "liter"], "UnsupportedUnitError"),
        (["-v", "1", "--from", "liter", "--to", "pints"], "UnsupportedUnitError"),
        (["-v", "1", "--from", "kg", "--to", "meter"], "IncompatibleUnitsError"),
        (
            ["-v", "1", "--from", "celsius", "--to", "kilogram"],
            "IncompatibleUnitsError",
        ),
    ],
)
def test_conversion_errors_go_to_stderr_with_exit_code_1(
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
    expected_in_message: str,
) -> None:
    code, out, err = run(capsys, argv)
    assert code == 1
    assert out == ""
    assert expected_in_message in err
    assert err.endswith("\n")
    assert "Traceback" not in err


def test_unknown_unit_error_shows_suggestions(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run(capsys, ["-v", "1", "--from", "kilomter", "--to", "miles"])
    assert "'kilomter'" in err
    assert "kilometer" in err


def test_unsupported_unit_error_names_the_unit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run(capsys, ["-v", "1", "--from", "Gallons", "--to", "liter"])
    assert "'Gallons'" in err


def test_the_number_error_comes_before_the_unit_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run(capsys, ["-v", "abc", "--from", "blorp", "--to", "blorp"])
    assert "InvalidNumberError" in err
    assert "UnknownUnitError" not in err


# --- Usage errors ---


@pytest.mark.parametrize(
    "argv",
    [
        [],
        ["-v", "10"],
        ["-v", "10", "--from", "km"],
        ["-v", "10", "--from", "km", "--to", "miles", "extra"],
        ["--bogus"],
        ["-v", "10", "--from", "km", "--to", "miles", "--bogus"],
    ],
)
def test_wrong_usage_exits_with_code_2(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> None:
    code, out, err = run_expecting_exit(capsys, argv)
    assert code == 2
    assert out == ""
    assert "usage:" in err


def test_missing_arguments_are_explained(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, _, err = run_expecting_exit(capsys, ["-v", "10", "--from", "km"])
    assert "value, from_unit and to_unit" in err


def test_a_negative_number_with_an_exponent_needs_an_equality_sign(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # argparse reads "-1e3".
    code, out, _ = run_expecting_exit(
        capsys, ["-v", "-1e3", "--from", "m", "--to", "km"]
    )
    assert code == 2
    code, out, _ = run(capsys, ["-v=-1e3", "--from", "m", "--to", "km"])
    assert (code, out) == (0, "-1000 m = -1 km\n")


# --- Help and unit list ---


@pytest.mark.parametrize("option", ["-h", "--help"])
def test_help_explains_the_command(
    capsys: pytest.CaptureFixture[str], option: str
) -> None:
    code, out, err = run_expecting_exit(capsys, [option])
    assert code == 0
    assert err == ""
    assert "usage: python project.py" in out
    assert "-v 10 --from km --to miles" in out
    assert "--list" in out


@pytest.mark.parametrize("option", ["-l", "--list"])
def test_list_shows_every_category_and_unit(
    capsys: pytest.CaptureFixture[str], option: str
) -> None:
    code, out, err = run(capsys, [option])
    assert code == 0
    assert err == ""
    for category in ("Length:", "Mass:", "Volume:", "Time:", "Temperature:"):
        assert category in out
    for unit in ("kilometer", "nautical mile", "metric ton", "fahrenheit"):
        assert unit in out


def test_list_lines_are_not_too_long(capsys: pytest.CaptureFixture[str]) -> None:
    _, out, _ = run(capsys, ["--list"])
    assert all(len(line) <= 78 for line in out.splitlines())


def test_list_never_splits_a_unit_name_across_lines(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _, out, _ = run(capsys, ["--list"])
    for name in ("nautical mile", "metric ton", "cubic centimeter"):
        assert name in out


def test_list_cannot_be_combined_with_a_conversion(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code, out, err = run_expecting_exit(
        capsys, ["--list", "-v=10", "--from=km", "--to=miles"]
    )
    assert code == 2
    assert out == ""
    assert "-l or --list option must be used alone." in err
