from keybert import KeyBERT
import Levenshtein
from functions import get_websites_by_similar_keyyowrds

def extract_keywords(query:str) -> list[str]:
    kw_model = KeyBERT()
    content_keywords = kw_model.extract_keywords(query, stop_words=None)
    content_keywords_list = [keyword for keyword, match in content_keywords]

    return content_keywords_list


def search(query:str) -> list[str]:
    # Extract the keywords from the user query
    keywords = extract_keywords(query)

    graded_websites = dict()

    for query_keyword in keywords:
        websites = get_websites_by_similar_keyyowrds(query_keyword, treshold=0.4)

        for website in websites:
            # Add the similarity between the query keyword and website keyword to website score
            if website["url"] in graded_websites:
                graded_websites[website["url"]] += website["similarity"]
            else:
                graded_websites[website["url"]] = website["similarity"]

    # Sort the websites by score
    sorted_websites = sorted(graded_websites.items(), key=lambda item: item[1], reverse=True)

    return [url for url, score in sorted_websites]