from django.shortcuts import render, redirect
from django.http import HttpResponse
import markdown2
import os
import random
from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    # Create a dynamic variable for the file path
    file_path = os.path.join("entries", f"{title}.md")

    # Check to see if the file/path exists
    if os.path.exists(file_path):
        # if so, read content of .md file into a variable
        with open(file_path, "r") as md_entry:
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
    query = request.GET.get("q", "")
    
    # Create a list of all possible entries
    entries = util.list_entries()
    
    # Iterate over the list and create a variable for the exact match
    exact_match = [entry for entry in entries if entry.lower() == query.lower()]
    
    # Find any partial matches
    partial_matches = [entry for entry in entries if query.lower() in entry.lower()]

    if exact_match:
        # Redirect straight to the 'entry' view.
        # Index into 0th item because we used a list comprehension to find any exact matches
        return redirect("entry", title=exact_match[0])
    
    elif partial_matches:
        # Render the search page passing in the partial matches and intial search query
        return render(request, "encyclopedia/search.html", {
            "entries": partial_matches,
            "search_query": query
        })
    
    else:
        # Render the search page passing in the initial search query and an empty list
        # The logic for dealing with populated or empty lists is handled in search.html
        return render(request, "encyclopedia/search.html", {
            "entries": [],
            "search_query": query
        })


def new(request):
    
    # If the form was submitted:
    if request.method == "POST":

        # Retrieve title from form submission
        new_title = request.POST.get("new_entry_title", "")

        # Server-side check if title is included
        if not new_title:
            return render(request, "encyclopedia/error.html", {
                "error": "Entries Must Include A Title."
            }, status=400)
        
        # Check for "/" in title entry which would create unwanted subdirectories
        if "/" in new_title:
            return render(request, "encyclopedia/error.html", {
                "error": "Titles May Not Include A Forward Slash."
            }, status=400)

        # Initiate check to see if an article with the same title already exists.
        # Create a list of all existing titles
        titles = util.list_entries()
    
        # Iterate over the list and create a variable for the exact match
        exact_match = [title for title in titles if title.lower() == new_title.lower()]
        
        # If a match exists, render an error page
        if exact_match:
            return render(request, "encyclopedia/error.html", {
                "error": "This Page Already Exists."
                }, status=409)
        
        else:
            # If the title is unique, fetch the text content
            new_text = request.POST.get("new_entry_text", "")

            # Server-side check if text is included
            if not new_text:
                return render(request, "encyclopedia/error.html", {
                    "error": "Entries Must Include Text."
                }, status=400)

            # Concatenate the title with the text to conform to pre-existing entries
            full_entry = "# " + new_title + "\n\n" + new_text

            # Save the entry and redirect to that page.
            util.save_entry(new_title, full_entry)
            return redirect("entry", title=new_title)
        
    # If page was accessed from sidebar or direct URL entry, display the form
    else:
        return render(request, "encyclopedia/new.html")


def edit(request, title):
    
    # If page is reached through hyperlink
    if request.method == "GET":
    
        # Store contents of entry in a variable
        entry_content = util.get_entry(title)

        # Render the edit page passing in the title and text
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "editable_text": entry_content
        })
    
    else:
        # If edit is submitted, store the new text in a variable
        new_text = request.POST.get("edited_text", "")

        # Server-side check if text is included
        if not new_text:
            return render(request, "encyclopedia/error.html", {
                "error": "Entries Must Include Text."
            }, status=400)
        
        # Save new text to the entry and render the entry's page
        else:
            util.save_entry(title, new_text)
            return redirect("entry", title=title)


def random_page(request):
        
    # Redirect to "entry" view using random.choice to chose an article from the list.
    return redirect("entry", title=random.choice(util.list_entries()))
