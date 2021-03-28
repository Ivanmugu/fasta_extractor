# fasta_extractor

Extract fasta sequences contained in a single fasta file.

This program extracts fasta sequences contained in two types of fasta files,
Unicycler or GenBank.

In order to run this scrip you need python3.

## Function

The program can process one or more fasta files. When only one fasta file
needs to be processed, the user should provide the path to the file. In the
case of multiple fasta files, the user should provide a path to a folder
containing subfolders with the fasta file that needs to be processed. For
example, the user can have a tree folder structure named results as shown
below. In this case, the path to the results folder is the input. As it can
be observed, the results folder contains two primary subfolders and every
primary subfolder contains the SW0001 and SW0002 assembly.fasta that would
be processed.

```
~/results/
    SW0001_n2759_L1000-/
        assembly.fasta
    SW0002_n2770_L1000-/
        assembly.fasta
```

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

## Examples of usage

### Example 1
Let's pretend the results folder shown above is the input. If we want to
get the extracted fasta files in the same folder as the provided
assembly.fasta, the user should type:

```bash
python3 fasta_extractor.py -i ~/results assembly.fasta
```

The input flag gets two arguments, the path to the results folder and the
name of the fasta files to be processed. An hypothetical result could be
the following:

```
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
```

It is important to note that the dash at the end of the folder's name is
replaced with underscore when naming the extracted fasta files (our lab
adds a dash at the end of the folder's name). If the folder's name doesn't
have a dash, the program will add an underscore anyway.

### Example 2

Let's use again the same results folder shown above as input. Now, if we
want the extracted fasta files in an specific folder named assemblies that
is in home the user should type:

```bash
python3 fasta_extractor.py -i ~/results assembly.fasta -o ~/assemblies
```

An hypothetical result could be the following:

```
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
```

### Example 3

In case the user has only one fasta file for processing, the user should
provide the path to that file as follows:

```bash
python3 fasta_extractor.py -i ~/results/SW0001_n2759_L1000-/assembly.fasta
```

An hypothetical result could be the following:

```
~/results/
    SW0001_n2759_L1000-/
        assembly.fasta
        SW0001_n2759_L1000_4000000_circular.fasta
        SW0001_n2759_L1000_100000_circular.fasta
        SW0001_n2759_L1000_5000_circular.fasta
```

### Example 4

If the user wants to extract multiple fasta sequences from a fasta file
named sequences.fasta created in GenBank, and the fasta file is in Desktop,
the user should type the following:

```bash
python3 fasta_extractor.py -i ~/Desktop/sequences.fasta -s genbank
```

To get the correcto output, the user must specify the style of the fasta
file. Therefore, the user must provide the -s flag with the genbank
argument. An hypothetical result could be the following:

```
~/Desktop/
    sequences.fasta
    CP049609.1.fasta
    CP049610.1.fasta
    CP49612.1.fasta
```
