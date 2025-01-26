from keybert import KeyBERT
import Levenshtein

def extract_keywords(query:str) -> list[str]:
    kw_model = KeyBERT()
    content_keywords = kw_model.extract_keywords(query, stop_words=None)
    content_keywords_list = [keyword for keyword, match in content_keywords]

    return content_keywords_list


def search(query:str) -> list[str]:
    keywords = extract_keywords(query)
    
    # For each query keyword
        # Get query keyword features
        # Select keywords from the database with similar features
        # For each keyword from the db
            # Calculate the Levenshtein distance
            # If Levenshtein distance is small enough -> add 1 point to every website with given keyword
    # Sort the websites by points
    # Return sorted websites

    pass