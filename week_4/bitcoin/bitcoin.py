# pip install requests
import requests
import sys


def main():
    cmd_arguments = sys.argv

    # Check the user provide only one argument.
    nb_arguments = len(cmd_arguments)
    if nb_arguments == 1:
        sys.exit("Missing command-line argument")
    elif nb_arguments > 2:
        sys.exit("Too many command-line argument")

    # Check the argument is a number.
    try:
        n = float(cmd_arguments[1])
    except ValueError:
        sys.exit("Command-line argument is not a number")

    # Output the cost in dollar.
    total_price = n * get_bitcoin_price()
    print(f"${total_price:,.4f}")


def get_bitcoin_price():
    API_KEY = "12259cafc63d699605d0e226f0abf75f390f38bcd4837f9f282143f6a9f5ba8d"
    try:
        response = requests.get(
            f"https://rest.coincap.io/v3/assets/bitcoin?apiKey={API_KEY}"
        )
    except requests.RequestException:
        sys.exit("Something is wrong ?")

    content = response.json()

    return float(content["data"]["priceUsd"])


main()
