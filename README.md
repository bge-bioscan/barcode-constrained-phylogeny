![workflow](https://github.com/naturalis/barcode-constrained-phylogeny/actions/workflows/python-package-conda.yml/badge.svg)

# Barcode tree inference and analysis
This repository contains code and data for building very large, topologically-constrained barcode phylogenies through a divide-and-conquer strategy. Such trees are useful as reference materials in the comparable calculation of alpha and beta biodiversity metrics across metabarcoding assays. The input data for the approach we develop here comes from BOLD. The international database [BOLD Systems](https://www.boldsystems.org/index.php) contains DNA barcodes for hundred of thousands of species, with multiple barcodes per species. Theoretically, this data could be filtered and aligned per DNA marker to make phylogenetic trees. However, there are two limiting factors: building very large phylogenies is computationally intensive, and barcodes are not considered ideal for building big trees because they are short (providing insufficient signal to resolve large trees) and because they tend to saturate across large patristic distances.

Both problems can be mitigated by using the [Open Tree of Life](https://tree.opentreeoflife.org/opentree/argus/opentree13.4@ott93302) as a further source of phylogenetic signal. The BOLD data can be split into chunks that correspond to Open Tree of Life clades. These chunks can be made into alignments and subtrees. The OpenTOL can be used as a constraint in the algorithms to make these. The chunks are then combined in a large synthesis by grafting them on a backbone made from exemplar taxa from the subtrees. Here too, the OpenTOL is a source of phylogenetic constraint.

In this repository this concept is prototyped for both animal species and plant species.

## Currently added to the snakemake pipeline/repository
- Extract BOLD data
- Split data into FASTA files on family level
- Align FASTA files
- Make constraint trees for families 
- Make subtrees from families using FASTA alignments and constraint trees 

## Installation

The pipeline and its dependencies are managed using conda. On a linux or osx system, you can follow these steps to set up the `bactria` Conda environment using an `environment.yml` file and a `requirements.txt` file:

1. **Clone the Repository:**  
   Clone the repository containing the environment files to your local machine:
   ```bash
   git clone https://github.com/naturalis/barcode-constrained-phylogeny.git
   cd barcode-constrained-phylogeny
   ```
2. **Create the Conda Environment:**
   Create the bactria Conda environment using the environment.yml file with the following command:
   ```bash
   conda env create -f environment.yml
   ```
   This command will create a new Conda environment named bactria with the packages specified in the environment.yml file. This file also includes pip packages specified in the requirements.txt file, which will be installed after the Conda packages.
3. **Activate the Environment:**
   After creating the environment, activate it using the conda activate command:
   ```bash
   conda activate bactria
   ```
4. **Verify the Environment:**
   Verify that the bactria environment was set up correctly and that all packages were installed using the conda list command:
   ```bash
   conda list
   ```
   This command will list all packages installed in the active Conda environment. You should see all of the packages specified in the environment.yml file and the requirements.txt file.

## Configuration
Important before runnning the snakemake pipeline is to change in [src/config.yaml](src/config.yaml) the number of threads available on your computer. It is also important to change the marker to be researched in the config.yaml (default COI-5P). The file [BOLD tar.gz_file](https://www.boldsystems.org/index.php/datapackage?id=BOLD_Public.30-Dec-2022) must be downloaded manually and stored in the [data/](data/) directory.

## How to run
From the barcode-constrained-phylogny directory move to directory where the snakefile is located:
```bash 
cd src/
```
How to run raxml for all family alignments:
```bash 
snakemake -R all --snakefile snakefile_phylogeny -j {number of threads}
```
Snakemake rules can be performed separately:
```bash 
snakemake -R {Rule} --snakefile snakefile_phylogeny -j {number of threads}
```
Fill the same number at {number of threads} as you filled in previously in src/config.yaml.
In {Rule} insert the rule to be performed.

Here is an overview of all the rules in the snakefile_phylogeny:

![graphviz (1)](https://github.com/naturalis/barcode-constrained-phylogeny/assets/70514560/2b7eb955-f3bc-4126-a7b4-e361a88f4010)

## Repository layout

All data used and generated are located in the [data/](data/) directory. 
The snakefile, snakefile configuration file and python scripts are found in the [src/](src/) directory. 

## License

MIT License

Copyright (c) 2022 Naturalis Biodiversity Center

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
