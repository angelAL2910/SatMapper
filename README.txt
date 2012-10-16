SatMapper by Carlos del Ojo and John Cole
=========================================

SatMapper is a bioinformatics tool developed to genotype microsatellites found in DNA short reads.

Requirements
============

pysam - Python interface for the SAM/BAM sequence alignment and mapping format


Usage
=====

SatMapper is made of several modules:

Chromosome extractor: 
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

