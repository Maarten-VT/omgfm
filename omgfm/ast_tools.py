""" Utilities to create parsers, renderers and nodes as well as iterators. Some of the functions lay fairly close on top of the C library. 
This means that some care must be taken when it comes to memory management. It is recommended to do any manipulation of the AST 
through processors from within the :py:class:`~cmark_gfm.renderers.CommonMark()` class using processors. 

some other considerations: 
    - If you create a node it must be added to an existing tree so that it will be automatically freed with the parent node after rendering. 
    - If a node is not part of a tree and is not used or is unlinked from a tree it must be deleted. 
      Instead of manually unlinking nodes use :py:func:`~cmark_gfm.ast_tools.delete_node` this will unlink the node and free its memory. 
    - Instead of manually unlinking a node and putting another one in its place, it is better to use :py:func:`~cmark_gfm.ast_tools.replace_node` where possible, 
      which will automatically free the node being replaced. 
"""
import re

from omgfm import _wrapper_cmark_gfm as _cmark

ENCODING = 'utf-8'


available_options = {
    'source_pos': _cmark.CMARK_OPT_SOURCEPOS,
    'hard_breaks': _cmark.CMARK_OPT_HARDBREAKS,
    'unsafe': _cmark.CMARK_OPT_UNSAFE,
    'no_breaks': _cmark.CMARK_OPT_NOBREAKS,
    'validate_utf8': _cmark.CMARK_OPT_VALIDATE_UTF8,
    'smart': _cmark.CMARK_OPT_SMART,
    'github_pre_lang': _cmark.CMARK_OPT_GITHUB_PRE_LANG,
    'liberal_html_tag': _cmark.CMARK_OPT_LIBERAL_HTML_TAG,
    'footnotes': _cmark.CMARK_OPT_FOOTNOTES,
    'strikethrough_double_tilde': _cmark.CMARK_OPT_STRIKETHROUGH_DOUBLE_TILDE,
    'table_prefer_style_attributes': _cmark.CMARK_OPT_TABLE_PREFER_STYLE_ATTRIBUTES,
    'full_info_string': _cmark.CMARK_OPT_FULL_INFO_STRING
}
"""Mapping of friendly names to integer options that can be passed to cmark functions"""


type_map = {
    'none': _cmark.NODE_NONE,
    'document' : _cmark.NODE_DOCUMENT,
    'block_quote': _cmark.NODE_BLOCK_QUOTE,
    'list': _cmark.NODE_LIST,
    'list_item': _cmark.NODE_ITEM,
    'code_block': _cmark.NODE_CODE_BLOCK,
    'html_block': _cmark.NODE_HTML_BLOCK,
    'custom_block': _cmark.NODE_CUSTOM_BLOCK,
    'paragraph': _cmark.NODE_PARAGRAPH,
    'heading': _cmark.NODE_HEADING,
    'thematic_break': _cmark.NODE_THEMATIC_BREAK,
    'footnote-definition': _cmark.NODE_FOOTNOTE_DEFINITION,
    'text': _cmark.NODE_TEXT,
    'softbreak': _cmark.NODE_SOFTBREAK,
    'linebreak': _cmark.NODE_LINEBREAK,
    'code': _cmark.NODE_CODE,
    'html_inline': _cmark.NODE_HTML_INLINE,
    'custom_inline': _cmark.NODE_CUSTOM_INLINE,
    'emph': _cmark.NODE_EMPH,
    'strong': _cmark.NODE_STRONG,
    'link': _cmark.NODE_LINK,
    'image': _cmark.NODE_IMAGE,
    'footnote_reference': _cmark.NODE_FOOTNOTE_REFERENCE,
}
"""Mapping of friendly names to integer node_types that can be passed to cmark functions"""

ext_type_map = {
    'table': _cmark.NODE_TABLE,
    'table_cell': _cmark.NODE_TABLE_CELL,
    'table_row': _cmark.NODE_TABLE_ROW,
    'strikethrough': _cmark.NODE_STRIKETHROUGH
}

list_names = {0: 'no_list', 1: 'bullet_list', 2: 'ordered_list'}
list_tightness = {0: 'loose', 1:'tight'}
list_delimiters = {0: 'no_delimiter', 1: 'period', 2: 'paren'}

# Helpers

def to_c_string(text):
    """convert text to utf-8 encoded byte string

    Args:
        text(string)
    Returns:
        bytes
    """
    return text.encode(ENCODING)


def from_c_string(text):
    """convert utf-8 encoded byte string text to utf-8 encoded python string

    Args:
        text(bytes)
    Returns:
        string
    """
    return text.decode(ENCODING)


def list_available_node_types():
    """returns the friendly names of all available node types
    """
    return list(type_map.keys())


def list_available_options():
    """returns the friendly names of all available rendering and parsing options
    """
    return list(available_options.keys())


def version_string():
    """the cmark-gfm C library version string
    """
    return from_c_string(_cmark.version_string())

# Higher level wrappers, allowing to create nodes and assign attributes/content in a single call

def make_heading(level, text=None):
    heading = new_node('heading')
    set_heading_level(heading, level)
    if text is not None:
        text_node = make_text_node(text)
        set_literal(text_node, text)
        append_child(heading, text_node)
    return heading


def make_html_node(block=True, content=None):
    """Creates a HTML Block node or an HTML Inline node
    
    Args:
        block (bool, optional): Creates a Block node if set to True, an inline node if set to False. Defaults to True.
        content (string, optional): The content of the html node. Defaults to None.
    
    Returns:
        cmark_node: HTML block or inline node
    """
    block = _cmark.NODE_HTML_BLOCK if block else _cmark.NODE_HTML_INLINE
    node = _cmark.node_new(block)
    if content is not None:
        _cmark.node_set_literal(node, to_c_string(content))
    return node


def make_text_node(text):
    """Creates a text node with content
    
    Args:
        text (string): Text content to add to the newly created node
    
    Returns:
        cmark_node: a text node with *text* as literal content
    """
    node = _cmark.node_new(_cmark.NODE_TEXT)
    _cmark.node_set_literal(node, to_c_string(text))
    return node


def make_list_node(ordered=True, tight=True, delimiter=0):
    """Creates a list node
    
    Args:
        ordered (bool, optional): Set to False for an unordered list. Defaults to True.
        tight (bool, optional): Sets the list tightness. False for loose list. Defaults to True.
        delimiter (int, optional): set to 1 for period "." delimiter, set to 2 for paren delimiter ")". 
            Defaults to 0 (no delimiter). Defined in C as below:

            .. code-block:: python

                CMARK_NO_DELIM = 0
                CMARK_PERIOD_DELIM = 1
                CMARK_PAREN_DELIM = 2
    
    """
    lst = _cmark.node_new(_cmark.NODE_LIST)
    ordered = _cmark.CMARK_ORDERED_LIST if ordered else _cmark.CMARK_BULLET_LIST
    tight = 1 if tight else 0
    _cmark.node_set_list_type(lst, ordered)
    _cmark.node_set_list_tight(lst, tight)
    if delimiter:
        _cmark.node_set_list_delim(lst, delimiter)
    return lst


def make_list_item():
    """Creates a new list item node.
    """
    item = _cmark.node_new(_cmark.NODE_ITEM)
    return item


def make_paragraph(text=None):
    """Creates a paragraph node
    
    Args:
        text (string, optional): Pass this keyword argument of you would like to create a child node with text content. Defaults to None.
    
    Returns:
        cmark_node: a paragraph node (with a text node child if specified)
    """
    paragraph = _cmark.node_new(_cmark.NODE_PARAGRAPH)
    if text is not None:
        text_node = make_text_node(text)
        append_child(paragraph, text_node)
    return paragraph


def make_link(url, title=None, text=None):
    """Creates a link node
    
    Args:
        url (string): url to assign to link node
        title (string, optional): assign a title to node on creation. Defaults to None.
        text (string, optional): assign link text on creation. Defaults to None.
    
    Returns:
        cmark_node: a link node including any assigned properties
    """
    node = _cmark.node_new(_cmark.NODE_LINK)
    _cmark.node_set_url(node, to_c_string(url))
    if title is not None:
        _cmark.node_set_title(node, to_c_string(title))
    if text is not None:
        text_node = make_text_node(text)
        append_child(node, text_node)
    return node


def make_image(url, title=None, description=None):
    """Creates an image node
    
    Args:
        url (string): url to assign to image node
        title (string, optional): assign a title to node on creation. Defaults to None.
        description (string, optional): set image description on creation. Defaults to None
    
    Returns:
        cmark_node: a image node including any assigned properties
    """
    image = new_node('image')
    set_url(image, url)
    if title is not None:
        set_title(image, title)
    if description is not None:
        text_node = make_text_node(description)
        append_child(image, text_node)      
    return image


# Node accessors

def get_start_line(node):
    """Returns the line on which *node* begins.
    """
    return _cmark.node_get_start_line(node)



def get_end_line(node):
    """Returns the line on which *node* ends.
    """
    return _cmark.node_get_end_line(node)


def get_start_column(node):
    """Returns the column at which *node* begins
    """
    return _cmark.node_get_start_column(node)


def get_end_column(node):
    """Returns the column at which *node* ends
    """
    return _cmark.node_get_end_column(node)


def set_literal(node, text):
    """Sets the string contents of node to *text* . 
    
    Args:
        node (cmark_node): The node to set the string content on
        text (string): The text to set on *node*

    Returns: 
        int: 1 on success, 0 on failure."""
    text = to_c_string(text)
    return _cmark.node_set_literal(node, text)


def get_literal(node):
    """Get string content of a node.
    
    Args:
        node (cmark_node): The node to request the string content of
    
    Returns:
        string: Returns the string contents of node, or an empty string if none is set. Returns None if called on a node that does not have string content
    """
    content = _cmark.node_get_literal(node)
    if content is not None:
        content = from_c_string(content)
    return content


def set_title(node, title):
    """Sets the title of a link or image node. Returns 1 on success, 0 on failure.
    
    Args:
        node (cmark_node): The node to set the title attribute on
        title (string): Title as string
    
    Returns:
        int: 0 on failure, 1 on success
    """
    title=to_c_string(title)
    return _cmark.node_set_title(node, title) 


def get_title(node):
    """returns the title of a link or image node, or an empty string if no title is set. Returns None if called on a node that is not a link or image.
    
    Args:
        node (cmark_node): The node to get the title property of
    
    Returns:
        string: url or empty string if url is not set. returns :py:data:`None` if node is not a link or image
    """
    title = _cmark.node_get_title(node)
    if title is not None:
        title = from_c_string(title)
    return title 


def set_url(node, url):
    """Sets the URL of a link or image node. Returns 1 on success, 0 on failure.
    
    Args:
        node (cmark_node): The node to set the url property on
        url (string): the url
    
    Returns:
        int: 0 on failure, 1 on success
    """
    url = to_c_string(url)
    return _cmark.node_set_url(node, url)


def get_url(node):
    """Returns the URL of a link or image node, or an empty string if no URL is set. Returns None if called on a node that is not a link or image.
    
    Args:
        node (cmark_node): The node to get the url property from
    
    Returns:
        string: url or empty string if url is not set. returns :py:data:`None` if node is not a link or image
    """
    ntype = _cmark.node_get_type(node)
    url = None
    if ntype == _cmark.NODE_LINK or ntype == _cmark.NODE_IMAGE:
        url = from_c_string(_cmark.node_get_url(node))
    return url


def set_heading_level(node, level):
    """Sets the heading level of node, returning 1 on success and 0 on error.
    
    Args:
        node (cmark_node): The node to modify the heading level on
        level (int): integer between 1 and 6 to assign to node heading level
    
    Returns:
        int: 0 on failure, 1 on success
    """
    return _cmark.node_set_heading_level(node, level)


def get_heading_level(node):
    """Returns the heading level of node, or 0 if node is not a heading.
    
    Args:
        node (cmark_node): the node to get the heading level of
    
    Returns:
        int: 0 if node is not a heading, int between 1 and 6 on success
    """
    return _cmark.node_get_heading_level(node)


def get_type_string(node):
    """Returns a string representation of the node type, or "<unknown>"."""
    return from_c_string(_cmark.node_get_type_string(node))


def get_type(node):
    """Returns the type of node as integer, or 0 on error.
    
    Returns:
        int: node type
    """
    return _cmark.node_get_type(node)

# Creating and destroying nodes

def new_node(ntype):
    """Creates a new node of type ntype. Note that the node may have other required properties, which it is the caller's responsibility to assign.
    
    Args:
        ntype (string): any of the available node types below:
        
            - linebreak
            - code
            - text
            - image
            - emph
            - html_inline
            - custom_block
            - softbreak
            - list_item
            - html_block
            - footnote_reference
            - document
            - custom_inline
            - link
            - thematic_break
            - strong
            - none
            - code_block
            - list
            - footnote-definition
            - paragraph
            - block_quote
            - heading
    
    Returns:
        cmark_node: a new instance of a cmark node
    """
    nodetype = type_map.get(ntype)
    if nodetype is None:
        raise ValueError('unknown node_type "{}"'.format(ntype))
    return _cmark.node_new(nodetype)
    

def new_node_with_extension(ntype, ext):
    """creates a node specific to cmark-gfm extensions
    
    Args:
        ntype (string): string representation of the type of node being created.
            can be any of the folowing:

                - table
                - table_cell
                - table_row
                - strikethrough

        ext (string): string representation of the extension this node belongs to.
    
    Returns:
        cmark_node: a new instance of a cmark node
    """
    exts = ['autolink', 'table', 'strikethrough']
    node_type = ext_type_map.get(ntype)
    if node_type is None:
        raise ValueError('unknown node_type "{}"'.format(ntype))
    if ext not in exts:
        raise ValueError('unknown extension "{}"'.format(ext))
    ext = _cmark.find_syntax_extension(to_c_string(ext))
    return _cmark.node_new_with_ext(node_type, ext)
    
    

def free_node(node):
    """Frees memory allocated to *node* destroying the node"""
    _cmark.node_free(node)
    # To prevent a segmentation fault in case _cmark.node_free is called on an already freed node,
    # or when any modifications are attempted on an already freed node
    # Will now result in a NameError instead
    del(node)


def delete_node(node):
    """unlinks *node* and its children from tree and frees its memory. Effectively this destroys the node.
    """
    status = _cmark.node_unlink(node)
    _cmark.node_free(node)
    # To prevent a segmentation fault in case _cmark.node_free is called on an already freed node,
    # or when any modifications are attempted on an already freed node
    # Will now result in a NameError instead
    del(node) 
    return status



# Tree manipulation

def unlink_node(node):
    """Unlinks *node* but does not free its memory.
    free node's memory with :py:func:`~cmark_gfm.ast_tools.free_node`.
    Alternativeliy use :py:func:`~cmark_gfm.ast_tools.delete_node` instead of unlink_node to automatically free memory after unlinking.
    """
    return _cmark.node_unlink(node)


def replace_node(old_node, new_node):
    """Replaces *old_node* with *new_node*. *old_node* is destroyed.

    Returns: 
        int: 1 on success, 0 on failure
    """
    status = _cmark.node_replace(old_node, new_node)
    delete_node(old_node)
    return status


def insert_sibling_before(node, sibling):
    """Inserts *sibling* before *node* 
    
    Returns: 
        int: 1 on success, 0 on failure
    """
    return _cmark.node_insert_before(node, sibling)


def insert_sibling_after(node, sibling):
    """Inserts *sibling* after *node* 
    
    Returns: 
        int: 1 on success, 0 on failure    
    """
    return _cmark.node_insert_after(node, sibling)


def append_child(node, child):
    """Appends *child* to *node*'s children
    
    Returns: 
        int: 1 on success, 0 on failure    
    """
    return _cmark.node_append_child(node, child)


def prepend_child(node, child):
    """Prepends *child* to *node*'s children
    
    Returns: 
        int: 1 on success, 0 on failure    
    """
    return _cmark.node_prepend_child(node, child)


# Tree traversal

def node_next(node):
    """Returns the next node in the sequence after node, or None if there is none.
    """
    return _cmark.node_next(node)


def node_previous(node):
    """Returns the previous node in the sequence after node, or None if there is none.
    """
    return _cmark.node_previous(node)


def node_parent(node):
    """Returns the parent of node, or None if there is none.
    """
    return _cmark.node_parent(node)


def node_first_child(node):
    """Returns the first child of node, or None if node has no children.
    """
    return _cmark.node_first_child(node)


def node_last_child(node):
    """Returns the last child of node, or None if node has no children.
    """
    return _cmark.node_last_child(node)


# Iterator

def new_iterator(root):
    """Creates a new iterator starting at root. The current node and event type are undefined until :py:func:`~cmark_gfm.ast_tools.iter_next` is called for the first time. 
    The memory allocated for the iterator should be released using :py:func:`~cmark_gfm.ast_tools.free_iterator` when it is no longer needed.
    Alternatively use :py:func:`~cmark_gfm.ast_tools.walk` which returns a python iterator and frees memory automaticaly after iteration is done.
    
    Args:
        root (cmark_nod): The root node to iterate over
    
    Returns:
        cmark_iterator: iterator that can be used to traverse a tree of nodes.
    """
    return _cmark.iter_new(root)


def free_iterator(iterator):
    """Frees the memory allocated for an iterator.
    
    Args:
        iterator (cmark_iterator): The itarator to free
    """
    _cmark.iter_free(iterator)
    # To prevent a segmentation fault in case _cmark.iter_free is called on an already freed iterator,
    # or when any modifications are attempted on an already freed iterator
    # Will now result in a NameError instead
    del(iterator)


def iter_next(iterator):
    """Advances to the next node and returns the event type (EVENT_ENTER, EVENT_EXIT or EVENT_DONE).
    
    Args:
        iterator (cmark_iterator): the iterator to call "next" on.
    
    Returns:
        int: cmark event type as described below:

            .. code-block::

                EVENT_NONE = 0
                EVENT_DONE = 1
                EVENT_ENTER = 2
                EVENT_EXIT = 3

    """
    return _cmark.iter_next()


def iter_get_node(iterator):
    """Returns the current node.
    
    Args:
        iterator (cmark_iterator): The iterator to get the current node from
    
    Returns:
        cmark_node: Returns the curent node in iteration.
    """
    return _cmark.iter_get_node(iterator)


def iter_get_event_type(iterator):
    """Returns the current event type.
    
    Args:
        itarator ([cmark_iterator): Iterator to get the current event type from
    
    Returns:
        int: cmark event type as described below:

            .. code-block::

                EVENT_NONE = 0
                EVENT_DONE = 1
                EVENT_ENTER = 2
                EVENT_EXIT = 3

    """

    return _cmark.iter_get_event_type(iterator)


def iter_get_root(iterator):
    """ returns the root node.
    """
    return _cmark.iter_get_root(iterator)


def iter_reset(iterator, node, event_type):
    """Resets the iterator so that the current node is current and the event type is event_type. 
    The new current node must be a descendant of the root node or the root node itself.
    
    Args:
        iterator (cmark_iterator): The iterator to reset
        node (cmark_node): Node to make current
        event_type (int): any of the events below:

            .. code-block::

                EVENT_NONE = 0
                EVENT_DONE = 1
                EVENT_ENTER = 2
                EVENT_EXIT = 3


    """
    return _cmark.iter_reset(iterator, node, event_type)


# Parsing

def new_parser(exclude_ext=None, **options):
    """Creates a new parser.
    NOTE: The returned parser must be freed with :py:func:`~cmark_gfm.ast_tools.free_parser`
    
    By default all available extensions are attached to parser.

    Args:
        exclude_ext (list, optional): extensions to exclude from the parsing process. Defaults to None.

    
    **Options:**
        If no options are passed the paser is created with the default options.
        For available options see :py:func:`~cmark_gfm.ast_tools.make_options`
    
    Returns:
        cmark_parser: cmark parser created with *options*
    """
    options = 0 if not options else make_options(**options)
    parser = _cmark.parser_new(options)
    # Setup parser with extensions
    extensions = _cmark.EXTENSIONS
    # Remove any exluded extensions from the defaults
    if exclude_ext is not None:
        extensions = [ext for ext in extensions if ext not in exclude_ext]
        
    for name in extensions:
        ext = _cmark.find_syntax_extension(to_c_string(name)) 
        success = _cmark.parser_attach_syntax_extension(parser, ext)
        assert success

    return parser


def parser_free(parser):
    """Frees memory allocated for a parser object.
    """
    _cmark.parser_free(parser)


def parser_feed(parser, text):
    """Feeds a string to parser.
    """
    text = to_c_string(text)
    _cmark.parser_feed(parser, text, len(text))


def parser_finish(parser):
    """Finish parsing and return a pointer to a tree of nodes
    NOTE: The retrurned tree of nodes must be freed with :py:func:`~cmark_gfm.ast_tools.free_node`
    """
    return _cmark.parser_finish(parser)


def parser_get_syntax_extensions(parser):
    """Gets the extensions currently applied to *parser*

    This returns a calculated integer value representing the active syntax extensions of *parser*. 
    This can in turn be passed to :py:func:`~cmark_gfm.ast_tools.render_html`.
    
    Args:
        parser (cmark_parser): The parser to get the currently active extensions from
    
    Returns:
        int: Integer representation of the active extensions
    """
    return _cmark.parser_get_syntax_extensions(parser)


# Rendering

def render_html(root_node, extensions, **options):
    """Render a node tree as an HTML fragment. It is up to the user to add an appropriate header and footer. 
    """
    options = make_options(**options)
    return _cmark.render_html(root_node, options, extensions)


def render_xml(root_node, **options):
    """Render a node tree as XML.
    """
    options = make_options(**options)
    return _cmark.render_xml(root_node, options)


def render_latex(root_node, width=0, **options):
    """Render a node tree as a LaTeX document.
    """
    options = make_options(**options)
    return _cmark.render_latex(root_node, options, width)


def render_man(root_node, width=0, **options):
    """Render a node tree as a groff man page, without the header.
    """
    options = make_options(**options)
    return _cmark.render_man(root_node, options, width)


def render_commonmark(root_node, width=0, **options):
    """Render a node tree as a commonmark document.
    """
    options = make_options(**options)
    return _cmark.render_commonmark(root_node, options, width)


# Convenience functions that handle *some* of the memory management automaticaly

def walk(root_node):
    """Create an iterator and walk the root node.
    Yield each encountered node, the status of iteration and node type.
    Stop when iteration is done.
    
    Nodes must only be modified after an EXIT event (*entering* is False), or an ENTER event for leaf nodes (*entering* is True).

    Args:
        root_node (cmark_node): The node to iterate over
    
    Yields:
        tuple containing the curent node returned by iterator, whether the node is being entered and the nodes type. 
        the node type can be compared to the types defined in the wrapper libary.

    :rtype: Iterator[tuple(cmark_node, entering (bool), cmark_node_type (int))]
    """
    it = _cmark.iter_new(root_node)
    while True:
        entering = False
        status = _cmark.iter_next(it)
        if status == _cmark.EVENT_DONE:
            break
        current_node = _cmark.iter_get_node(it)
        if status == _cmark.EVENT_ENTER: 
            entering = True
        yield current_node, entering, _cmark.node_get_type(current_node)

    # free memory of iterator
    free_iterator(it)   

def make_options(**options):
    """Generate the proper integer value to pass to cmark renderers and parsers based on keyword arguments
    
    Keyword Args:
         source_pos (bool, optional): Include source index attribute. Default is False.

         hard_breaks (bool, optional): Treat newlines as hard line breaks.

         unsafe (bool, optional): Render raw HTML and unsafe links 
            By default, raw HTML is replaced by a placeholder HTML comment. 
            Unsafe links are replaced by empty strings. Defaults to False.
        
         no_breaks (bool, optional): Render soft line breaks as spaces
        
         validate_utf8 (bool, optional): Replace invalid UTF-8 sequences with U+FFFD. Default is False.
        
         smart (bool, optional): Use smart punctuation. 
            (convert straight quotes to curly, --- to em dashes, -- to en dashes) Default is False.
        
         github_pre_lang (bool, optional): Use GitHub-style <pre lang> for code blocks.
        
         liberal_html_tag (bool, optional): Be liberal in interpreting inline HTML tags.
        
         footnotes (bool, optional): Parse footnotes. Defaluts to False
        
         strikethrough_double_tilde (bool, optional): 
            Only parse strikethroughs if surrounded by exactly 2 tildes. 
            Gives some compatibility with redcarpet. Defaults to False.
        
         table_prefer_style_attributes (bool, optional): 
            Use style attributes to align table cells instead of align attribute.
        
         full_info_string (bool, optional): 
            Include the remainder of the info string in code blocks in a separate attribute.

    """
    base_options = _cmark.CMARK_OPT_DEFAULT
    # check passed options with available options
    for name , val in options.items():
        opt = available_options.get(name)
        if val and opt is not None:
            base_options |= opt
        if opt is None:
            raise TypeError("got an unexpected keyword argument '{}'".format(name))
    return base_options

    
    
