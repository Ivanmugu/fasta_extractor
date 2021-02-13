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
            To run this program you need a folder containing subfolders. Every
            subfolder should have a fasta file, and the fasta file can have one
            or more fasta sequences. For example, you can have a folder named
            results containing the SW0001 and SW0002 assembly.fasta results as
            follow:
            results/
                SW0001_n2759_L1000-/
                    assembly.fasta
                SW0002_n2770_L1000-/
                    assembly.fasta

            This script will search for assembly.fasta in the SW0001 subfolder
            and parse the fasta file. When a header is found, i.e. when a '>'
            symbol is found, the fasta sequence is transfer to a new file
            inside of the SW0001 folder. The new fasta file will be named
            according to the name of the directory that contains the fasta
            file. Header's information as length and topology will be included
            in the fasta file name. The script will repeat the process every
            time it finds a header, i. e. a '>' symbol. When the EOF is
            reached, the scripts continues with the next SW0002 subfolder.

            An example of possible results:
            results/
                SW0001_n2759_L1000-/
                    assembly.fasta
                    SW0001_n2759_L1000_4000000_circular
                    SW0001_n2759_L1000_100000_circular
                    SW0001_n2759_L1000_5000_circular
                SW0002_n2770_L1000-/
                    assembly.fasta
                    SW0002_n2770_L1000_3800000_linear
                    SW0002_n2770_L1000_125000_circular
                """))
    parser.add_argument('-i', '--input', help="name of input fasta file")
    parser.add_argument('-d', '--directory', help="path to input directory")
    args = parser.parse_args()
    # Checking if input folder exists
    if not os.path.exists(args.directory):
        print("error: directory does not exits\n")
        parser.print_help()
        sys.exit(1)
    # Checking if user provided mandatory arguments
    if (vars(args)).get("input") is None:
        print("error: you did not provide input file\n")
        parser.print_help()
        sys.exit(1)
    if (vars(args)).get("directory") is None:
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
    # Replacing dash at the end of folder name with underscore
    if folder_name[len(folder_name) - 1:] == '-':
        folder_name = folder_name[: -1]
        folder_name = folder_name + '_'
    elif folder_name[len(folder_name) - 1:] != '_':
        folder_name = folder_name + '_'
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


def get_file_and_dir_names(input_file, input_folder):
    """
    Iterates over subdirectories of a given directory (input_folder) looking
    for files with the same name (input_file). For the purpose of this script,
    input_file is "assembly.fasta". Returns the path to these file_names.
    Additionaly, returns the names af all the subfolders cantaining input_file.

    Parameters
    ----------
    input_folder : str
        Name of the directory to analyze.
    input_file : str
        Name of the file which path is needed

    Returns
    -------
    tuple
        Index 0 has a list of the addresses.
        Index 1 has a list of the directories' names.
    """
    # List of files' addresses
    file_addresses = []
    # List of directory's names
    dir_names = []
    # Get all files' and folders' names in the indicated directory
    files_and_folders = os.listdir(input_folder)
    # Iterate over all the files and folders contained in input_folder
    for filename in files_and_folders:
        # Check if the currect object is a folder or not
        if os.path.isdir(os.path.join(input_folder, filename)):
            # Checking if folder contains input_file
            if not os.path.exists(
                    os.path.join(input_folder, filename, input_file)):
                print("folder " + filename + " does not have " + input_file)
                continue
            # Getting folder's name
            dir_names.append(filename)
            # Getting path of input_file, i.e. assembly.fasta
            file_addresses.append(
                    os.path.join(input_folder, filename, input_file))
    return (file_addresses, dir_names)


def parse_folders(input_file, input_folder):
    """
    Explain function
    """
    # Get list of paths to the assembly.fasta files and list of folder's name
    input_information = get_file_and_dir_names(input_file, input_folder)
    # Get list of path to fasta files
    input_file_list = input_information[0]
    # Get list of folder names
    input_folder_list = input_information[1]
    # Number of fasta files to analyze
    number_files = len(input_file_list)
    # Loop over the list of paths to extract fasta sequences
    for i in range(number_files):
        fasta_extractor(input_file_list[i], input_folder_list[i])


def main():
    """
    Main function
    """
    # Checking usage
    args = user_input()
    # Getting input file
    input_file = args.input
    # Getting output directory
    input_folder = args.directory
    # extracting fasta sequences from fasta files
    parse_folders(input_file, input_folder)
    print("Done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
