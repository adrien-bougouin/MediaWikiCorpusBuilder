#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import codecs
import htmlentitydefs
import multiprocessing
import os
import re
import sys
import urllib2

from lxml import html as etree
from os import path

# formating ####################################################################

def html_entity_to_char(match_object):
  """ Replaces HTML special characters (e.g. &amp;) by the appropriate symbol
  (e.g. '&amp;' -> '&').

  Args:
    match_object: A C{re.MatchObject} delimiting the character within a given
      string.

  Returns:
    The C{string} equivalent of the HTML character.
  """

  char_name = match_object.string[match_object.start() + 1:match_object.end() - 1]
  char = ""

  # text code
  if char_name in htmlentitydefs.name2codepoint:
    char = chr(htmlentitydefs.name2codepoint[char_name])
  else:
    try:
      # hexadecimal code
      if char_name.startswith("x"):
        char = unichr(int(char_name[1:], 16))
      # decimal code
      if char_name.startswith("#"):
        char = unichr(int(char_name[1:]))
      # decimal code
      else:
        char = unichr(int(char_name))
    except:
      pass

  return char

def clean_html(html_string):
  """ Removes HTML tags from an HTML string.

  This function slightly derives from the nltk.clean_html function.

  Args:
    html_string: The C{string} representation of the HTML content.

  Returns:
    A C{string} free of any HTML tag.
  """

  # remove inline JavaScript/CSS:
  cleaned_html = re.sub(r"(?is)<(script|style).*?>.*?(<!--\1-->)",
                        "",
                        html_string.strip())
  # remove comments
  cleaned_html = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned_html)
  # remove HTML tags (modified from NLTK version)
  cleaned_html = re.sub(r"(?s)<.*?>", "", cleaned_html)
  # remove extra whitespace
  cleaned_html = re.sub(r" ", " ", cleaned_html)
  cleaned_html = re.sub(r"  ", " ", cleaned_html)
  cleaned_html = re.sub(r"  ", " ", cleaned_html)

  # replace HTML special characters (modified from NLTK version)
  return re.sub(r"[&][^;]+;", html_entity_to_char, cleaned_html.strip())

def mediawiki_html_to_text(html_string):
  """ Extracts content information within a mediawiki HTML page.

  Args:
    html_string: The C{string} HTML of the wikimedia page.

  Returns:
    A C{tuple} containing the title and the content of the HTML page.
  """

  html = etree.fromstring(html_string)
  title = html.find("./head/title").text.replace("\n", "").replace("\r", "").rsplit("-", 1)[0]
  content = "\n".join(clean_html(etree.tostring(p).replace("\n", "").replace("\r", "").strip()) \
                      for p in html.findall(".//*[@id='mw-content-text']/p"))
  # FIXME
  # use this version to remove wikinews' date (for instance)
  #content = "\n".join(clean_html(etree.tostring(p).replace("\n", "").strip()) \
  #                    for p in html.findall(".//*[@id='mw-content-text']/p")[1:])

  return "%s\n%s"%(title, content)

# download #####################################################################

MEDIAWIKI_RANDOM_PAGE = "Special:Random"
ENCODING = "utf-8"

def download(url):
  """ Downloads a random page from a mediawiki website.

  Args:
    url: The C{string} url of a mediawiki website (e.g. http://en.wikinews.org).

  Returns:
    A C{string} representation of the downloaded HTML page.
  """

  output = urllib2.urlopen("%s/wiki/%s"%(url, MEDIAWIKI_RANDOM_PAGE))

  return output.read().decode(ENCODING)

if __name__ == "__main__":
  # retrieve arguments
  positional_arguments = ["<mediawiki_url>", "<document_number>", "output_dir"]
  arg_parser = argparse.ArgumentParser(usage="%s [options] %s %s %s"%(
                                               sys.argv[0],
                                               positional_arguments[0],
                                               positional_arguments[1],
                                               positional_arguments[2]
                                             ))

  arg_parser.add_argument("-i",
                          "--iteration-number",
                          dest="max_iter",
                          default="10",
                          help="number of maximum trials to download the documents (default=10)")
  arg_parser.set_defaults(must_strip=False)
  arg_parser.add_argument("mediawiki_url",
                          help="URL of the mediawiki (e.g. http://en.wikinews.org)")
  arg_parser.add_argument("document_number",
                          help="number of documents to download")
  arg_parser.add_argument("output_dir",
                          help="directory to save extracted HTMLs, TXTs and XMLs")

  if len(sys.argv) < 4:
    arg_parser.print_help()
  else:
    # accept positional arguments starting with '-'
    arguments = arg_parser.parse_args(args=sys.argv[1:-3] + ["--"] + sys.argv[-3:])
    #---------------------------------------------------------------------------
    url = arguments.mediawiki_url
    nb_pages = int(arguments.document_number)
    max_iter = int(arguments.max_iter)
    output_dir = arguments.output_dir
    output_html = path.join(output_dir, "html")
    output_txt = path.join(output_dir, "txt")
    output_xml = path.join(output_dir, "xml")

    # ensures output_dir is initialized
    if not path.exists(output_dir):
      os.makedirs(output_dir)
    if not path.exists(output_html):
      os.makedirs(output_html)
    if not path.exists(output_txt):
      os.makedirs(output_txt)
    if not path.exists(output_xml):
      os.makedirs(output_xml)

    # multi-threaded downloads
    page_counter = 0
    nb_iter = 0
    while page_counter != nb_pages and nb_iter < max_iter:
      nb_pages_to_download = nb_pages - page_counter
      download_pool = multiprocessing.Pool()
      #-------------------------------------------------------------------------
      print ">> Downloading %d page(s)!"%(nb_pages_to_download)
      #-------------------------------------------------------------------------
      pages = set(download_pool.map(download, [url] * nb_pages_to_download))

      #-------------------------------------------------------------------------
      print ">> %d unique page(s) succesfully downloaded!"%(len(pages))
      #-------------------------------------------------------------------------
      for html_string in pages:
        txt = mediawiki_html_to_text(html_string)
        lines = txt.splitlines()

        if len(lines) > 1:
          if lines[-1] == "":
            lines = lines[:-1]
          xml_string  = "<mediawikiDoc>\n"
          xml_string += "  <title>%s</title>\n"%(lines[0])
          xml_string += "  <content>\n"
          xml_string += "    <p>%s</p>\n"%("</p>\n    <p>".join(lines[1:]))
          xml_string += "  </content>\n"
          xml_string += "</mediawikiDoc>"
          #---------------------------------------------------------------------
          html_file = codecs.open(path.join(output_html,
                                  "%d.html"%(page_counter + 1)), "w", ENCODING)
          txt_file = codecs.open(path.join(output_txt,
                                 "%d.txt"%(page_counter + 1)), "w", ENCODING)
          xml_file = codecs.open(path.join(output_xml,
                                 "%d.xml"%(page_counter + 1)), "w", ENCODING)

          html_file.write(html_string)
          txt_file.write(txt)
          xml_file.write(xml_string)

          html_file.close()
          txt_file.close()
          xml_file.close()

          page_counter += 1

      nb_iter += 1

