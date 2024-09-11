import argparse
from disassemble import linnear_sweep


def main():
    # set up argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="binary file to disassemble", required=True
    )

    # parse args and get input filename
    args = vars(parser.parse_args())
    input_file = args["input"]

    # disassemble the file
    output = linnear_sweep(input_file)


if __name__ == "__main__":
    main()
