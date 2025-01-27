from keybert import KeyBERT
import Levenshtein
from functions import get_websites_by_similar_keyyowrds

def extract_keywords(query:str) -> list[str]:
    kw_model = KeyBERT()
    content_keywords = kw_model.extract_keywords(query, stop_words=None)
    content_keywords_list = [keyword for keyword, match in content_keywords]

    return content_keywords_list


def search(query:str) -> list[str]:
    keywords = extract_keywords(query)

    for query_keyword in keywords:
        websites = get_websites_by_similar_keyyowrds(query_keyword, treshold=0.4)
    
    # For each query keyword
        # Select similar keywords from the database
        # For each keyword from the db
            # Add float(similarity_score) points to the website
    # Sort the websites by points
    # Return sorted websites