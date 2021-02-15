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

            Usage example:
            python3 fasta_extractor -n assembly.fasta -d ~/Documents/results
                """))
    parser.add_argument('-n', '--name', help="name of input fasta file")
    parser.add_argument('-d', '--directory', help="path to input directory")
    args = parser.parse_args()
    if (args.name is None) and (args.directory is None):
        parser.exit(1, message=textwrap.dedent("""\
                error: missing arguments, you did not provide name of input
                fasta file nor path to input folder\n"""))
    # Checking if user provided mandatory arguments
    if (vars(args)).get("name") is None:
        parser.exit(1, message=textwrap.dedent("""\
                error: missing argument, you did not provide name of input
                fasta file\n"""))
    if (vars(args)).get("directory") is None:
        parser.exit(1, message=textwrap.dedent("""\
                error: missing argument, you did not provide path to input
                folder\n"""))
    # Checking if input folder exists
    if not os.path.exists(args.directory):
        parser.exit(1, message="error: directory does not exits\n")

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
            length = length.replace('\n', '')
        elif "circular" in info:
            info = info.split("=")
            topology = info[0]
            topology = topology.split('\n', '')
        else:
            continue
    if topology == "":
        topology = "linear"
    # Returning tupple with length and topology
    return (length, topology)


def fasta_extractor(input_file):
    """
    Parse an input fasta file to extract one or more fasta sequences into
    independent files. The new fasta files are outputed in the same directory
    where the input_file is located.

    Parameters
    ----------
    input_file : string
        Path to file to be opened for parsing
    """
    # Getting absolute path to input file
    path_infile = os.path.abspath(input_file)
    print("input file: " + path_infile)
    # Getting path to folder containing input file
    path_infolder = os.path.dirname(path_infile)
    # Getting path to output folder
    output_folder = path_infolder
    # Getting name of folder containing input file
    folder_name = os.path.basename(path_infolder)
    # Replacing dash at the end of folder name with underscore
    if folder_name[len(folder_name) - 1:] == '-':
        folder_name = folder_name[: -1]
        folder_name = folder_name + '_'
    elif folder_name[len(folder_name) - 1:] != '_':
        folder_name = folder_name + '_'
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
                print(header)
                # Making out file name and new fasta file header
                outfile_name = (
                        folder_name + header[0] + '_' +
                        header[1])
                outfile_header = '>' + outfile_name + '\n'
                # Opening out file
                outfile = open(output_folder + '/' + outfile_name + ".fasta",
                               'w')
                # Copying header into outfile
                outfile.write(outfile_header)
                # increase counter
                counter += 1
            elif line[0] == '>' and counter > 0:
                # Close previous outfile
                outfile.close()
                # Getting information of new header
                header = header_extractor(line)
                print(header)
                # Making out file name and new fasta file header
                outfile_name = (
                        folder_name + header[0] + '_' +
                        header[1])
                outfile_header = '>' + outfile_name + '\n'
                # Opening out file
                outfile = open(output_folder + '/' + outfile_name + ".fasta",
                               'w')
                # Copying header into outfile
                outfile.write(outfile_header)
                # increase counter
                counter += 1
            elif line[0] != '>' and counter > 0:
                # Concatenate line into outfile
                outfile.write(line)
        # Closing last outfile only if a file was created
        if counter > 0:
            outfile.close()


def get_file_paths(input_file, input_folder):
    """
    Iterates over subdirectories of a given directory (input_folder) looking
    for files with the same name (input_file). For the purpose of this script,
    input_file is "assembly.fasta". Returns the path to these file_names.
    Additionaly, returns the names af all the subfolders cantaining input_file.

    Parameters
    ----------
    input_file : str
        Name of the file which path is needed
    input_folder : str
        Path to the directory to analyze.

    Returns
    -------
    tuple
        Index 0, list of paths to input_file.
        Index 1, list of directories' names carring input_file.
    """
    # List of paths to input_file
    file_addresses = []
    # List of directories's names carrying input_file
    dir_names = []
    # Get all files' and folders' names in the indicated directory
    files_and_folders = os.listdir(input_folder)
    # Iterate over all the files and folders contained in input_folder
    for folder in files_and_folders:
        # Check if the currect object is a folder or not
        if os.path.isdir(os.path.join(input_folder, folder)):
            # Checking if folder contains input_file
            if not os.path.exists(
                    os.path.join(input_folder, folder, input_file)):
                print("folder " + folder + " does not have " + input_file)
                continue
            # Getting folder's name
            dir_names.append(folder)
            # Getting path of input_file, i.e. assembly.fasta
            file_addresses.append(
                    os.path.join(input_folder, folder, input_file))
    return (file_addresses, dir_names)


def screen_subfolders(input_file, input_folder):
    """
    Screens primary subfolders of input_folder to extract fasta sequences
    contained in a fasta file (input_file). For more information about the
    extraction of fasta sequences from a fasta file read the documentation of
    the fasta_extractor function.

    Parameters
    ----------
    input_file : str
        Name of fasta file to analyze.
    input_folder : str
        Path to input folder containing the primary subfolders to analyze
    """
    # Get list of paths to the assembly.fasta files and list of folder's name
    input_information = get_file_paths(input_file, input_folder)
    # Get list of path to fasta files
    input_file_list = input_information[0]
    # Number of fasta files to analyze
    number_files = len(input_file_list)
    # Loop over the list of paths to extract fasta sequences
    for i in range(number_files):
        fasta_extractor(input_file_list[i])


def main():
    """
    Main function
    """
    # Checking usage
    args = user_input()
    # Getting fasta file name
    file_name = args.name
    # Getting path to input directory
    input_folder = args.directory
    # Screen primary subfolders of input_folder to extract fasta sequences from
    # a fasta file (file_name).
    screen_subfolders(file_name, input_folder)
    # If everything went OK print Done
    print("Done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
