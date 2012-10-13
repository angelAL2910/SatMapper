Microsatellite description format:
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
