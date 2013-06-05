## SatMapper by Carlos del Ojo and John Joseph Cole ##

SatMapper is a bioinformatics pipeline for population scale genotyping of microsatellite loci, from next generation sequencing datasets. The pipeline integrates a novel whole genome alignment software index with a naive implementation of regular expressions, to align, score and filter reads. A series of peak finding algorithms based on XXX provides accurate genotyping calls. An analysis toolkit provides means of retrieving population frequencies and absolute allele counts by locus. It further provides means for visualising reads, visualsing genotype calls and for estimating hardy weinberg frequencies, both by locus and by sample.

### SatMapper Description of Workflow ###

Satmapper requires few steps in order to genotype microsatellites 

* Generating template file: The template file is a TSV file (tab separated values) containing positions and coordinates of the microsatellites you are interested in. You can use software like [TRF](http://tandem.bu.edu/trf/trf.html), but you will need to convert tohe output to the format used in SatMapper (described below)
* Bait construction and indexing (baits allow mining of variable repeat lengths, whilst still benefitting from the speed of bowite.): Creation if bait chromosomes that will be used to fish the reads containig microsatellites.
* Alignment and Scoring of Fasq reads and database population.
* Genotyping: Command line user interface that allows to query the database and get information about the genotypes calculated for every microsatellite.
* Data visualization

### Requirements ###

[pysam](https://code.google.com/p/pysam/) - Python interface for the SAM/BAM sequence alignment and mapping format

[Bowtie](http://bowtie-bio.sourceforge.net/index.shtml) - An ultrafast memory-efficient short read aligner

### Usage ###

SatMapper is made of several modules:

#### msdescgen.py (MS description generator) ###

msdescgen.py: (MS description generator) Creates a TSV file containing the
description of every microsatellite

This module extracts microsatellites from FastA files. In order to find the MS,
a description of their exact location as well as their extension must be
provided in a TSV file called TEMPLATE.

You must provide a file with the description of the microsatellite (e.g:
mss_descr_example.txt) providing exact position and pattern length for each
microsatellite. Information about Microsatellites location can be obtained by
using the software Tandem Repeat Finder, however you will have to convert the
output to the format accepted by SatMapper.

The format of the TEMPLATE file is described below:

* Field 1: Chromosome number (must be an integer number)
* Field 2: Start position in the chromosome (position of the first nucleotide in the MS)
* Field 3: End position in the chromosome (position of the LAST nucleotide IN the MS)
* Field 4: Repeat pattern length
* Field 5: Chromosome ID in the FastA files (it must match the chromosome number always)

msdescgen.py reads a set of chromosomes (FastA files) and extracts the MS specified
in the TEMPLATE file generating a new file containing extra information from the
Micro Satellites. This information willbe enough to create the different baits
to be used in the alignment process.

The output file is a new TSV file (.msdesc) containing the following fields:

* Locus :            Auto generated name for the bait
* # chromosome:      Chromosome number
* Pattern:           Pattern detected
* Left flanking seq: Left flankind DNA sequence
* Right Flank Seq:   Right flankind DNA sequence
* MS:                MS found

All the records are a set of two lines. The first is a comment and the second
tab-separated values. The first line ( comment # ) wether the MS has been found
pure or not.
 
 
##### Example. Generating template and bait chromosomes. #####

TEMPLATE containing exact position for every MS:

    $ cat mss_descr_example.txt
    
    19	46273462	46273521	3	gi|224384750|gb|CM000681.1| Homo sapiens chromosome 19, GRC primary reference assembly
    1	248130347	248130366	2	gi|224384768|gb|CM000663.1| Homo sapiens chromosome 1, GRC primary reference assembly
    2	242866551	242866576	2	gi|224384767|gb|CM000664.1| Homo sapiens chromosome 2, GRC primary reference assembly
    22	40697176	40697199	3	gi|224384747|gb|CM000684.1| Homo sapiens chromosome 22, GRC primary reference assembly
    
Extracting MS to generatos a microsatellite description file:

    $ python msdescgen.py -t mss_descr_example.txt -l 15 /data/chrs/*.fa
    INFO: Reading chromosome gi|224384768|gb|CM000663.1| Homo sapiens chromosome 1, GRC primary reference assembly...
    INFO: Reading chromosome gi|224384750|gb|CM000681.1| Homo sapiens chromosome 19, GRC primary reference assembly...
    INFO: Reading chromosome gi|224384767|gb|CM000664.1| Homo sapiens chromosome 2, GRC primary reference assembly...
    INFO: Reading chromosome gi|224384747|gb|CM000684.1| Homo sapiens chromosome 22, GRC primary reference assembly...
    INFO:  *** [ mss-out.msdesc ] *** WRITTEN!
   
Content of the .msdesc file:

    $ cat mss-out.msdesc
    
    #[Locus]           [Pattern]  [Left flanking seq]  [Right  Flank  Seq]  [MS]
    # Ok!: ...CATGCAAACACACCACACAC | CACACACACACACACACACA | CGAGGTGCACACCCGGGGCC...
    1_CA_248130347.1   CA         AAACACACCACACAC      GAGGTGCACACCCGG      CACACACACACACACACACA
    # Ok!: ...GAAATGGTCTGTGATCCCCC | CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG | CATTCCCGGCTACAAGGACC...
    19_CAG_46273462.2  CAG        GGTCTGTGATCCCCC      TTCCCGGCTACAAGG      CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG
    # Ok!: ...GATGATTATCAAAATGAAAT | ACACACACACACACACACACACACAC | GCACACACCTCATGGAGCTC...
    2_AC_242866551     AC         TTATCAAAATGAAAT      GCACACACCTCATGG      ACACACACACACACACACACACACAC
    # Ok!: ...GCTCGAATGGTGAGTGCACT | GCAGCAGCAGCAGCAGCAGCAGCA | GAGGCAGCCAGGCATGAAGC...
    22_GCA_40697176.1  GCA        AATGGTGAGTGCACT      AGGCAGCCAGGCATG      GCAGCAGCAGCAGCAGCAGCAGCA
   
Generating the bait chromosomes, with MS lengths between 3 and 9bp:

    $ python baitsgen.py -i mss-out.msdesc -b 3 -t 9
    INFO:  *** [ out-baits.fa ] *** WRITTEN!
    
    $ cat out-baits.fa 
    
    >1_CA_248130347.1:2:2:4:15:19
    AAACACACCACACACCACAGAGGTGCACACCCGG
    >1_CA_248130347.1:3:2:6:15:21
    AAACACACCACACACCACACAGAGGTGCACACCCGG
    >1_CA_248130347.1:4:2:8:15:23
    AAACACACCACACACCACACACAGAGGTGCACACCCGG
    >19_CAG_46273462.2:1:3:3:15:18
    GGTCTGTGATCCCCCCAGTTCCCGGCTACAAGG
    >19_CAG_46273462.2:2:3:6:15:21
    GGTCTGTGATCCCCCCAGCAGTTCCCGGCTACAAGG
    >19_CAG_46273462.2:3:3:9:15:24
    GGTCTGTGATCCCCCCAGCAGCAGTTCCCGGCTACAAGG
    >22_GCA_40697176.1:1:3:3:15:18
    AATGGTGAGTGCACTGCAAGGCAGCCAGGCATG
    >22_GCA_40697176.1:2:3:6:15:21
    AATGGTGAGTGCACTGCAGCAAGGCAGCCAGGCATG
    >22_GCA_40697176.1:3:3:9:15:24
    AATGGTGAGTGCACTGCAGCAGCAAGGCAGCCAGGCATG
    >2_AC_242866551:2:2:4:15:19
    TTATCAAAATGAAATACACGCACACACCTCATGG
    >2_AC_242866551:3:2:6:15:21
    TTATCAAAATGAAATACACACGCACACACCTCATGG
    >2_AC_242866551:4:2:8:15:23
    TTATCAAAATGAAATACACACACGCACACACCTCATGG

Chromosome IDs have a special format which provides all the information about the MS:

###### 19_CAG_46273462.2:2:3:6:15:21 ######

* chromosome number: 19
* MS pattern: CAG
* chromosome position: 46273462
* Facrtion part: 2 (optional field, fractional part can be missing)
* copy number (repeats): 2
* pattern size (bp): 3
* MS length: 6 (2 * 3)
* MS start position in the bait: 15
* MS end position in the beit: 21

#### Resource fetcher (resourcefetcher.py) ####

This module reads a list of resources from a TSV file and dumps them to the standard output. Resources must be Fastq files (which can be compressed or uncompressed) and can be located either on internet (FTP or HTTP) or in your own filesystem.

The execution of this script requires a file containing a list with all the resources to be read. The format of the file is a two column dataset
tab separated values containing the individual name and the resource containing the files.

Format: 
  
* Field 1: Individual name (will indicate the table in the DB where alignments will be stored.
* Field 2: FastQ file resource. Can be HTTP, FTP of filesystem resource.

Read names for the FastQ entries will be modified temporarily to let dealer.py module know to which sample does the read belong.

An example of a resource TSV file is provided in the file [fastq_input_examp.txt](https://github.com/coelias/SatMapper/blob/master/fastq_input_examp.txt)

The Individual name will be used to create a table in the database with the same name. All the MS found in a resource will be inserted in its individual table

#### Alignment processor (dealer.py) ####

The resource fetcher dumps all the data to the aligner (bowtie) and the SAM output is redirected to the dealer.py module, which extracts all the information regarding the microsatellite
and populated the database. 
Database configuration can be set up in the file satmapper.cfg

Execution of this module requires as a parameter the description of the microsatellites produced by the chromosome extractor module (msdescgen.py) . (msdesc file)


### Example ### 

First we generate the .msdesc file, accordig to our selected 

We generate the MS description file (.msdesc)

    $ python msdescgen.py -t mss_descr_example.txt -l 15 /data/chrs/*.fa
    INFO: Reading chromosome gi|224384768|gb|CM000663.1| Homo sapiens chromosome 1, GRC primary reference assembly...
    INFO: Reading chromosome gi|224384750|gb|CM000681.1| Homo sapiens chromosome 19, GRC primary reference assembly...
    INFO: Reading chromosome gi|224384767|gb|CM000664.1| Homo sapiens chromosome 2, GRC primary reference assembly...
    INFO: Reading chromosome gi|224384747|gb|CM000684.1| Homo sapiens chromosome 22, GRC primary reference assembly...
    INFO:  *** [ mss-out.msdesc ] *** WRITTEN!
   
We check mss-out.msdesc to check wether there are mistakes or not in the MSS definition.
    
    ...
    # Ok!: ...GAAATGGTCTGTGATCCCCC | CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG | CATTCCCGGCTACAAGGACC...
    19_CAG_46273462.2  CAG        GGTCTGTGATCCCCC      TTCCCGGCTACAAGG      CAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAGCAG
    # Ok!: ...GATGATTATCAAAATGAAAT | ACACACACACACACACACACACACAC | GCACACACCTCATGGAGCTC...
    2_AC_242866551     AC         TTATCAAAATGAAAT      GCACACACCTCATGG      ACACACACACACACACACACACACAC
    # Ok!: ...GCTCGAATGGTGAGTGCACT | GCAGCAGCAGCAGCAGCAGCAGCA | GAGGCAGCCAGGCATGAAGC...
    22_GCA_40697176.1  GCA        AATGGTGAGTGCACT      AGGCAGCCAGGCATG      GCAGCAGCAGCAGCAGCAGCAGCA
	...
   
Generating the bait chromosomes, with MS lengths between 3 and 9bp:

    $ python baitsgen.py -i mss-out.msdesc -b 3 -t 9
    INFO:  *** [ out-baits.fa ] *** WRITTEN!

Generating bowtie index of the bait chromosomes

	$ bowtie-build out-baits.fa /tmp/myidx

Processing resources and storing data in the database.

    $ python resourcefetcher.py fastq_input_examp.txt | bowtie --best --sam /tmp/myidx - | python dealer.py mss-out.msdesc
	

	
