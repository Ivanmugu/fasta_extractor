#!/opt/anaconda3/bin/python3
"""
Created on Wed 10, 2021
@author: ivanmugu
"""
import sys
import os
import argparse
import textwrap


def user_input():
    """
    Gets input from user to run the program, parse the arguments and check
    correct usage.

    Returns
    -------
    argparse object
        Contains all the needed information of the arguments provided by the
        user, i.e. the path to the input and output directories.
    """
    # Parsing aguments and providing help
    parser = argparse.ArgumentParser(
        prog='fasta_extractor.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Extracts fasta sequences contained in a single fasta file"),
        epilog=textwrap.dedent("""
            This script loops overs the input fasta file. When a header is
            found, i.e. when a '>' symbol is found, the fasta sequence is
            transfer to a new file. The new fasta file will be named according
            to the name of the directory that contains the fasta file. Header's
            information as length and topology will be included in the fasta
            file name. The script will repeat the process every time it finds a
            header, i. e. a '>' symbol."""))
    parser.add_argument('-i', '--input', help="input fasta file")
    parser.add_argument('-o', '--output', help="path to output directory")
    args = parser.parse_args()
    # Making sure user provides input and output directory
    # Checking if output and input folder exist
    if (vars(args)).get("input") is None:
        print("error: you did not provide input file\n")
        parser.print_help()
        sys.exit(1)
    if (vars(args)).get("output") is None:
        print("error: you did not provide output folder\n")
        parser.print_help()
        sys.exit(1)

    return args


def header_extractor(line):
    """
    Parse a fasta sequence header and extracts lenght and topology.

    Parameters
    ----------
    line : string
        header of fasta sequence

    Returns
    -------
    tuple
        tuple containing lenght and topology (circular or linear)
    """
    # Information needed
    length = ""
    topology = ""
    # split line into list
    line = line.split(" ")
    # Looping over line to get info
    for info in line:
        if "length" in info:
            info = info.split("=")
            length = info[1]
        elif "circular" in info:
            info = info.split("=")
            topology = info[0]
        else:
            continue
    if topology == "":
        topology = "linear"
    # Returning tupple with length and topology
    return (length, topology)


def fasta_extractor(input_file, output_folder):
    """
    Parse an input fasta file to extract one or more fasta sequences into
    independent files.

    Parameters
    ----------
    input_file : string
        File to be opened for parsing

    output_folder : string
        Path to folder where the resulting fasta files are going to be output
    """
    # Getting path to input file
    path_infile = os.path.abspath(input_file)
    # Getting path to folder containing input file
    path_infolder = os.path.dirname(path_infile)
    # Getting name of folder containing input file
    folder_name = os.path.basename(path_infolder)
    # Getting absolute path to output folder
    output_folder = os.path.abspath(output_folder)
    # Opening input file
    with open(input_file, "r") as infile:
        # counter of fasta sequence
        counter = 0
        # Iterating over infile
        for line in infile:
            # Checking if line is header
            if line[0] == '>' and counter == 0:
                # Get information from header
                header = header_extractor(line)
                # Making out file name and new fasta file header
                outfile_name = (
                        folder_name + header[0] + '_' +
                        header[1] + ".fasta")
                outfile_header = '>' + outfile_name + '\n'
                # Opening out file
                outfile = open(output_folder + '/' + outfile_name, 'w')
                # Copying header into outfile
                outfile.write(outfile_header)
                # increase counter
                counter += 1
            elif line[0] == '>' and counter > 0:
                # Close previous outfile
                outfile.close()
                # Getting information of new header
                header = header_extractor(line)
                # Making out file name and new fasta file header
                outfile_name = (
                        folder_name + header[0] + '_' +
                        header[1] + ".fasta")
                outfile_header = '>' + outfile_name + '\n'
                # Opening out file
                outfile = open(output_folder + '/' + outfile_name, 'w')
                # Copying header into outfile
                outfile.write(outfile_header)
                # increase counter
                counter += 1
            else:
                # Concatenate line into outfile
                outfile.write(line)
        # Closing last outfile
        outfile.close()


def main():
    """
    Main function
    """
    # Checking usage
    args = user_input()
    # Getting input file
    input_file = args.input
    # Getting output directory
    output_folder = args.output
    # Extracting fasta sequences from fasta file
    fasta_extractor(input_file, output_folder)
    # If everything went OK print a messege
    print("Done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
