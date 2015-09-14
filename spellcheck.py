import enchant
'''
This function checks the spelling for every word on the given page
@params
    -Page HTML
    -current URL
@returns
    -List of misspelled words
'''
def spellCheck(words, url):
    badWords = []
    english = enchant.Dict('en_US')
    first = True
    checkWords = re.findall(r"[\w]+", words)
    for word in checkWords:
        #print(word)
        if (len(str(word)) > 2 and not any(char.isdigit() for char in word)):
            try:
                word = str(word)
                print(word)
                if(first and not english.check(word)):
                    badWords.append('\nSpelling Error on: '+url)
                    badWords.append(word)
                elif(not english.check(word)):
                    badWords.append(word)
            except Exception as e:
                print(str(e))
    return badWords

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element)):
        return False
    return True
