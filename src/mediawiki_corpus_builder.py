#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import htmlentitydefs
import multiprocessing
import re
import sys
import urllib2

from lxml import html as etree
from os import path

# formating ####################################################################

# TODO explain its a modification from nltk.clean_html
def html_cleaning(html_string):
  """
  """

  # remove inline JavaScript/CSS:
  cleaned_html = re.sub(r"(?is)<(script|style).*?>.*?(<!--\1-->)", "", html_string.strip())
  # remove comments
  cleaned_html = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned_html)
  # remove html tags (modified from NLTK version)
  cleaned_html = re.sub(r"(?s)<.*?>", "", cleaned_html)
  # remove extra whitespace
  cleaned_html = re.sub(r" ", " ", cleaned_html)
  cleaned_html = re.sub(r"  ", " ", cleaned_html)
  cleaned_html = re.sub(r"  ", " ", cleaned_html)

  return cleaned_html.strip()

def html_entity_to_char(match_object):
  """
  """

  char_name = match.string[match.start() + 1:match.end() - 1]
  char = ""

  if char_name in htmlentitydefs.char_name2codepoint:
    char = unichr(htmlentitydefs.char_name2codepoint[char_name])
  else:
    try:
      if char_name.startswith("x"):
        char = unichr(int(char_name[1:], 16))
      if char_name.startswith("#"):
        char = unichr(int(char_name[1:], 10))
      else:
        char = unichr(int(char_name))
    except:
      pass

  return char

def mediawiki_html_to_txt(html_string):
  """
  """

  pass

# download #####################################################################

def download(url):
  """
  """

  output = urllib2.urlopen(url)

  return output.read() 

if __name__ == "__main__":
  # TODO get-opt
  #      - nb_documents
  #      - max_iter
  #      - output_dir
  #      - mediawiki_url (ex.: http://en.wikinews.org)
  #      - max_iter

