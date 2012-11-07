SatMapper by Carlos del Ojo and John Jospeh Cole
================================================

SatMapper is a bioinformatics pipeline for population scale genotyping of microsatellite loci, from next generation sequencing datasets. The pipeline integrates a novel whole genome alignment software index with a naive implementation of regular expressions, to align, score and filter reads. A series of peak finding algorithms based on XXX provides accurate genotyping calls. An analysis toolkit provides means of retrieving population frequencies and absolute allele counts by locus. It further provides means for visualising reads, visualsing genotype calls and for estimating hardy weinberg frequencies, both by locus and by sample.

SatMapper Description of Workflow
=================================

SatMapper 

1) Data Collection Phase

a) Parsing of miscrosatellite loci file

b) Bait construction and indexing

- baits allow mining of variable repeat lengths, whilst still benefitting from the speed of bowite.

c) Alignment and Scoring of Fasq reads and database population


Requirements
============

pysam - Python interface for the SAM/BAM sequence alignment and mapping format


Usage
=====

SatMapper is made of several modules:

Chromosome extractor (chrextract.py): 
	This module extracts microsatellites from FastA files generating multiple chromosomes
	per microsatellite and generating its multiple alleles.
	
	You must provide a file with the description of the microsatellite (e.g: mss_descr_example.txt) providing
	exact position and pattern length for each microsatellite. Below you can see a description of the required fields.
	Information about Microsatellites location can be obtained by using the software Tandem Repeat Finder, however
	you will have to convert the output to the format accepted by SatMapper.

	Once you have your MS descrption file written you must execute chrextract.py:

	chrextract.py -o outfile <MS_definition.txt> <fasta1.fa> <fasta2.fa> ... <fastaN.fa>

	outfile --> Specify the name of the FastA file which will contain all the chromosomes
				Moreover, a second file will be created (same name with an msdesc extension)
				containing sequence information of the microsatellites, which will be used
				by the next modules.

	MS_definition.txt --> File containing the definition of the microsatellites you want to extract
	                      from a reference genome (see format below)

	fasta1.fa ... fastaN.fa --> Reference genome provided, you can specify as many files as you want
								They can be compressed in gzip or bz2.

		Example: 

	* Microsatellite description format:
	  ---------------------------------
	
	  Tab separated fields: 
	  
	  Field 1: Chromosome number (must be an integer number)
	  Field 2: Start position in the chromosome (position of the first nucleotide in the MS)
	  Field 3: End position in the chromosome (position of the LAST nucleotide IN the MS)
	  Field 4: Flanking sites length for each bait chromosome
	  Field 5: Repeat pattern length
	  Field 6: Minimum number of repeats to be generated for this specific locus
	  Field 7: Maximum number of repeats to be generated for this specific locus
	  Field 8: Chromosome ID in the FastA files (it must match the chromosome number always)
	  
	  Example:
	  4	3076603	3076659	10	3	1	20	4 dna:chromosome chromosome:GRCh37:4:1:191154276:1
	  19	46273462	46273521	300	3	1	20	19 dna:chromosome chromosome:GRCh37:19:1:59128983:1
	  1	248130347	248130366	10	2	1	20	1 dna:chromosome chromosome:GRCh37:1:1:249250621:1
	  2	242866551	242866576	300	2	1	20	2 dna:chromosome chromosome:GRCh37:2:1:243199373:1
	  22	40697176	40697199	300	3	1	20	22 dna:chromosome chromosome:GRCh37:22:1:51304566:1
	  
	  
	  Output:
	  ...CACCACACAC | CACACACACACACACACACA | CGAGGTGCAC...
	  ...GATGATTATCAAAATGAAAT | ACACACACACACACACACACACACAC | GCACACACCTCATGGAGCTC...
	  ...GCTCGAATGGTGAGTGCACT | GCAGCAGCAGCAGCAGCAGCAGCA | GAGGCAGCCAGGCATGAAGC...
	  ...CAAGTCCTTC | CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG | CAACAGCCGC...
	  ...GAAATGGTCTGTGATCCCCC | CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG | CATTCCCGGCTACAAGGACC...


	Example:

	> python chrextract.py -o mss.fa mss_descr_example.txt /Volumes/PROJECT/human_genome/*.gz
	...
	INFO: Reading chromosome 18 dna:chromosome chromosome:GRCh37:18:1:78077248:1...
	INFO: Reading chromosome 19 dna:chromosome chromosome:GRCh37:19:1:59128983:1...
	DEBUG: Chr 19, Pos 46273462 : ...GAAATGGTCTGTGATCCCCC | CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG | CATTCCCGGCTACAAGGACC...
	INFO: Reading chromosome 2 dna:chromosome chromosome:GRCh37:2:1:243199373:1...
	DEBUG: Chr 2, Pos 242866551 : ...GATGATTATCAAAATGAAAT | ACACACACACACACACACACACACAC | GCACACACCTCATGGAGCTC...
	INFO: Reading chromosome 20 dna:chromosome chromosome:GRCh37:20:1:63025520:1...
	...

	It will show the extracted microsatellites as it finds them, so you can see whether they are well defined or not.

Resource fetcher (resourcefetcher.py):

	This module reads fastq files which can be compressed or uncompressed and located either on internet (FTP or HTTP) or in your filesystem.

	The execution of this script requires a file containing a list with all the resources to be read. The format of the file is a two column dataset
	tab separated containing the individual name and the resource containing the files.

	Tab separated fields: 
	  
	Field 1: Individual name (will indicate the table in the DB where alignments will be stored.
	Field 2: FastQ file resource. Can be HTTP, FTP of filesystem resource.

	An example is provided in the file fastq_input_examp.txt

Alignment processor (dealer.py)

	This modules accepts SAM data as standard input and populates the database with microsatellite aligning information. 
	Database configuration can be set up in the file satmapper.cfg

	Execution of this module requires as a parameter the description of the microsatellites produced by the chromosome extractor module. (msdesc file)


EXAMPLE
=======

# Chromosome extractor tool
python chrextract.py -o /tmp/myref.fa mss_descr_example.txt ../human_genome/h.sapiens-GRCh37.bz2

# Index creation for bowtie (any other aligner can be used)
bowtie-build /tmp/myref.fa /tmp/myidx

# Resource collector reading FastQ files, sending to bowtie and storing the information into the DB
python resourcefetcher.py fastq_input_examp.txt | bowtie --best --sam /tmp/myidx - | python dealer.py /tmp/myref.fa.msdesc
	

	
