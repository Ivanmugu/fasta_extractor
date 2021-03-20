#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File name:          fasta_extractor.py
Author:             Ivan Munoz-Gutierrez
Date created:       02/10/2021
Date last modified: 03/17/2021
Python version:     3.9
Description:        Extract fasta sequences contained in fasta files. For more
                    information refer to the epilog_msg in the user_input
                    function.

TODO: make an option to extract fasta sequences in a single folder.
"""

import sys
import os
import argparse
import textwrap


def user_input():
    """
    Parse command line arguments provided by the user and check correct usage.

    For example, if the user provides the following input:

    python3 fasta_extractor.py -n assembly.fasta -i ~/Documents/results

    The -n flag indicates that assembly.fasta is the name of the input file and
    the -i flag indicates that ~/Documents/results is the path to the directory
    that contains the input file. These information is saved and returned.

    Returns
    -------
    argparse object (.name, .input and .output)
        .name : holds the name of the input fasta file.
        .input : holds the path to the input directory.
        .output : holds the path to the output directory.
    """
    epilog_msg  = ("""
    To run this program you need a folder containing subfolders. Every
    subfolder should have a fasta file, and the fasta file can have one or more
    fasta sequences. For example, you can have a folder named results. In this
    case, results will be the input folder and contain the SW0001 and SW0002
    assembly.fasta results as follows:

    ~/results/
        SW0001_n2759_L1000-/
            assembly.fasta
        SW0002_n2770_L1000-/
            assembly.fasta

    This script will search for assembly.fasta in the SW0001 subfolder and
    parse the fasta file. When a header is found, i.e. when a '>' symbol is
    found, the fasta sequence will be extracted as an independent file. The new
    fasta file will be named according to the name of the directory that
    contains the fasta file. Header's information as length and topology will
    be included in the fasta file name. The script will repeat the process
    every time it finds a header. If the EOF is reached, the script will
    continues with the next SW0002 subfolder. If the user doesn't provide an
    output path, the new fasta files will be saved in the same folder that
    contains the fasta file used for the extraction.

    Example of usage
    ----------------
    python3 fasta_extractor.py -n assembly.fasta -i ~/results

    If we use the directory tree mentioned above as an example of input
    folder, an hypothetical result, if the user doesn't provide an output path,
    could be the following:

    ~/results/
        SW0001_n2759_L1000-/
            assembly.fasta
            SW0001_n2759_L1000_4000000_circular.fasta
            SW0001_n2759_L1000_100000_circular.fasta
            SW0001_n2759_L1000_5000_circular.fasta
        SW0002_n2770_L1000-/
            assembly.fasta
            SW0002_n2770_L1000_3800000_linear.fasta
            SW0002_n2770_L1000_125000_circular.fasta

    It is important to note that the dash at the end of the folder's name is
    replaced with underscore when naming the extracted fasta files (our lab
    adds a dash at the end of the folder's name). If the folder's name doesn't
    have a dash, the program will add an underscore anyway.
    """)

    # Parsing aguments and providing help.
    parser = argparse.ArgumentParser(
        prog='fasta_extractor.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Extracts fasta sequences contained in a fasta file"),
        epilog=textwrap.dedent(epilog_msg))
    parser.add_argument('-n', '--name', help="name of input fasta file")
    parser.add_argument('-i', '--input', help="path to input directory")
    parser.add_argument('-o', '--output', help="path to output directory")
    args = parser.parse_args()
    # Checking if user provided mandatory arguments.
    if (args.name is None) and (args.input is None):
        parser.exit(1, message=textwrap.dedent("""\
                error: missing arguments, you did not provide name of input
                fasta file nor path to input folder\n"""))
    if (vars(args)).get("name") is None:
        parser.exit(1, message=textwrap.dedent("""\
                error: missing argument, you did not provide name of input
                fasta file\n"""))
    if (vars(args)).get("input") is None:
        parser.exit(1, message=textwrap.dedent("""\
                error: missing argument, you did not provide path to input
                folder\n"""))
    # Checking if input folder exists.
    if not os.path.exists(args.input):
        parser.exit(1, message="error: input directory does not exits\n")
    # Checking if output folder exists.
    if (not (args.output is None)) and (not os.path.exists(args.output)):
        parser.exit(1, message="error: output directory does not exits\n")

    return args


def get_file_paths(file_name, input_folder):
    """
    Get the paths of files with the same name that are contained in primary
    subdirectories.

    Iterate over subdirectories of a given directory (input_folder) looking
    for files with the same name (file_name). Return the paths to these files.

    This function was designed to get the path of the assembly.fasta files
    generated by Unicycler.

    Parameters
    ----------
    file_name : str
        Name of the file which path is needed, usually assembly.fasta.
    input_folder : str
        Path to the directory to analyze.

    Returns
    -------
    file_addresses : list
        List of paths to file_name.

    For example, if you have the hypothetical tree:

    ~/assemblies/
            SW0001/
                assembly.fasta
            SW0002/
                assembly.fasta

    You will get the following:
    ["~/assemblies/SW0001/assembly.fasta",
     "~/assemblies/SW0002/assembly.fasta"]
    """
    # List to save the paths to file_name.
    file_addresses = []
    # Getting all files' and folders' names in the indicated directory.
    files_and_folders = os.listdir(input_folder)
    # Iterating over all the files and folders contained in input_folder.
    for folder in files_and_folders:
        # Checking if the current object is a folder or not.
        if os.path.isdir(os.path.join(input_folder, folder)):
            # If folder contains file_name, get path and append it to
            # file_addresses. Otherwise, print an error message and continue.
            if not os.path.exists(
                    os.path.join(input_folder, folder, file_name)):
                print("folder " + folder + " does not have " + file_name)
                continue
            file_addresses.append(
                    os.path.join(input_folder, folder, file_name))

    return file_addresses


def header_extractor(header):
    """
    Parse a header of a fasta sequence to look for length and topology.

    This function was designed to parse headers of assembly.fasta files
    returned by Unycicler.

    Parameters
    ----------
    header : string
        Header of fasta sequence.

    Returns
    -------
    tuple (length, topology)
        length : int
        topology : string
    """
    # Information needed.
    length = ""
    topology = ""
    # Spliting header into list.
    header = header.split(" ")
    # Looping over header to get info.
    for info in header:
        if "length" in info:
            info = info.split("=")
            length = info[1]
            length = length.replace('\n', '')
        elif "circular" in info:
            info = info.split("=")
            topology = info[0]
            topology = topology.replace('\n', '')
        else:
            continue
    if topology == "":
        topology = "linear"

    # Returning tupple with length and topology.
    return (length, topology)


def fasta_extractor(input_file, output_folder=None):
    """
    Parse a fasta file to extract its fasta sequences.

    The extracted fasta sequences are saved into independent files and are
    named according to the name of the directory that contains the input_file.
    Additionally, the length and topology of the extracted fasta sequences are
    included in their name. If the user doesn't specify the output_folder, the
    new fasta files are outputed in the same directory where the input_file is
    located.

    For example, if we have a hypothetical fasta file that contains three fasta
    sequences in the following path: ~/My_assembly/assembly.fasta. If we don't
    specify the output_folder, a hypothetical output could be:

    ~/My_assembly/
            assembly.fasta
            My_assembly_4000000_circular.fasta
            My_assembly_100000_circular.fasta
            My_assembly_80000_circular.fasta

    Parameters
    ----------
    input_file : string
        Path to file to be opened for parsing.
    output_folder : string
        Path to save the the new fasta files.
    """
    # Getting absolute path to input file.
    path_infile = os.path.abspath(input_file)
    # Getting path to folder containing input file.
    path_infolder = os.path.dirname(path_infile)
    # Getting path to output folder.
    if output_folder is None:
        path_output = path_infolder
    else:
        path_output = output_folder
    # Getting name of folder containing input file.
    folder_name = os.path.basename(path_infolder)
    # Replacing dash at the end of folder name with underscore (in our lab we
    # add a dash at the end of folder name).
    if folder_name[len(folder_name) - 1:] == '-':
        folder_name = folder_name[: -1]
        folder_name = folder_name + '_'
    else:
        folder_name = folder_name + '_'
    # Opening input file.
    with open(input_file, "r") as infile:
        # Counter of fasta sequence.
        counter = 0
        # Iterating over infile.
        for line in infile:
            # Checking if line is header.
            if line[0] == '>' and counter == 0:
                # Gettting information from header.
                header = header_extractor(line)
                # Making out file name and new fasta file header.
                outfile_name = (
                        folder_name + header[0] + '_' + header[1])
                outfile_header = '>' + outfile_name + '\n'
                # Opening out file.
                outfile = open(
                    path_output + '/' + outfile_name + ".fasta", 'w')
                # Copying header into outfile.
                outfile.write(outfile_header)
                # Increasing counter.
                counter += 1
            elif line[0] == '>' and counter > 0:
                # Closing previous outfile.
                outfile.close()
                # Getting information of new header.
                header = header_extractor(line)
                # Making out file name and new fasta file header.
                outfile_name = (
                        folder_name + header[0] + '_' + header[1])
                outfile_header = '>' + outfile_name + '\n'
                # Opening out file.
                outfile = open(
                    path_output + '/' + outfile_name + ".fasta", 'w')
                # Copying header into outfile.
                outfile.write(outfile_header)
                # Increase counter.
                counter += 1
            elif line[0] != '>' and counter > 0:
                # Concatenate line into outfile.
                outfile.write(line)
        # Closing last outfile only if a file was created.
        if counter > 0:
            outfile.close()


def main():
    """Extract fasta sequences from fasta files."""
    # Getting user input.
    args = user_input()
    # Getting fasta file name.
    file_name = args.name
    # Getting path to input directory.
    input_folder = args.input
    # Getting path to output directory.
    output_folder = args.output
    # Getting a list of paths to the primary subdirectories that contain the
    # requested fasta file.
    input_path_list = get_file_paths(file_name, input_folder)
    # Looping over the list of paths to extract fasta sequences.
    for _, path in enumerate(input_path_list):
        fasta_extractor(path, output_folder)
    print("fasta_extractor is done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
