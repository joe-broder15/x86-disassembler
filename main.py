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
    try:
        output_list, labels = linnear_sweep(input_file)
    except Exception as e:
        print(e)
        exit()

    # print disassembly
    # get the offsets in sorted order
    offsets = sorted(list(output_list.keys()))
    # for each offset
    for off in offsets:
        # format the instruction bytes
        instruction_bytes = " ".join(f"{byte:02x}" for byte in output_list[off][1])
        # print all fields
        print(f"0x{off:08X}: {instruction_bytes:24} {str(output_list[off][0])}")


if __name__ == "__main__":
    main()
