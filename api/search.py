class Search:
    def __init__(self):
        pass

    def levenshtein_distance(self, str1, str2, m, n):
        # str1 is empty
        if m == 0:
            return n
        
        # str2 is empty
        if n == 0:
            return m
        
        if str1[m - 1] == str2[n - 1]:
            return self.levenshtein_distance(str1, str2, m - 1, n - 1)
        
        return 1 + min(
            # Insert     
            self.levenshtein_distance(str1, str2, m, n - 1),
            min(
                # Remove
                self.levenshtein_distance(str1, str2, m - 1, n),
            # Replace
                self.levenshtein_distance(str1, str2, m - 1, n - 1))
        )

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