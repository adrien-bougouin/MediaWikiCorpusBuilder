MediaWikiCorpusBuilder
======================

## Features

- Builds MediaWiki-based corpora (of a given size) using random page retrieval (e.g. http://en.wikinews.org/wiki/Special:Random)
- Outputs HTML, XML and TXT file

## Usage

    src/mediawiki_corpus_builder.py [options] <mediawiki_url> <document_number> output_dir
    
    positional arguments:
      mediawiki_url         URL of the mediawiki (e.g. http://en.wikinews.org)
      document_number       number of documents to download
      output_dir            directory to save extracted HTMLs, TXTs and XMLs
      
    optional arguments:
      -h, --help            show this help message and exit
      -i MAX_ITER, --iteration-number MAX_ITER
                            number of maximum trials to download the documents
                            (default=10)
