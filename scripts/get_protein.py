#!/usr/bin/env python3

## get_protein_www.py -- 
## get a protein sequence from the Uniprot or NCBI/Refseq web sites using the accession
##

import sys
import re
import textwrap
import time
from urllib.request import Request, urlopen
from urllib.error import URLError

ncbi_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" 
uniprot_url = "https://www.uniprot.org/uniprot/"

sub_range = ''
for acc in sys.argv[1:]:

  if (re.search(r':',acc)):
    (acc, sub_range) = acc.split(':')

  if (re.match(r'^(sp|tr|iso|ref)\|',acc)):
      acc=acc.split('|')[1]

  if (re.match(r'[A-Z]P_\d+',acc)):   # get refseq
    db_type="protein"

    seq_args = "db=%s&id=" % (db_type) + ",".join(sys.argv[1:])  + "&rettype=fasta"

    url_string = ncbi_url + seq_args

  else:				# get uniprot
    acc_fields = acc.split('|')
    if (len(acc_fields)==1):
      url_string = uniprot_url + acc + ".fasta"
    else:
      url_string = uniprot_url + acc_fields[0] + ".fasta"


  req = Request(url_string)

  try: 
    resp = urlopen(req)
  except URLError as e:
    seq_html = ''
    if hasattr(e, 'reason'):
      sys.stderr.write("Sequence [%s] not found: %s\n"%(acc,str(e.reason)))
    elif hasattr(e, 'code'):
      sys.stderr.write("Sequence [%s] not found: %s\n"%(acc,str(e.ecode)))
    else:
      sys.stderr.write("Sequence [%s] not found\n"%(acc))
    exit(0)

  else:
    seq_html=resp.read().decode('utf-8')
    time.sleep(0.3)

  if (not sub_range):
    print(seq_html)
  else:
    (start, stop) = sub_range.split('-')

    (start, stop) = (int(start), int(stop))

    lines = seq_html.split('\n')

    header=lines[0]
    seq = ''.join(lines[1:])
    
    if (start > 0):
      start -= 1

    new_seq = seq[start:stop]
    ## print the header
    if (start > 0):
      print("%s @C:%d" %(header, start+1))
    else:
      print(header)

    print('\n'.join(textwrap.wrap(new_seq)))

