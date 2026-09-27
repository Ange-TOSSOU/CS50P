import sys
from PIL import Image, ImageOps


def main():
    # Check the number of command line argument.
    arguments = sys.argv
    nb_cmd_args = len(arguments)
    if nb_cmd_args < 3:
        sys.exit("Too few command-line arguments")
    elif nb_cmd_args > 3:
        sys.exit("Too many command-line arguments")

    input_img_path = arguments[1]
    output_img_path = arguments[2]

    # Check the input_img has a valid extension.
    if not has_valid_extension(input_img_path):
        sys.exit("Invalid input")

    # Check the input_img and out_img have the same extension.
    if get_extension(input_img_path) != get_extension(output_img_path):
        sys.exit("Input and output have different extensions")

    # Open the shirt image.
    shirt_img = Image.open("shirt.png")

    # Open the person image and fit it with the shirt size.
    input_img = Image.open(input_img_path)
    input_img = ImageOps.fit(input_img, shirt_img.size)

    # Combine the two images.
    input_img.paste(shirt_img, (0, 0), shirt_img)

    # Save the final image.
    input_img.save(output_img_path)


def has_valid_extension(name):
    valid_extensions = [".jpg", ".jpeg", ".png"]

    # Check if name ends with a valid extension.
    name = name.strip().lower()
    for extension in valid_extensions:
        if name.endswith(extension):
            return True  # Valid extension.

    return False  # Not valid extension.


def get_extension(name):
    return name.split(".")[1]


if __name__ == "__main__":
    main()
