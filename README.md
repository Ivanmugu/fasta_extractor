# fasta_extractor

Extract fasta sequences contained in a single fasta file

## Function

To run this program you need a folder containing subfolders. Every
subfolder should have a fasta file, and the fasta file can have one or more
fasta sequences. For example, you can have a folder named results. In this
case, results will be the input folder and contain the SW0001 and SW0002
assembly.fasta results as follows:

```
~/Documents/results/
              SW0001_n2759_L1000-/
                          assembly.fasta
              SW0002_n2770_L1000-/
                          assembly.fasta
```

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

## Example of usage

In this example, we will use the hypothetical tree shown above as input folder.
We are not going to provide an output folder. To run the program you have to
type:

```bash
python3 fasta_extractor.py -n assembly.fasta -i ~/Documents/results
```

* The -n flag indicates the name of the fasta file.
* The -i flag indicates the path to the input folder 

When the program is done, a hypothetical result could be the following:

```
~/Documents/results/
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

In the next example, we will use the same input folder described before and
we will provide an output folder as follows:

```bash
python3 fasta_extractor.py -n assembly.fasta -i ~/Documents/results -o ~/Desktop/fasta_sequences
```

* The -o flag indicates the path to the output folder

When the program is done, a hypothetical result could be the following:

```
~/Desktop/fasta_sequences/
               SW0001_n2759_L1000_4000000_circular.fasta
               SW0001_n2759_L1000_100000_circular.fasta
               SW0001_n2759_L1000_5000_circular.fasta
               SW0002_n2770_L1000_3800000_linear.fasta
               SW0002_n2770_L1000_125000_circular.fasta
```

Notice that in this last example, the output folder contains only the extracted fasta
sequences.

