import time
import urllib

import requests
from bs4 import BeautifulSoup


#TODO FIX TAB SPACING IN VIM YOU FUCK
#TODO FIX VIMRC TO INCLUDE SYNTAX ON

#TODO find a way to exclude the link loops and no links articles to not skew data.


def find_first_link(url):
    # takes a string for a wikipedia url and returns the first link in the body of the article.
    response = requests.get(url)
    html_doc = response.text
    soup = BeautifulSoup(html_doc, 'html.parser')

    # searching the tree of the html using the soup object to find the first paragraph in body of article.
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")

    article_link = None
    
    # find first p tag in content_div, find first a tag within that, this is your first link.
    for element in content_div.find_all("p", recursive=False):
        if element.find("a", recursive=False):
            article_link = element.find("a", recursive=False).get('href')
            break
    
    # if no a tag was found
    if not article_link:
        return

    # joining the link found in html to create a proper wikipedia URL
    first_link = urllib.parse.urljoin('https://en.wikipedia.org/', article_link)

    return first_link

def continue_crawl(search_history, target_url, max_steps=99999999999999999999):
    # conditionals controlling the crawling behavior
    if search_history[-1] == target_url:
        print(search_history[-1])
        print("We've found the target article!")
        steps = len(search_history) - 1
        print("took: %s steps" % steps)
        return False
    elif len(search_history) > max_steps:
        print("The search has gone on suspiciously long, aborting search!")
        return False
    elif search_history[-1] in search_history[:-1]:
        print("We've arrived at an article we've already seen, aborting search!")
        # this keeps track of articles with no links, put in index 1 because index 0 is the RANDOM link
        # and will be removed in the loop, use LINK_LOOP to parse out this data later to prevent outliers.
        search_history[1] = "LINK_LOOP"
        return False
    else:
        return True

def get_article_chain():
    # function returns the completed chain of URLs, from first page to target inside of a list.
    start_url = "https://en.wikipedia.org/wiki/Special:Random"
    #start_url = "https://en.wikipedia.org/wiki/Classroom"
    target_url = "https://en.wikipedia.org/wiki/Philosophy"
    article_chain = [start_url]

    while continue_crawl(article_chain, target_url):
        # sleep the program to avoid spamming servers
        time.sleep(2)
        print(article_chain[-1])
        
        # if the article contains no link then break.
        first_link = find_first_link(article_chain[-1])
        if not first_link:
            print("We've arrived at an article with no links, aborting search!")
            # if article has no links, replace index 1 with tag so we can parse out later on.
            article_chain[1] = "NO_LINK"
            break
        else:
            #TODO make sure this makes the articles that do not have links are not recorded in the article chain
            article_chain.append(first_link)
    
    # removes the 'RANDOM' url from the start of the crawler.
    del article_chain[0]
    #print(article_chain)
    return article_chain
     
def crawler(num_of_searches): # executes the get_article_chain function, x number of times.
    # chains[] is a list of lists, containing article chains.
    chains = [] 
    x = 0
    while x < num_of_searches:
        chains.append(get_article_chain())
        x += 1

    return chains

def print_article_chain(article_chain): # prints articles in an easily readable format
    
    for article in article_chain:
        for link in article:
            print(link)
        print("***************************************")

def print_article_dict(article_dict): # prints the article_dict in an easily readable format
    for k,v in article_dict.items():
        print("{} : {}".format(k,v))

def count_article_steps(article_chain): # count each article chain and assign it to a dictionary
    article_dict = {}
    for article in article_chain:
        print("Debug: getting length of {}...".format(article))
        article_dict[article[0]] = len(article) 

    return article_dict

def calculate_step_mean(article_dict): # takes a dictionary of articles and calculates the mean of the values
				       # (steps taken from start to finish
    value_sum = 0
    article_dict_length = len(article_dict)
    
    for value in article_dict.values():
        value_sum += value
    
    mean = value_sum / article_dict_length

    return mean

def calculate_step_median(article_dict):
    steps_list = [] # list containing all of the step values from the article_dict
    for value in article_dict.values():
        steps_list.append(value)

    steps_list.sort()
    print("Sorted list of steps\n{}\n".format(steps_list))
    middle = len(steps_list) // 2
    print("MIDDLE OF LIST =  {}".format(middle))
    if len(steps_list) % 2 != 0:
        return steps_list[middle] 
    else:
        return (steps_list[middle] + steps_list[middle - 1]) / 2

def main():
    article_chain = crawler(50)
    article_dict = count_article_steps(article_chain)

    print("****RESULTS****")
    print_article_dict(article_dict)
    print("MEAN: {}".format(calculate_step_mean(article_dict)))
    print("MEDIAN: {}".format(calculate_step_median(article_dict)))
    print("****END RESULTS****")

if __name__ == "__main__":
    main()
