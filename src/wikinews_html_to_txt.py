#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import htmlentitydefs
import re
import sys

from lxml import html as etree
from os import path

# NLTK function
def clean_html(html):
  """Removes HTML markup from the given string.

  :param html: the HTML string to be cleaned
  :type html: str
  :rtype: str
  """

  # First we remove inline JavaScript/CSS:
  cleaned = re.sub(r"(?is)<(script|style).*?>.*?(<!--\1-->)", "", html.strip())
  # Then we remove html comments. This has to be done before removing regular
  # tags since comments can contain '>' characters.
  cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
  # Next we can remove the remaining tags:
  cleaned = re.sub(r"(?s)<.*?>", "", cleaned)
  # Finally, we deal with whitespace
  cleaned = re.sub(r" ", " ", cleaned)
  cleaned = re.sub(r"  ", " ", cleaned)
  cleaned = re.sub(r"  ", " ", cleaned)
  return cleaned.strip()

def html_entity_to_char(match):
  """
  """

  name = match.string[match.start() + 1:match.end() - 1]
  char = ""

  try:
    char = unichr(htmlentitydefs.name2codepoint[name])
  except:
    try:
      if name.startswith("x"):
        char = unichr(int(name[1:], 16))
      if name.startswith("#"):
        char = unichr(int(name[1:], 10))
      else:
        char = unichr(int(name))
    except:
      pass

  return char

## MAIN ########################################################################

def main(argv):
  """
  """

  filepath = argv[1]
  output_dir = argv[2]
  #-----------------------------------------------------------------------------
  html_file = codecs.open(filepath, "r", "utf-8")
  html_string = html_file.read()
  html = etree.fromstring(html_string)
  output_filepath = path.join(output_dir, path.split(filepath)[1].replace(".html", ".txt"))
  output_file = codecs.open(output_filepath, "w", "utf-8")
  title = html.find("./head/title").text.rsplit("-", 1)[0]

  output_file.write("%s\n"%(title))
  for p in html.findall(".//*[@id='mw-content-text']/p")[1:]:
    inner = clean_html(etree.tostring(p))

    if inner != "":
      inner = re.sub(r"[&][^;]+;", html_entity_to_char, inner)
      output_file.write("%s\n"%(inner))

  html_file.close()
  output_file.close()

if __name__ == "__main__":
  main(sys.argv)

