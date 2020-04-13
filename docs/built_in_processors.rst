Built in procesessors
=====================
omgfm comes with a couple of built in processor functions. While they have their use cases ,they are also here to serve as an example of how functionality can be built. 

    - ExtractMetadata_ processes the source text (splits the metadata header from content, extracts data from the header itself. Returns content and data).
    - MaxHeadingLevel_ only modifies an AST before rendering. (e.g. changes all the heading levels in AST before passing it on).
    - HeadingCollector_ simply collects some information about headings and returns that info. It leaves the AST unmodified
    - TOCGenerator_ does what you might expect and generates a tbale of contents

.. _ExtractMetadata: #id1
.. _MaxHeadingLevel_: #id2
.. _HeadingCollector: #id3
.. _TOCGenerator: #id4

ExtractMetadata
---------------
In the introduction_ we have seen an example of using the :class:`~omgfm.processors.ExtractMetadata` class in conjunction with :class:`~omgfm.renderers.CommonMark` to modify the source markdown text and extract data from it.

.. _introduction: introduction.html#advanced-features

By default this processor only accepts key: value pairs, one on each line. It is possible to pass a custom loader for your metadata; for example, when you expect something like JSON or YAML in the header.

This is an example of initialising with the Python standard library :py:func:`json.loads`.

.. highlight: python
.. code-block:: python

    >>> from omgfm.processors import ExtractMetadata
    >>> import json
    >>> em = ExtractMetadata(loader=json.loads)
    >>> text = '''
    ... ------------
    ... ["foo", 
    ... {"bar":["baz", null, 1.0, 2]}
    ... ]
    ... ---
    ... Some more text following the header
    ... '''
    >>> processed, data = em(text)
    >>> data
    ['foo', {'bar': ['baz', None, 1.0, 2]}]
    >>> processed
    'Some more text following the header\\n'


It is also possible to pass arguments or keyword arguments to a custom loader using a tuple and *loader_args* or a dictionary with *loader_kwargs*.

.. highlight: python
.. code-block:: python

    >>> import decimal
    >>> loader_kwargs = {'parse_float':decimal.Decimal}
    >>> em = ExtractMetadata(loader=json.loads, 
    ...          loader_kwargs=loader_kwargs)
    >>> text = """
    ... ------------
    ... {
    ...   "author": "The Author",
    ...   "version": 1.0
    ...   }
    ... ---
    ... Some more text following the header
    ... """
    >>> processed, data = em(text)
    >>> processed
    'Some more text following the header\n'
    >>> data
    {'author': 'The Author', 'version': Decimal('1.0')}


MaxHeadingLevel
---------------
If for some reason you need to enforce a maximum heading level in a document before rendering you could use this processor.

Create an instance of this processor and register it to to run after parsing.

.. highlight: python
.. code-block:: python

    >>> from omgfm import CommonMark 
    >>> from omgfm.processors import MaxHeadingLevel
    >>>
    >>> cm = CommonMark()
    >>> max_heads = MaxHeadingLevel(max_level=4)
    >>> cm.register_ast_processor('max_heads', max_heads)
    >>>
    >>> cm.to_html('###### h6 heading, will render as h4')
    '<h4>h6 heading, will render as h4</h4>'

HeadingCollector
----------------
Below example demonstrated how to het some information about the headings in a document, can be usefull for table of contents generation, or otherwise referencing sections.

.. highlight: python
.. code-block:: python

    >>> from omgfm.processors import HeadingCollector
    >>> from omgfm import CommonMark
    >>> cm = CommonMark()
    >>> hc = HeadingCollector()
    >>> cm.register_ast_processor('headings', hc)
    >>> html, data = cm.to_html('## A single h2 heading')
    >>> data
    {'headings': [{'level': 2, 'text': 'A single h2 heading', 'line_number': 1}]}
 

TOCGenerator
------------
Generate a table of contents, by default the toc is appended as first child of the root document and an anchor link is added to every heading in the document to make in-document links work. Since for generating the toc an id attribute has to be set on the header and this can only be done with raw html, the renderer must be set to *unsafe* for this to work. Alternativeley you can specify *inject=False* to leave the headings alone and return the generated toc (as rendered HTML) in the data attribute.

.. highlight: python
.. code-block:: python

    >>> from omgfm.processors import TOCGenerator
    >>> from omgfm import CommonMark
    >>> cm = CommonMark()    
    >>> toc = TOCGenerator() # defaults
    >>> cm.register_ast_processor('toc', toc)
    >>> text = """
    text = """
    # Heading 1
    ## Heading 1.2
    ### Heading 1.2.1
    #### Heading 1.2.1.1
    """
    <ul>
    <li><a href="#2-heading-1" title="Heading 1">Heading 1</a>
    <ul>
    <li><a href="#3-heading-1-2" title="Heading 1.2">Heading 1.2</a>
    <ul>
    <li><a href="#4-heading-1-2-1" title="Heading 1.2.1">Heading 1.2.1</a>
    <ul>
    <li><a href="#5-heading-1-2-1-1" title="Heading 1.2.1.1">Heading 1.2.1.1</a></li>
    </ul>
    </li>
    </ul>
    </li>
    </ul>
    </li>
    </ul>
    <h1 id="2-heading-1">Heading 1</h1>
    <h2 id="3-heading-1-2">Heading 1.2</h2>
    <h3 id="4-heading-1-2-1">Heading 1.2.1</h3>
    <h4 id="5-heading-1-2-1-1">Heading 1.2.1.1</h4>

   
To not inject the toc into document instantiate like so:

.. highlight: python
.. code-block:: python

    toc = TOCGenerator(inject=False)

to limit the toc depth:

.. highlight: python
.. code-block:: python

    toc = TOCGenerator(max_depth=4)

