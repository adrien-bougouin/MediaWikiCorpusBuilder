#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import multiprocessing
import sys
import urllib2

from os import path

WIKINEWS_RANDOM_URL = "http://en.wikinews.org/wiki/Special:Random"

def download_page(url):
  """
  """

  html = urllib2.urlopen(url)

  return html.read()

## MAIN ########################################################################

def main(argv):
  """
  """

  nb_pages = 50000
  max_trials = 10
  output_dir = argv[1]
  #-----------------------------------------------------------------------------
  page_counter = 0
  nb_trials = 0

  while page_counter != nb_pages \
        or nb_trials == max_trials:
    nb_pages_to_download = nb_pages - page_counter
    download_pool = multiprocessing.Pool()
    #---------------------------------------------------------------------------
    print ">> Downloading %d page(s)!"%(nb_pages_to_download)
    #---------------------------------------------------------------------------
    pages = set(download_pool.map(download_page,
                                  [WIKINEWS_RANDOM_URL] * nb_pages_to_download))

    for html in pages:
      html_filepath = path.join(output_dir, "%d.html"%(page_counter))
      html_file = open(html_filepath, "w")

      html_file.write(html)
      html_file.close()

      page_counter += 1

    nb_trials += 1

if __name__ == "__main__":
  main(sys.argv)

