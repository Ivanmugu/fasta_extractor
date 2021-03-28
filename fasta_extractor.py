#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File name:          fasta_extractor.py
Author:             Ivan Munoz-Gutierrez
Date created:       02/10/2021
Date last modified: 03/27/2021
Python version:     3.9
Description:        Extract fasta sequences contained in fasta files. For more
                    information refer to the epilog_msg in the user_input
                    function.

TODO: make an option to extract fasta sequences in a single folder. Make the
      program more general.
"""

import sys
import os
import argparse
import textwrap


def user_input():
    """
    Parse command line arguments provided by the user and check correct usage.

    Uses the module argparse to parse the command line arguments

    Parameters
    ----------
    --input, --output and --style
        Command line arguments provided by the user.

    Returns
    -------
    argparse object (.input, .output and .style)
        .input : list
            If one argument is provided, the list contains one element which
            is a path to a single fasta file requested for processing. If two
            arguments are provided, the list contains two elements. The first
            element is the path to an input directory that contains primary
            subfolders for analysis. The second element is the name of the
            fasta file that is contained in the primary subfolders and will be
            processed.
        .output : string
            Holds the path to the output directory.
        .style : string
            Header style of the fasta(s) file(s) to be analyzed.
    """
    epilog_msg  = ("""
    The program can process one or more fasta files. When only one fasta file
    needs to be processed, the user should provide the path to the file. In the
    case of multiple fasta files, the user should provide a path to a folder
    containing subfolders with the fasta file that needs to be processed. For
    example, the user can have a tree folder structure named results as shown
    below. In this case, the path to the results folder is the input. As it can
    be observed, the results folder contains two primary subfolders and every
    primary subfolder contains the SW0001 and SW0002 assembly.fasta that would
    be processed.

    ~/results/
        SW0001_n2759_L1000-/
            assembly.fasta
        SW0002_n2770_L1000-/
            assembly.fasta

    If the path to the results folder from the above example is provided as
    input, the program searches for assembly.fasta in the SW0001 subfolder and
    parse the fasta file. When a header is found, i.e. when a '>' symbol is
    found, the fasta sequence will be extracted as an independent file. The
    script will repeat the process every time it finds a header. When the EOF
    is reached, the script continues with the next SW0002 subfolder. If the
    user doesn't provide an output path, the new fasta files are saved in the
    same folder that contains the fasta file used for the extraction.

    This program parses two styles of fasta files, Unicycler and GeneBank. The
    Unicycler style is characterized by providing the length and topology of
    the molecule in the header, whereas GeneBank provides the accession number.
    By default, this programs assumes that the provided fasta files are
    Unicycler style. The user can specify the style by providing the
    corresponding flag.

    If the fasta file style is Unicycler, the new extracted fasta sequences are
    named according to the name of the directory that contains the fasta file.
    Additionally, header's information as length and topology are included in
    the fasta file name. In the case of GeneBank style, the new extracted fasta
    files are named according to the accession number present in the header.

    Examples of usage
    ----------------
    Example 1
    Let's pretend the results folder shown above is the input. If we want to
    get the extracted fasta files in the same folder as the provided
    assembly.fasta, the user should type:

    python3 fasta_extractor.py -i ~/results assembly.fasta

    The input flag gets two arguments, the path to the results folder and the
    name of the fasta files to be processed. An hypothetical result could be
    the following:

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

    Example 2
    Let's use again the same results folder shown above as input. Now, if we
    want the extracted fasta files in an specific folder named assemblies that
    is in home the user should type:

    python3 fasta_extractor.py -i ~/results assembly.fasta -o ~/assemblies

    An hypothetical result could be the following:

    ~/results/
        SW0001_n2759_L1000-/
            assembly.fasta
        SW0002_n2770_L1000-/
            assembly.fasta
    ~/assemblies/
        SW0001_n2759_L1000_4000000_circular.fasta
        SW0001_n2759_L1000_100000_circular.fasta
        SW0001_n2759_L1000_5000_circular.fasta
        SW0002_n2770_L1000_3800000_linear.fasta
        SW0002_n2770_L1000_125000_circular.fasta

    Example 3
    In case the user has only one fasta file for processing, the user should
    provide the path to that file as follows:

    python3 fasta_extractor.py -i ~/results/SW0001_n2759_L1000-/assembly.fasta

    An hypothetical result could be the following:

    ~/results/
        SW0001_n2759_L1000-/
            assembly.fasta
            SW0001_n2759_L1000_4000000_circular.fasta
            SW0001_n2759_L1000_100000_circular.fasta
            SW0001_n2759_L1000_5000_circular.fasta

    Example 4
    If the user wants to extract multiple fasta sequences from a fasta file
    named sequences.fasta created in GenBank, and the fasta file is in Desktop,
    the user should type the following:

    python3 fasta_extractor.py -i ~/Desktop/sequences.fasta -s genbank

    To get the correcto output, the user must specify the style of the fasta
    file. Therefore, the user must provide the -s flag with the genbank
    argument. An hypothetical result could be the following:

    ~/Desktop/
        sequences.fasta
        CP049609.1.fasta
        CP049610.1.fasta
        CP049611.1.fasta
    """)
    # Creating a parser object for parsing arguments and providing help.
    parser = argparse.ArgumentParser(
        prog='python3 fasta_extractor.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Extracts fasta sequences contained in a fasta file"),
        epilog=textwrap.dedent(epilog_msg))
    # Creating required argument group.
    mandatory_argument = parser.add_argument_group("required arguments")
    # Making required argument.
    mandatory_argument.add_argument(
        '-i', '--input', required=True, nargs='+',
        help=(
            """
            One or two arguments are required. If the user provides one
            argument, the program will process one fasta file. Therefore, the
            argument must be a path to the fasta file that needs to be
            processed. If the user provides two arguments, the program will
            process fasta files within primary subfolders. The fasta files to
            be processed must have the same name. Therefore, in this option,
            the first argument must give the path to the folder that contains
            the primary subfolders to be analyzed, and the second argument is
            the name of the fasta file contained in the primary subfolders that
            the program will process.""")
    )
    # Making optional arguments.
    parser.add_argument('-o', '--output', help="Path to output directory.")
    parser.add_argument(
        '-s', '--style',
        help=(
            """
            Header style of the submitted fasta file (Unicycler or GenBank). If
            style is Unicycler, type unicycler or u. If the style is GenBank
            type genbank or g.""")
    )
    # Saving parsed arguments.
    args = parser.parse_args()
    # Checking if user provided mandatory arguments.
    if len(args.input) == 1 and (not os.path.exists(args.input[0])):
        parser.exit(1, message=textwrap.dedent("""\
                Error: path to fasta file doesn't exist\n"""))
    if len(args.input) == 1 and (os.path.isdir(args.input[0])):
        parser.exit(1, message=textwrap.dedent("""\
                Error: the path provided is a directory not a fasta file\n"""))
    if len(args.input) == 2 and (not os.path.exists(args.input[0])):
        parser.exit(1, message=textwrap.dedent("""\
                Error: path to input folder file doesn't exist\n"""))
    if len(args.input) > 2:
        parser.exit(1, message=textwrap.dedent("""\
                Error: too many arguments\n"""))
    # If output folder is provided, check if it exists.
    if (args.output is not None) and (not os.path.exists(args.output)):
        parser.exit(1, message="Error: output directory does not exits\n")
    # If header style is provided check correct input.
    if args.style is not None:
        fasta_style = args.style.lower()
        if not (fasta_style == "unicycler" or fasta_style == "u" 
        or fasta_style == "genbank" or fasta_style == "g"):
            parser.exit(1, message="Error: wrong submitted style\n")
        # Standardizing name of header style
        else:
            if fasta_style == "unicycler" or fasta_style == "u":
                args.style = "unicycler"
            if fasta_style == "genbank" or fasta_style == "g":
                args.style = "genbank"

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

def header_extractor(header, style):
    """
    Parse a header of a fasta sequence to extract information.

    If the style is unicycler, length and topology are extrated. If the style
    is genbank, accession number is extracted.

    Parameters
    ----------
    header : string
        Header of fasta sequence.
    style : string
        style of fasta file, it could be Unycler or GenBank style.

    Returns
    -------
    header_info : string
        If header style is unicycler, returns length and topology separated by
        underscore. For example, 5000000_circular.
        If header style is genbank, returns the accession number present in the
        header. For example, CP029244.1.
    """
    # Spliting header into list.
    header = header.split(" ")
    if style == "unicycler" or style == None:
        # Information needed.
        length = ""
        topology = ""
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
        header_info = length + '_' + topology
    elif style == "genbank":
        # Getting the accession number
        header_info = header[0][1:]
    else:
        sys.exit("Error: wrong fasta header style.")

    return header_info


def fasta_extractor(input_file, header_style, output_folder):
    """
    Parse a fasta file to extract its fasta sequences.

    The extracted fasta sequences are saved into independent files and are
    named depending of the header style provided. If header style is unicycler,
    new files are named according to the name of the directory that contains
    the input_file. Additionally, the length and topology of the extracted
    fasta sequences are included in their name. If the header style is genbank,
    new files are named according to the accession number provided in the
    header of each fasta sequence.

    If the user doesn't specify the output_folder, the new fasta files are
    outputed in the same directory where the input_file is located.

    For example, if we have a hypothetical fasta file that contains three fasta
    sequences in the following path: ~/My_assembly/assembly.fasta. If header
    style is unicycler and if we don't specify the output_folder, a
    hypothetical output could be:

    ~/My_assembly/
            assembly.fasta
            My_assembly_4000000_circular.fasta
            My_assembly_100000_circular.fasta
            My_assembly_80000_circular.fasta

    Parameters
    ----------
    input_file : string
        Path to file to be opened for parsing.
    header_style : string
        Style of header that can be unicycler or genbank.
    output_folder : string
        Path to save the the new fasta files.
    """
    # Getting absolute path to input file.
    path_infile = os.path.abspath(input_file)
    # Getting path to folder containing input file.
    path_infolder = os.path.dirname(path_infile)
    # Getting name of folder containing input file.
    folder_name = os.path.basename(path_infolder)
    # If folder_name has a dash at its end, replace it with underscore (in our
    # lab we add a dash at the end of folder name).
    if folder_name[len(folder_name) - 1:] == '-':
        folder_name = folder_name[: -1]
        folder_name = folder_name + '_'
    # If folder_name has underscore at its end, ignore.
    elif folder_name[len(folder_name) - 1:] == '_':
        pass
    # Otherwise add underscore at its end.
    else:
        folder_name = folder_name + '_'

    # Getting path to output folder.
    if output_folder is None:
        path_output = path_infolder
    else:
        path_output = output_folder

    # Opening input file.
    with open(input_file, "r") as infile:
        # Counter of fasta sequence.
        counter = 0
        # Iterating over infile.
        for line in infile:
            # If line is the first header open a new fasta file for writing.
            if line[0] == '>' and counter == 0:
                # Gettting information from header.
                header = header_extractor(line, header_style)
                # Making file name and new fasta file header.
                if header_style == "unicycler" or header_style is None:
                    outfile_name = (folder_name + header)
                    outfile_header = '>' + outfile_name + '\n'
                if header_style == "genbank":
                    outfile_name = header
                    outfile_header = line
                # Opening out file.
                outfile = open(
                    path_output + '/' + outfile_name + ".fasta", 'w')
                # Copying header into outfile.
                outfile.write(outfile_header)
                # Increasing counter.
                counter += 1
            # If line isn't the first header, close the previous fasta file and
            # open a new one for writing.
            if line[0] == '>' and counter > 0:
                # Closing previous outfile.
                outfile.close()
                # Getting information of new header.
                header = header_extractor(line, header_style)
                # Making file name and new fasta file header.
                if header_style == "unicycler" or header_style is None:
                    outfile_name = (folder_name + header)
                    outfile_header = '>' + outfile_name + '\n'
                if header_style == "genbank":
                    outfile_name = header
                    outfile_header = line
                # Opening out file.
                outfile = open(
                    path_output + '/' + outfile_name + ".fasta", 'w')
                # Copying header into outfile.
                outfile.write(outfile_header)
                # Increase counter.
                counter += 1
            # If line is not header concatene line into the opened fasta file.
            # To make sure that line is comming from a fasta sequence, counter
            # must be greaater than 0.
            if line[0] != '>' and counter > 0:
                outfile.write(line)
        # Closing the last fasta file only if a file was created, i.e. if the 
        # counter is greater than 0.
        if counter > 0:
            outfile.close()


def main():
    """Extract fasta sequences from fasta files."""
    # Getting user input.
    args = user_input()
    # Getting input information list.
    input_info = args.input
    # Getting path to output directory.
    output_folder = args.output
    # Getting the header style of fasta file
    header_style = args.style

    # If user provided one argument in input, process the provided fasta file.
    if len(input_info) == 1:
        fasta_extractor(input_info[0], header_style, output_folder)
    # Otherwise, process the fasta files in the primary subdirectories.
    else:
        # Getting a list of paths to the primary subdirectories that contains 
        # the requested fasta file.
        input_path_list = get_file_paths(input_info[1], input_info[0])
        # Looping over the list of paths to extract fasta sequences.
        for _, path in enumerate(input_path_list):
            fasta_extractor(path, header_style, output_folder)

    print("fasta_extractor is done!")
    sys.exit(0)


if __name__ == "__main__":
    main()
