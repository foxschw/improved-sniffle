from django.shortcuts import render, redirect
from django.http import HttpResponse
import markdown2
import os
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    # Create a dynamic variable for the file path
    file_path = os.path.join('entries', f'{title}.md')

    # Check to see if the file/path exists
    if os.path.exists(file_path):
        # if so, read content of .md file into a variable
        with open(file_path, 'r') as md_entry:
            entry_content = md_entry.read()

        # Use markdown2 to convert markdown to HTML
        html_entry = markdown2.markdown(entry_content)

        # Pass the HTML and title into the entry.html file
        return render(request, "encyclopedia/entry.html", {
            "entry_content": html_entry, 
            "title": title
        })

    # if not, return an error
    else:
        return render(request, "encyclopedia/error.html", {
            "error": "Page Not Found"
        }, status=404)
    
def search(request):

    # Retrieve the query from the search form
    query = request.GET.get('q', '')
    
    # Create a list of all possible entries
    entries = util.list_entries()
    
    # Iterate over the list and create a variable for the exact match
    exact_match = [entry for entry in entries if entry.lower() == query.lower()]
    
    # Find any partial matches
    partial_matches = [entry for entry in entries if query.lower() in entry.lower()]

    if exact_match:
        # Redirect straight to the 'entry' view. 
        # Index into 0th item because we used a list comprehension to find any exact matches
        return redirect('entry', title=exact_match[0])
    
    elif partial_matches:
        # Render the search page passing in the partial matches and intial search query
        return render(request, "encyclopedia/search.html", {
            "entries": partial_matches,
            "search_query": query
        })
    
    else:
        # Render the search page passing in the initial search query and an empty list
        # The logic for deal with populated or empty lists is handled in search.html
        return render(request, "encyclopedia/search.html", {
            "entries": [],
            "search_query": query
        })

