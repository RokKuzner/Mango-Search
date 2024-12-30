from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.
def home(request):
    return render(request, "app/index.html")

def search(request):
    query = request.GET.get("q", None)

    if not query:
        return redirect("/")
    
    # Only for development
    results = [
        {"title": "Google Search", "url": "https://www.google.com/", "keywords": "search, google, google search"},
        {"title": "YouTube", "url": "https://www.youtube.com/", "keywords": "youtube, video, stream videos, search videos"},
        {"title": "Facebook", "url": "https://www.facebook.com/", "keywords": "social media, connect, facebook"},
        {"title": "Twitter", "url": "https://www.twitter.com/", "keywords": "social media, tweets, microblogging"},
        {"title": "Amazon", "url": "https://www.amazon.com/", "keywords": "shopping, ecommerce, online store"},
        {"title": "Wikipedia", "url": "https://www.wikipedia.org/", "keywords": "encyclopedia, information, wiki"},
        {"title": "Instagram", "url": "https://www.instagram.com/", "keywords": "social media, photos, instagram"},
        {"title": "LinkedIn", "url": "https://www.linkedin.com/", "keywords": "professional, jobs, networking"},
        {"title": "Reddit", "url": "https://www.reddit.com/", "keywords": "forum, discussions, community"},
        {"title": "Netflix", "url": "https://www.netflix.com/", "keywords": "movies, tv shows, streaming"},
        {"title": "GitHub", "url": "https://www.github.com/", "keywords": "code, repositories, collaboration"},
        {"title": "Stack Overflow", "url": "https://stackoverflow.com/", "keywords": "coding, programming, questions, answers"},
        {"title": "Bing", "url": "https://www.bing.com/", "keywords": "search engine, microsoft, bing search"},
        {"title": "Yahoo", "url": "https://www.yahoo.com/", "keywords": "news, email, search, yahoo"},
        {"title": "eBay", "url": "https://www.ebay.com/", "keywords": "auction, ecommerce, online store"},
        {"title": "Twitch", "url": "https://www.twitch.tv/", "keywords": "streaming, gaming, live videos"},
        {"title": "Pinterest", "url": "https://www.pinterest.com/", "keywords": "ideas, inspiration, pinterest"},
        {"title": "Dropbox", "url": "https://www.dropbox.com/", "keywords": "cloud storage, file sharing, backup"},
        {"title": "Spotify", "url": "https://www.spotify.com/", "keywords": "music, streaming, playlists"},
        {"title": "Coursera", "url": "https://www.coursera.org/", "keywords": "education, courses, online learning"},
        {"title": "Udemy", "url": "https://www.udemy.com/", "keywords": "online courses, learning, education"},
        {"title": "Quora", "url": "https://www.quora.com/", "keywords": "questions, answers, knowledge"},
        {"title": "Medium", "url": "https://medium.com/", "keywords": "blogs, articles, writing"},
        {"title": "Khan Academy", "url": "https://www.khanacademy.org/", "keywords": "education, learning, free resources"},
    ]


    return render(request, "app/search.html", {
        "query":query,
        "results":results,
    })