"""Basic rendering options. Renderers that accept text and convert to selected formats.
""" 

from omgfm import _wrapper_cmark_gfm as _cmark
from omgfm.ast_tools import (
    to_c_string, from_c_string, available_options, make_options, 
    new_parser, parser_finish, parser_feed, parser_free, free_node)


def render(text, fmt, exclude_ext=None, width=0, **options):
    """Convert *text* to selected output format *fmt*
    
    Args:
        text (str): utf-8 encoded string to render
        fmt (str): The output format to render to. ("html", "xml", "latex", "commonmark" or "man")
        exclude_ext (list, optional): extensions to exclude from the rendering process. Defaults to None.
        width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
            for rendering Commonmark, Latex and Man.
    

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
    
    Returns:
         string: UTF-8 encoded string in the chosen output format
    """
    OPTS = make_options(**options)

    output = ""

    parser =  new_parser(exclude_ext=exclude_ext, **options) 
    exts = _cmark.parser_get_syntax_extensions(parser)
    
    # Parse document from text

    parser_feed(parser, text)
    doc = parser_finish(parser)

    if fmt == 'html':    
        output = _cmark.render_html(doc, OPTS, exts)

    if fmt == 'xml':
        output = _cmark.render_xml(doc, OPTS)

    if fmt == 'latex':
        output = _cmark.render_latex(doc, OPTS, width)
       
    if fmt == 'commonmark':
        output = _cmark.render_commonmark(doc, OPTS, width)    

    if fmt == 'man':
        output = _cmark.render_man(doc, OPTS, width)
    
    # Free memory of parser and document
    # Document is root node, children will also be freed
    parser_free(parser)
    free_node(doc)

    return output.decode('utf-8')


def to_html(text, exclude_ext=None, **options):
    """"Use cmark-gfm to render markdown into HTML.
    
    Args:
        text (str): utf-8 encoded string to render
        exclude_ext (list, optional): extensions to exclude from the rendering process. Defaults to None.
        options: the options to be passed to :py:func:`render`
            see the options available in :py:func:`render` for more information

    Returns:
        string: UTF-8 encoded HTML formatted string
    """
    return render(text, 'html', exclude_ext=exclude_ext, **options)


def to_xml(text, **options):
    """Use cmark-gfm to render markdown into XML.
    
    Args:
        text (str): utf-8 encoded string to render
        options: the options to be passed to :py:func:`render`
            see the options available in :py:func:`render` for more information
    
    Returns:
        string: UTF-8 encoded XML formatted string
    """
    return render(text, 'xml', **options)


def to_latex(text, width=0, **options):
    """Use cmark-gfm to render markdown into LaTex.
    
    Args:
        text (str): utf-8 encoded string to render
        width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
        options: the options to be passed to :py:func:`render`
            see the options available in :py:func:`render` for more information
    
    Returns:
        string: UTF-8 encoded LaTex formatted string
    """
    return render(text, 'latex', width=width, **options)


def to_commonmark(text, width=0, **options):
    """Use cmark-gfm to render markdown into CommonMark.
    
    Args:
        text (str): utf-8 encoded string to render
        width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
        options: the options to be passed to :py:func:`render`
            see the options available in :py:func:`render` for more information

    Returns:
        string: UTF-8 encoded CommonMark formatted string
    """
    return render(text, 'commonmark', width=width, **options)


def to_man(text, width=0, **options):
    """Use cmark-gfm to render markdown into Unix Man format.
    
    Args:
        text (str): utf-8 encoded string to render
        width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
        options: the options to be passed to :py:func:`render`
            see the options available in :py:func:`render` for more information

    Returns:
        string: UTF-8 encoded Unix Man formatted string
    """    
    return render(text, 'man', width=width, **options)


class CommonMark:
    """Render markdown into different formats. modify the source text before parsing and hook into the cmark AST post-parsing.
    Enables manipulation of the source text before parsing and manipulation of the AST before rendering by means of registering pre or post processors.
    See :py:mod:`~omgfm.processors` for more information on built in processors and the :py:class:`~omgfm.processors.Processor` base class.
    """
    def __init__(self):
        self.extensions = _cmark.EXTENSIONS
        self.data = {}
        self._processors = {'before_parse': [], 'after_parse': []}  

    def render(self, text, fmt, exclude_ext=None, width=0, **options):
        """Like :py:func:`~omgfm.renderers.render` but with the posibility of running code before or after parsing.
        
        Args:
            text (string): utf-8 encoded string to parse and render
            fmt (str): The output format to render to. ("html", "xml", "latex", "commonmark" or "man")
            exclude_ext (list, optional): extensions to exclude from the rendering process. Defaults to None.
            width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
                for rendering Commonmark, Latex and Man.
        
        Raises:
            TypeError: This is only raised if any of the options passed do not exists in available opions (see :py:func:`~omgfm.renderers.render`)
        
        Returns:
            tuple: 
                - UTF-8 encoded string in the chosen output format 
                - dictionary containing data gathered from processing source text and/or ast or empty dict. 
        """
        OPTS = make_options(**options)
        output = ""

        # run text preprocessors
        text = self._run_processors(text, 'before_parse')

        text = to_c_string(text)
       
        parser = _cmark.parser_new(OPTS)  

        # Setup parser with extensions
        if fmt == 'html':
            extensions = self.extensions
            # Remove any exluded extensions from the defaults
            if exclude_ext is not None:
                extensions = [ext for ext in extensions if ext not in exclude_ext]
            
            for name in extensions:
                ext = _cmark.find_syntax_extension(to_c_string(name)) 
                success = _cmark.parser_attach_syntax_extension(parser, ext)
                assert success

        # Parse document from text
        _cmark.parser_feed(parser, text, len(text))
        doc = _cmark.parser_finish(parser)

        # Run AST postprocessors
        self._run_processors(doc, 'after_parse')

        if fmt == 'html':
            exts = _cmark.parser_get_syntax_extensions(parser)
            output = _cmark.render_html(doc, OPTS, exts)

        if fmt == 'xml':
            output = _cmark.render_xml(doc, OPTS)

        if fmt == 'latex':
            output = _cmark.render_latex(doc, OPTS, width)
        
        if fmt == 'commonmark':
            output = _cmark.render_commonmark(doc, OPTS, width)    

        if fmt == 'man':
            output = _cmark.render_man(doc, OPTS, width)
        
        _cmark.parser_free(parser)
        _cmark.node_free(doc)
        
        output = from_c_string(output)
     
        return output, self.data

    def _register_processor(self, name, processor, entrypoint, index=None):
        item = {'name': name, 'processor': processor} 
        if index is not None:
            self._processors[entrypoint].insert(index, item)
        else:
            self._processors[entrypoint].append(item)

    def _run_processors(self, doc, entrypoint):
        for item in self._processors[entrypoint]:
            doc, data = item['processor'](doc)
            if data:
                self.data.update({item['name']: data})
        return doc

    def register_text_processor(self, name, processor, index=None):
        """Register any functions to manipulate source text before parsing the AST
        """ 
        self._register_processor(name, processor, 'before_parse', index=index)

    def deregister_text_processor(self, name):
        """Removes an text processor with *name* from the pool
        
        Args:
            name (string): Name of the processor to remove
        
        Returns:
            callable: the callable that was registered in case it is needed later.
        """        
        return self._processors['before_parse'].pop(name)

    def register_ast_processor(self, name, processor, index=None):
        """Register any functions to manipulate the AST before rendering

        Example:
            This example only extracts data from the AST after parsing

            .. highlight: python
            .. code-block:: python

                >>> from omgfm import CommonMark
                >>> from omgfm.processors import TOCGenerator
                >>> cm = CommonMark()
                >>> toc = TOCGenerator()       
                >>> cm.register_after_parse('toc', toc)

        """
        self._register_processor(name, processor, 'after_parse', index=index)

    def deregister_ast_processor(self, name):
        """Removes an ast processor with *name* from the pool
        
        Args:
            name (string): Name of the processor to remove
        
        Returns:
            callable: the callable that was registered case it is needed later.
        """
        return self._processors['after_parse'].pop(name)

    def to_html(self, text, exclude_ext=None, **options):
        """"Use cmark-gfm to render markdown into HTML.
        
        Args:
            text (str): utf-8 encoded string to render
            exclude_ext (list, optional): extensions to exclude from the rendering process. Defaults to None.
            options: the options to be passed to :py:func:`CommonMark.render`
                see the options available in :py:func:`~omgfm.renderers.render` for more information

        Returns:
            string: UTF-8 encoded HTML formatted string
        """
        return self.render(text, 'html', exclude_ext=exclude_ext, **options)


    def to_xml(self, text, **options):
        """Use cmark-gfm to render markdown into XML.
        
        Args:
            text (str): utf-8 encoded string to render
            options: the options to be passed to :py:func:`CommonMark.render`
                see the options available in :py:func:`~omgfm.renderers.render` for more information
        
        Returns:
            string: UTF-8 encoded XML formatted string
        """
        return self.render(text, 'xml', **options)


    def to_latex(self, text, width=0, **options):
        """Use cmark-gfm to render markdown into LaTex.
        
        Args:
            text (str): utf-8 encoded string to render
            width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
            options: the options to be passed to :py:func:`CommonMark.render`
                see the options available in :py:func:`~omgfm.renderers.render` for more information
        
        Returns:
            string: UTF-8 encoded LaTex formatted string
        """
        return self.render(text, 'latex', witdth=width, **options)


    def to_commonmark(self, text, width=0, **options):
        """Use cmark-gfm to render markdown into CommonMark.
        
        Args:
            text (str): utf-8 encoded string to render
            width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
            options: the options to be passed to :py:func:`CommonMark.render`
                see the options available in :py:func:`~omgfm.renderers.render` for more information

        Returns:
            string: UTF-8 encoded CommonMark formatted string
        """
        return self.render(text, 'commonmark', witdth=width, **options)


    def to_man(self, text, width=0, **options):
        """Use cmark-gfm to render markdown into Unix Man format.
        
        Args:
            text (str): utf-8 encoded string to render
            width (int, optional): Specify wrap width. Defaults to 0 (nowrap)
            options: the options to be passed to :py:meth:`CommonMark.render`
                see the options available in :py:func:`~omgfm.renderers.render` for more information

        Returns:
            string: UTF-8 encoded Unix Man formatted string
        """    
        return self.render(text, 'man', witdth=width, **options)
