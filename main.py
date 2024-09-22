import argparse
from disassemble import linnear_sweep


# main function and entry point into program
def main():

    # set up argparse and parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="binary file to disassemble", required=True
    )
    args = vars(parser.parse_args())

    # get the input filename
    input_file = args["input"]

    # try to disassemble the program and print any errors that occur
    try:
        output_list, labels = linnear_sweep(input_file)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    # Print disassembly, start by getting the offsets in sorted order
    for offset in sorted(output_list.keys()):

        # check if a label exists at this offset and print it first
        if offset in labels:
            print(f"{labels[offset]}:")

        # format the raw instruction bytes
        instruction_bytes = "".join(f"{byte:02X}" for byte in output_list[offset][1])

        # print the offset, instruction bytes, and finally the instruction
        print(f"0x{offset:08X}: {instruction_bytes:20} {output_list[offset][0]}")


if __name__ == "__main__":
    main()
