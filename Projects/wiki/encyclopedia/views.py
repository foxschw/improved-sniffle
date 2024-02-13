from django.shortcuts import render
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