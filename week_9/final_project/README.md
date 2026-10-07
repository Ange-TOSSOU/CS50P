# Unit Converter

## Video Demo: [A Unit Converter in Python](https://youtu.be/s7c8xLWLdaw)

## Description
A Python tool that converts values between units of measurement. Use it from the command line.

```
$ python project.py -v 10 --from km --to miles
10 km = 6.2137 mi
```
**Note**: For Windows user, you should use `py` instead of `python` command.


## Quick start

```
python project.py -v 10 --from km --to miles
python project.py -v 100 --from celsius --to fahrenheit
python project.py -v 5 --from "nautical mile" --to km
python project.py --list
```

| Option | Meaning |
|---|---|
| `-v VALUE` | The number to convert |
| `--from UNIT` | The unit of that number |
| `--to UNIT` | The unit to convert to |
| `--list` (or `-l`) | List every supported unit, then exit |
| `--help` (or `-h`) | Show the help |

## Tutorial: using the command line

This walk-through takes about five minutes. Every example below was run, and the output shown is what you should see.

### 1. Your first conversion

Give a number with `-v`, the unit it is in with `--from`, and the unit you want with `--to`:

```
$ python project.py -v 10 --from km --to miles
10 km = 6.2137 mi
```

The answer reads `source = result`. Both sides show the unit's standard symbol (`km`, `mi`), whatever you typed.

### 2. Name units your way

Unit names ignore case and extra spaces, and accept symbols, plurals and British spellings. These all mean the same thing:

```
$ python project.py -v 10 --from km --to m
10 km = 10000 m

$ python project.py -v 10 --from Kilometres --to "  METRES "
10 km = 10000 m
```

| You can write | For |
|---|---|
| `km`, `kilometer`, `kilometers`, `kilometre`, `KILOMETRES` | kilometer |
| `ft`, `foot`, `feet` | foot |
| `lb`, `lbs`, `pound`, `pounds` | pound |
| `l`, `liter`, `litres` | liter |
| `sec`, `second`, `seconds`, `s` | second |

### 3. Temperatures

Temperatures work like any other unit. The supported ones are `celsius`, `fahrenheit` and `kelvin` (symbols `C`, `F`, `K`). Type the names in plain text, without the degree sign.

```
$ python project.py -v 100 --from celsius --to fahrenheit
100 C = 212 F

$ python project.py -v 98.6 --from fahrenheit --to celsius
98.6 F = 37 C

$ python project.py -v 0 --from kelvin --to celsius
0 K = -273.15 C
```

Only absolute temperatures are converted. A temperature *difference* ("a 10 degree rise") needs a different rule and is not supported.

### 4. Units with spaces

Put names that contain a space in quotes:

```
$ python project.py -v 5 --from "nautical mile" --to km
5 nmi = 9.26 km

$ python project.py -v 1 --from "cubic foot" --to liters
1 ft3 = 28.3168 l
```

### 5. Negative numbers

A negative number works as is:

```
$ python project.py -v -40 --from celsius --to fahrenheit
-40 C = -40 F

$ python project.py -v -2.5 --from m --to cm
-2.5 m = -250 cm
```

The one exception is a negative number written with an exponent such as `-1e3`. The command line would read it as an option, so join it to the option with `=`:

```
$ python project.py -v=-1e3 --from m --to km
-1000 m = -1 km
```

Positive numbers with an exponent need nothing special: `python project.py -v 1e3 --from m --to km`.

### 6. How results are displayed

Results show at least 4 decimal places and at least 4 significant digits, with trailing zeros removed. Very large and very small numbers switch to scientific notation:

```
$ python project.py -v 2.5 --from kg --to lb
2.5 kg = 5.5116 lb

$ python project.py -v 5 --from km --to mm
5 km = 5e6 mm

$ python project.py -v 1 --from mm --to km
1 mm = 1e-6 km
```

The rule: at or above one million, or below 0.0001, you get scientific notation (`5e6` means 5 × 10⁶, `1e-6` means 1 × 10⁻⁶).

### 7. What can I convert?

List every supported unit, grouped by category:

```
$ python project.py --list
length:
  millimeter (mm), centimeter (cm), meter (m), kilometer (km), inch (in), foot (ft),
  yard (yd), mile (mi), nautical mile
mass:
  ...
```

Units can only be converted within their own category: length to length, mass to mass, and so on.

### 8. When something goes wrong

Errors go to standard error, results to standard output. A message starts with the kind of problem:

```
$ python project.py -v abc --from km --to miles
InvalidNumberError: 'abc' is not a valid number.

$ python project.py -v 1 --from kilomter --to miles
UnknownUnitError: unknown unit 'kilomter'. Did you mean 'kilometer', ...?

$ python project.py -v 1 --from gallon --to liter
UnsupportedUnitError: 'gallon' is not supported: it has no single worldwide definition.

$ python project.py -v 1 --from kg --to meter
IncompatibleUnitsError: cannot convert from 'mass' to 'length'.
```

For a misspelled unit, the closest unit names are suggested. The suggestions are the closest matches, so they can include units unrelated to what you meant when nothing is close.

Some units are left out on purpose, because their size differs between countries or over time: gallon, pint, fluid ounce, cup, tablespoon, teaspoon, ton, month and year. The metric ton is supported (`tonne` or `metric ton`).


## Supported units

| Category | Units |
|---|---|
| Length | millimeter, centimeter, meter, kilometer, inch, foot, yard, mile, nautical mile |
| Mass | milligram, gram, kilogram, metric ton, ounce, pound, stone |
| Volume | milliliter, cubic centimeter, liter, cubic meter, cubic inch, cubic foot |
| Time | millisecond, second, minute, hour, day, week |
| Temperature | kelvin, Celsius, Fahrenheit |

## Features

- Five categories of units, defined from their official definitions (exact where a definition exists)
- Flexible unit names: case-insensitive, with symbols, plurals and British spellings
- Clear errors, with "did you mean" suggestions for misspelled units and an explicit message for unsupported ones
- Readable output: at least 4 decimals and 4 significant digits, with scientific notation for very large or small values
- A command-line interface
- Unit data that is validated when it loads, so a mistake in the data fails immediately
- Tests with a 100% coverage gate, strict type checking, linting and formatting


## Design choices

- **Plain-text units only.** Type `celsius`, not the degree sign. The symbols are plain `C`, `F` and `K`.
- **No regionally ambiguous units.** Gallons, pints, fluid ounces, cups, spoons and the bare "ton" are left out on purpose, because their size differs between countries (for example US versus UK gallons).
- **No months or years**, because their length varies. The ounce is the avoirdupois ounce.
- **Absolute temperatures only.**
