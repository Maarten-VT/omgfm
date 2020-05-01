import re
from omgfm import ast_tools
from omgfm import _wrapper_cmark_gfm as _cmark


def get_headings(document):
    """Find all the headings in *document* and capture data from them.
    Contains an inner function that iterates over any found heading node to extract any text content.
        
    Args:
        document (cmark_node): the root node to iterate over
        
    Example output:

        .. code-block::
        
            {'headings': [{'level': 1, 'text': 'this is a H1 heading', 'line_number': 1}]}

    Returns:
        list: a list of dictionaries containing info about the headings
    """
    def get_heading_info(node):
        level = ast_tools.get_heading_level(node)
        line_no = ast_tools.get_start_line(node)
        # Get the heading level and line number
        # Find any text node to get the heading text
        for cur, entering, node_type in ast_tools.walk(node):
            if entering and node_type == _cmark.NODE_TEXT:
                text = ast_tools.get_literal(cur)
                data = {
                    'level': level,
                    'text': text,
                    'line_number': line_no
                    }
                return(data)  
    heads = []
    for node, entering, node_type in ast_tools.walk(document):        
        if not entering and node_type == _cmark.NODE_HEADING:
            info = get_heading_info(node)
            heads.append(info)  
    return heads


class Processor:
    """Base class for procesors that can be registered 
    on the CommonMark class to perform pre or post processing.
    Either on source text before parsing or a parsed AST.
    When sub-classing the "process_input" method must be implemented.

    The result is a callable class that returns a tuple(*doc*, *data*).
    The "process_input" method can extract data from *doc*, modify *doc* or both.

    *doc* can be either the source text before parsing or a parsed AST.

    Example:
        This example only extracts data without modifying the AST.

        .. highlight: python
        .. code-block:: python

            >>> from omgfm.renderers import CommonMark 
            >>> from omgfm.processors import Processor, get_headings

            >>> class HeadingCollector(Processor):
            ...     def process_input(self, root_node):
            ...         self.data = get_headings(root_node)

            >>> cm = CommonMark()
            >>> process_headings = HeadingCollector()       
            >>> cm.register_ast_processor('headings', process_headings)

        
        Above could be used as follows:

        .. highlight: python
        .. code-block:: python
        
            >>> processed, data = cm.to_html('# this is a H1 heading')
            >>> processed
            '<h1>this is a H1 heading</h1>\\n'
            >>> data
            {'headings': [{'level': 1, 'text': 'this is a H1 heading', 'line_number': 1}]}
    
    """
    def __init__(self, *processor_args, **processor_kwargs):
        self.data = None
        self.processed = None
        self.processor_args = processor_args or ()
        self.processor_kwargs = processor_kwargs or {}
  

    def process_input(self, doc):
        raise NotImplementedError(
        'Processor "{}.{}" must define a process_input method'.format(
            self.__class__.__module__, self.__class__.__name__
        )
    )
    def __call__(self, doc):
        self.process_input(doc, *self.processor_args, **self.processor_kwargs)
        doc = self.processed or doc
        return doc, self.data


class ExtractMetadata(Processor):
    """Extract metadata from the top of a Markdown doacument.

    Metadata header should start with at least 3 dashes --- on the first line and end with at least 3 dashes on the last.
    
    e.g. 
       .. code-block:: 

           ---
           foo: bar
           baz: fizz
           ------
           rest of your document.

    by default this processor only accepts key: value pairs, one on each line. 
    It is possible to pass a custom loader for your metadata; for example, when you expect something like JSON or YAML in the header.

    Example:
        this is an example of initialising with the Python standard library :py:func:`json.loads`

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

    """
    def process_input(self, text, loader=None, **kwargs):
        """Tries to match text with patern to extract metadata from header.

        If a match object is returned extract the following capturing groups:

            - group(1) metadata including delimiters (---)
            - group(2) metadata 
            - group(4) everything after metadata closing delimiter

        The metadata string is then passed to the specified loader. after loading it is assigned to the *data* instance variable.
        The text is assigned to the *proccessed* instance variable.
        """
        # Set up custom loader if specified
        loader_args = kwargs.get('loader_args') or ()
        loader_kwargs = kwargs.get('loader_kwargs') or {}
        loader = loader or self.key_value_to_dict

        patern = r'(-{3,}[\r\n]((.*\s*[\r\n])+?)^-{3,}[\r\n])((.*[\r\n]*)+)'
        matcher = re.compile(patern, re.MULTILINE)
        metadata = None
        match_obj = matcher.search(text)
        if match_obj:
            metadata = match_obj.group(2)
            text = match_obj.group(4)

        self.data = loader(metadata, *loader_args, **loader_kwargs)
        self.processed = text 

    def key_value_to_dict(self, string, delimiter=None):
        """Extract key-value pairs from well formatted text
        
        Args:
            string (string): a (multiline) string containing one key-value pair per line.
            delimiter (string): the string representation of the delimiter used to separate keys and values.
                defaults to ":" if no delimiter is specified
        
        Returns:
            dict: a dictionary containing the extracted key-value pairs
        """
        delimiter = delimiter or ':'              
        data = {}
        lines = string.split('\n')
        for line in lines:
            line = line.strip()
            if line != '':       
                line = line.split(delimiter)
                data[line[0]] = line[1]
        return data


class MaxHeadingLevel(Processor):
    """Enforce a maximum heading level on document before rendering.

    Example:
        Create an instance of this processor and register it to to run after parsing.

        .. highlight: python
        .. code-block:: python

        >>> from omgfm.renderers import CommonMark 
        >>> from omgfm.processors import MaxHeadingLevel

        >>> cm = CommonMark()
        >>> max_heads = MaxHeadingLevel(max_level=4)
        >>> cm.register_ast_processor('max_heads', max_heads)

        >>> processed, data = cm.to_html('###### h6 heading, will render as h4')
        >>> processed
        '<h4>h6 heading, will render as h4</h4>\\n'

    """
    def process_input(self, root_node, max_level=6):
        """calls :py:func:`~omgfm.processors.MaxHeadingLevel.enforce_max_heading_level`
        
        Args:
            root_node (cmark_node): set all headings in document to *max_level*
            max_level (int, optional): the max heading level. Defaults to 6.
        """
        self.enforce_max_heading_level(root_node, max_level=max_level)

    def enforce_max_heading_level(self, root_node, max_level=6):
        """Walks the document and checks the heading levels. 
        If level is higher than *max_level* heading level is set to *max_level*
        
        Args:
            root_node (cmark_node): The document node to iterate over
            max_level (int, optional): The desired maximum heading level. Defaults to 6.
        
        Raises:
            ValueError: If the max_level is set to something higher than 6 or lower than 1
        """
        for node, entering, node_type in ast_tools.walk(root_node):        
            if entering and node_type == _cmark.NODE_HEADING:
                level = ast_tools.get_heading_level(node)
                if max_level > 6 or max_level < 0:
                    raise ValueError('max_level must be between 1 and 6')
                if level > max_level:
                    ast_tools.set_heading_level(node, max_level)


class HeadingCollector(Processor):
    """Collect a list of dictionaries containing information about every heading in the document.
    """
    def process_input(self, root_node):
        self.data = self.get_headings(root_node)

    def get_headings(self, document):
        """Find all the headings in *document* and capture data from them.
        Contains an inner function that iterates over any found heading node to extract any text content.
        
        Args:
            document (cmark_node): the root node to iterate over
        
        Returns:
            list: a list of dictionaries containing info about the headings
        """
        def get_heading_info(node):
            level = ast_tools.get_heading_level(node)
            line_no = ast_tools.get_start_line(node)
            # Get the heading level and line number
            # Find any text node to get the heading text
            for cur, entering, node_type in ast_tools.walk(node):
                if entering and node_type == _cmark.NODE_TEXT:
                    text = ast_tools.get_literal(cur)
                    data = {
                        'level': level,
                        'text': ast_tools.from_c_string(text),
                        'line_number': line_no
                        }
                    return(data)  
        heads = []
        for node, entering, node_type in ast_tools.walk(document):        
            if not entering and node_type == _cmark.NODE_HEADING:
                info = get_heading_info(node)
                heads.append(info)  
        return heads


class TOCGenerator(Processor):
    """ Generate a table of contents for document and return as a data attribute on document. Optionaly inject toc into document bofore rendering.
    """
    def process_input(self, root_node, max_depth=6, inject=True):
        """Walks the *root_node* to collect headings and generates HTML table of contents.
        
        Args:
            root_node (cmark_node): The root document to generate a TOC for
            max_depth (int, optional): Maximum heading level to use for toc generation. Defaults to 6.
            inject (bool, optional): If set to True TOCGenerator will prepend the TOC to the beginning of the document. 
                Will also replace the headings with raw HTML that includes the ID and anchor link. Defaults to True.
                **Note**: Because injecting the toc involves rendering raw HTML, the renderer should be set up with *unsafe=True*
        
        Raises:
            ValueError: If the max_depth is set to something higher than 6 or lower than 1
        """
        
        if max_depth > 6 or max_depth < 0:
            raise ValueError('max_level must be between 1 and 6')
        
        self.inject = inject
        headings = self.set_heading_attributes(root_node, max_depth)
        nested = self.nest_toc_items(headings)
        toc = self.toc_to_nodes(nested)
        if self.inject:
            #toc = make_html_node(block=True, content=html)
            ast_tools.prepend_child(root_node, toc)
        self.data = ast_tools.from_c_string(ast_tools.render_html(toc, 0))

    def set_heading_attributes(self, root_node, max_depth):
        """Iterate over root node, create heading tokens to generate toc, replace heading nodes in tree with html.
        """   
        headings_list = []
        for node, entering, node_type in ast_tools.walk(root_node):
            if not entering and node_type == _cmark.NODE_HEADING:
                level = ast_tools.get_heading_level(node)
                line_number = ast_tools.get_start_line(node)
                text = ''
                if not level > max_depth:
                    for cur, entering, node_type in ast_tools.walk(node):
                        if entering and node_type == _cmark.NODE_TEXT:
                            text = ast_tools.get_literal(cur)
                            data = {
                                'level': level,
                                'text': text,
                                'line_number': line_number
                            }
                            headings_list.append(data)
                
                # replace headings in AST with raw html for working toc links 
                if self.inject:
                    template = '<h{level} id="{_id}">{text}</h{level}>'
                    _id = '{}-{}'.format(line_number, self.slugify(text))
                    heading = template.format(level=level, _id =_id, text=text)
                    new_node =ast_tools.make_html_node(content=heading)
                    ast_tools.replace_node(node, new_node)

        return headings_list

    def nest_toc_items(self, toc_list):
        """Nest the items from toc list based on the heading level 1 to 6.
        """
        processed = []
        if len(toc_list):
            last_item = toc_list.pop(0)
            last_item['children'] = []
            last_level = last_item['level']
            parent_list = []
            processed.append(last_item)
            for item in toc_list:
                item['children'] = []
                level = item['level']
                if level < last_level: 
                    if parent_list:
                        # remove all parents that have a higher or equal level to current item
                        for parent in reversed(parent_list):    
                            if level <= parent['level']:
                                parent_list.pop(parent_list.index(parent))
                    last_level = level
                # If after poping there are still parents in parent_list
                # append current item to last parent's children
                # otherwise the current item is a sibling to last item
                if level == last_level:
                    if len(parent_list):
                        parent_list[-1]['children'].append(item)                          
                    else:
                        processed.append(item)
                        
                # If we arrive here current item has a higher heading level than last item
                # making it a child to last item 
                else:
                    last_item['children'].append(item)
                    parent_list.append(last_item)
                    last_level = level
                
                last_item = item
           
        return processed

    def toc_to_nodes(self, toc):
        """Create tree of nodes from tokens generated by :py:func:`~TOCGenerator.nest_toc_tokens`
        """
        toc_node = ast_tools.make_list_node(ordered=False)

        def build_toc_nodes(toc, parent_node):
            for item in toc:
     
                line_number = item.get('line_number')
                item_text = item.get('text', '')
                href = '#{}-{}'.format(line_number, self.slugify(item_text))

                paragraph = ast_tools.make_paragraph()
                anchor = ast_tools.make_link(href, title=item_text, text=item_text)
                #make a new item
                list_item = ast_tools.make_list_item()
                #place anchor node in paragraph
                ast_tools.append_child(paragraph, anchor)
                #place paragraph in list item
                ast_tools.append_child(list_item, paragraph)
                if item.get('children'):
                    inner_list = ast_tools.make_list_node(ordered=False)
                    children = build_toc_nodes(item['children'], inner_list)
                    ast_tools.append_child(list_item, children)
                #apend the final item to parent list
                ast_tools.append_child(parent_node, list_item)
            return parent_node
        
        build_toc_nodes(toc, toc_node)

        return toc_node

    def slugify(self, text):
        """covert string to slug suitable for urls
        """
        # Ugly but works
        text = text.lower()
        for c in [' ', '-', '.', '/']:
            text = text.replace(c, '_')
        text = re.sub(r'\W', '', text)
        text = text.replace('_', ' ')
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = text.replace(' ', '-')
        return text
