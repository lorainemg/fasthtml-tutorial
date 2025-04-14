from fasthtml.common import *

hdrs = (MarkdownJS(), HighlightJS(langs=['python', 'javascript', 'html', 'css']), )

app, rt = fast_app(hdrs=hdrs)

content = """
Here are some _markdown_ elements.

- This is a list item
- This is another list item
- And this is a third list item

**Fenced code blocks work here.**
"""

code_example = """
import datetime
import time

for i in range(10):
    print(f"{datetime.datetime.now()}")
    time.sleep(1)
""" 

@rt('/')
def get(req):
    return Titled("Markdown rendering example", Div(content,cls="marked"))

@rt('/home')
def get(req):
    return Titled("Markdown rendering example", Div(Pre(Code(code_example))))
serve()