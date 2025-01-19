from keybert import KeyBERT

def levenshtein_distance(str1, str2, m, n):
    # str1 is empty
    if m == 0:
        return n
    
    # str2 is empty
    if n == 0:
        return m
    
    if str1[m - 1] == str2[n - 1]:
        return levenshtein_distance(str1, str2, m - 1, n - 1)
    
    return 1 + min(
        # Insert     
        levenshtein_distance(str1, str2, m, n - 1),
        min(
            # Remove
            levenshtein_distance(str1, str2, m - 1, n),
        # Replace
            levenshtein_distance(str1, str2, m - 1, n - 1))
    )

def extract_keywords(query:str) -> list[str]:
    kw_model = KeyBERT()
    content_keywords = kw_model.extract_keywords(query, stop_words=None)
    content_keywords_list = [keyword for keyword, match in content_keywords]

    return content_keywords_list


def search(query:str) -> list[str]:
    # Extract keywords from the query
    # For each query keyword
        # Get query keyword features
        # Select keywords from the database with similar features
        # For each keyword from the db
            # Calculate the Levenshtein distance
            # If Levenshtein distance is small enough -> add 1 point to every website with given keyword
    # Sort the websites by points
    # Return sorted websites

    pass