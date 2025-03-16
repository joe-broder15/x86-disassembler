import argparse
from disassemble import linear_sweep


# Program entry point
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="binary file to disassemble", required=True
    )
    args = vars(parser.parse_args())
    input_file = args["input"]

    # Disassemble the binary file
    try:
        output_list, labels = linear_sweep(input_file)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    # Display disassembly output
    for offset in sorted(output_list.keys()):
        # Print label if it exists at this offset
        if offset in labels:
            print(f"{labels[offset]}:")

        # Format and print instruction with its bytes
        instruction_bytes = "".join(f"{byte:02X}" for byte in output_list[offset][1])
        print(f"{offset:08X}: {instruction_bytes:24} {output_list[offset][0]}")


if __name__ == "__main__":
    main()
