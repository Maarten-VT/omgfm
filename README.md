omgfm
=====

omgfm is build on top of [cmark-gfm][cmark_link]. Aim is to make cmark-gfm's rendering options avaialble from python while maintining most of the speed benefit the shared C library provides. 

Features:
---------
- [CommonMark][cmarkorg] with GFM extensions. (see the [spec][spec] with GFM additions)
- Simple interface for converting CommonMark formated text to any of the suported formats. (HTML, XML, CommonMark, man, LaTeX)
- gfm extensions enabled by default, posibility to disable any one or all of them if needed 
- a wrapper library for [cmark-gfm][cmark_link]. 
- Provides additional functionality to facilitate pre-processing input text before parsing or to process the parsed AST before rendering. 

[cmark_link]: https://github.com/github/cmark-gfm
[cmarkorg]: http://commonmark.org/
[spec]: https://github.github.com/gfm/

Quickstart
----------

For simply converting a CommonMark formatted text document to HTML:

~~~python
    >>> import omgfm
    
    >>> print(omgfm.to_html('# this is a level 1 heading'))
    <h1>this is a level 1 heading</h1>
~~~

for raw HTML blocks or inline HTML use the unsafe flag, cmark-gfm escapes raw html by default, omgfm has the same behavior.

~~~python
    >>> omgfm.to_html('<div>text</div>') # default
    '<!-- raw HTML omitted -->\n'
    
    >>> omgfm.to_html('<div>text</div>', unsafe=True) # unsafe
    '<div>text</div>\n'
~~~

Available renderers:
--------------------
- to_html
- to_xml
- to_latex
- to_commonmark
- to_man

Available options for renderers:
-----------------

#### General (affects both parsing and rendering)
- **exclude_ext** (list, optional) By default all the GFM extensions are enabled, you can pass a list of extensions to exclude. This can be any of the following: 

  - 'autolink', 
  - 'table', 
  - 'strikethrough', 
  - 'tagfilter'

#### Commonmark, Latex and Man only
- **width** (int, optional): Specify wrap width. Defaults to 0 (nowrap) Affects rendering Commonmark, Latex and Man.

#### Options affecting rendering
- **source_pos** (bool, optional): Include source index attribute. Default is False.
- **hard_breaks** (bool, optional): Treat newlines as hard line breaks.
- **unsafe** (bool, optional): Render raw HTML and unsafe links. By default, raw HTML is replaced by a placeholder HTML comment. Unsafe links are replaced by empty strings. Defaults to False.
- **no_breaks** (bool, optional): Render soft line breaks as spaces

#### options affecting parsing
- **validate_utf8** (bool, optional): Replace invalid UTF-8 sequences with U+FFFD. Default is False.
- **smart** (bool, optional): Use smart punctuation. (convert straight quotes to curly, --- to em dashes, -- to en dashes) Default is False.
- **github_pre_lang** (bool, optional): Use GitHub-style \<pre lang> for code blocks.
- **liberal_html_tag** (bool, optional): Be liberal in interpreting inline HTML tags.
- **footnotes** (bool, optional): Parse footnotes. Defaluts to False
- **strikethrough_double_tilde** (bool, optional): Only parse strikethroughs if surrounded by exactly 2 tildes. Gives some compatibility with redcarpet. Defaults to False.
- **table_prefer_style_attributes** (bool, optional): Use style attributes to align table cells instead of align attribute.
- **full_info_string** (bool, optional): Include the remainder of the info string in code blocks in a separate attribute.

## Advanced features

If you want to be able to perform pre processing on your source document before parsing or manipulate the parsed AST before rendering  <....> provides some options.

The starting point to use this functionality is the CommonMark class.

~~~python
from omgfm import CommonMark
~~~

The CommonMark class allows you to register a processor to run over the source text with *CommonMark.register_text_processor*  this method accepts the name of the processor, the callable to use for processing. 

**Example using one of the built in pre-processors:**

~~~python
from omgfm import CommonMark
from omgfm.processors import ExtractMetadata

cm = CommonMark()
extact_metadata = ExtractMetadata()
cm.register_text_processor('metadata', extact_metadata)
~~~

ExtractMetadata, when used as above (the default) will look for a metadata header in the source text. The header should be delimited by at least 3 "-" on the *first* line of document and at least 3 "-" after the header. Each line should have a single ":" delimited key-value pair. Like this:

~~~
---
foo: bar
baz: fizz
------
rest of your document.
~~~

If we would combine the examples above:

~~~python
>>> from omgfm import CommonMark
>>> from omgfm.processors import ExtractMetadata
>>> 
>>> cm = CommonMark()
>>> extact_metadata = ExtractMetadata()
>>> cm.register_text_processor('metadata', extact_metadata)
>>> 
>>> text = """
... ---
... foo: bar
... baz: fizz
... ------
... rest of your document.
... """
>>> 
>>> doc, data = cm.to_html(text)
>>> print(doc)
<p>rest of your document.</p>

>>> print(data)
{'metadata': {'foo': ' bar', 'baz': ' fizz'}}
>>>
>>> data['metadata']
{'foo': ' bar', 'baz': ' fizz'}

~~~

`CommonMark.to_html` will always return a tuple (rendered document, data) If you registered a processor that collects data, any collected data will be available under the name you registered the processor under. In the example case `data['metadata']`. The same is true for `CommonMark.to_xml`, `CommonMark.to_latex`, `CommonMark.to_man` and `CommonMark.to_commonmark`

The `ExtractMetadata` class can be configured and modified, for more information see the documentation.

## Documentation
Documentation can be built with sphinx. 

~~~shell
$ sphinx-build docs/ <where you put docs>
~~~

