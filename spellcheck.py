from bs4 import BeautifulSoup
import requests
import datetime
import urllib.request
import sys
import re
import string

# This class will check the spelling of visible words on a page
class SpellCheck():
    # Initialize the dictionary (should only be preformed once)
    def __init__(self):
        self.errors = set()
        self.hash = {}
        self.names = {}
        spellwords = open("words_en.txt").readlines()
        spellwords = spellwords + open("FirstNames.txt").readlines()
        spellwords = spellwords + open("LastNames.txt").readlines()
        spellwords = map(lambda x: x.strip(), spellwords)
        for word in spellwords : self.hash[word] = True

    # Read the html and parse for visible text
    def checktext(self, soup, url, SLACK):
        # This regex removes <script>, <head>, <style>, and comment tags from the html
        soup = re.sub(r'<script.*?>[\s\S]*?<\/script>|<head>[\s\S]*?<\/head>|<style.*?>[\s\S]*?<\/style>|<!--.*?-->|<nav.*?>[\s\S]*?<\/nav>', '', str(soup), 0, re.X)
        # This returns the regex string back into soup
        soup = BeautifulSoup(soup, "html.parser")
        # Get text from the soup
        text = soup.body.getText()
        # This regex removes words with digits in them i.e. the4cat
        text = re.sub(r'\w*\d\w*', '', str(text)).strip()
        # This regex removes all caps words (to get rid of acronyms) i.e. NASA
        text = re.sub(r'\b[A-Z]+\b', '', str(text)).strip()
        # This regex removes words that begin with capitol letters (In an effort to reduce false positives)
        text = re.sub(r'\b[A-Z][a-z]+\b', '', str(text)).strip()
        # This regex removes words with special characters. i.e. for%narnia
        text = re.sub(r'\w+[a-zA-Z0-9.+-][\d\.\/\@\*-][a-zA-Z.@/?=0-9]*\w+', '', str(text)).strip()
        # This regex also removes words with special characters
        text = re.sub(r'\w+[~`!-^@_*.%:;+=/,|#]+\w+([~`!#-^@_*.%:;+=/,|]?\w*)*', '', str(text)).strip()
        # This puts all remaining words that are at least 3 characters in length into a list 
        findwords = re.compile(r"\b[A-Za-z][A-Za-z][A-Za-z]+\b")
        words = findwords.findall(text)
        # send the list to spellcheck
        badwords = self.spellCheckHash(words)
        # return errors if they are found
        if badwords:
            if SLACK:
                return "Spelling Errors on page: <" + url + "|Link> :: " + str(badwords)
            #return str(badwords)
            return "Spelling Errors on page: " + url + " :: " + str(badwords)
        else:
            return False

    # this function compares each word in a list to a dictionary of words
    def spellCheckHash(self, words):
        # List comprehension to get words lowercase and into a list
        misspelled = [word for word in words if not word.lower() in self.hash]
        # Use a set (no need to list items more than once)
        seterrors = set()
        for error in misspelled:
            seterrors.add(error)
            
        return seterrors