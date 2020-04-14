"""Wrapper library for libcmark-gfm and libcmark-gfm-extensions.
Supplies low-level acces to the underlying libaries.
when used directly the caller is responsible for memory management.
(use: node_free, iter_free, parser_free)
"""
import os
import sys

from ctypes import c_int, c_char_p, c_size_t, c_void_p, CDLL

if sys.platform == 'darwin':
    libname = 'libcmark-gfm.dylib'
    extname = 'libcmark-gfm-extensions.dylib'
elif sys.platform == 'win32':
    libname = 'cmark-gfm.dll'
    extname = 'cmark-gfm-extensions.dll'
else:
    libname = 'libcmark-gfm.so'
    extname = 'libcmark-gfm-extensions.so'

here = os.path.dirname(os.path.abspath(__file__))
libpath = os.path.join(here, 'lib/')

lib_cmark = CDLL(os.path.join(libpath, libname))
lib_ext = CDLL(os.path.join(libpath, extname))

EXTENSIONS = [
  'autolink',
  'table',
  'strikethrough',
  'tagfilter',
]

def wrap_ff(lib, func, restype=None, argtypes=None, docstring=None):
    func = lib.__getattr__(func)
    func.restype = restype
    func.argtypes = argtypes
    if docstring is not None:
        func.__doc__ = docstring
    return func

version_string = wrap_ff(
    lib_cmark, 'cmark_version_string',
    restype=c_char_p,
    )

# Parsing
parser_new = wrap_ff(
    lib_cmark, 'cmark_parser_new', 
    restype=c_void_p, 
    argtypes=[c_int]
)

parser_attach_syntax_extension = wrap_ff(
    lib_cmark, 'cmark_parser_attach_syntax_extension',
    restype=c_int,
    argtypes=[c_void_p, c_void_p]
)

parser_get_syntax_extensions = wrap_ff(
    lib_cmark, 'cmark_parser_get_syntax_extensions',
    restype=c_void_p,
    argtypes=[c_void_p]
)

parser_feed = wrap_ff(
    lib_cmark, 'cmark_parser_feed', 
    restype=None, 
    argtypes=[c_void_p, c_char_p, c_size_t]
)

parser_finish = wrap_ff(
    lib_cmark, 'cmark_parser_finish',
    restype=c_void_p,
    argtypes=[c_void_p]
)

parse_document = wrap_ff(
    lib_cmark, 'cmark_parser_finish',
    restype=c_void_p,
    argtypes=[c_char_p, c_int, c_int]
)

parser_free = wrap_ff(
    lib_cmark, 'cmark_parser_free',
    restype=None,
    argtypes=[c_void_p]
)

# Iterator functions
iter_new = wrap_ff(
    lib_cmark, 'cmark_iter_new',
    restype=c_void_p,
    argtypes=[c_void_p]
)

iter_next = wrap_ff(
    lib_cmark, 'cmark_iter_next',
    restype=c_int,
    argtypes=[c_void_p]
)

iter_get_node = wrap_ff(
    lib_cmark, 'cmark_iter_get_node',
    restype=c_void_p,
    argtypes=[c_void_p]
) 

iter_get_event_type = wrap_ff(
    lib_cmark, 'cmark_iter_get_event_type',
    restype=c_int,
    argtypes=[c_void_p]
)

iter_get_root = wrap_ff(
    lib_cmark, 'cmark_iter_get_root',
    restype=c_void_p,
    argtypes=[c_void_p]
)

iter_reset = wrap_ff(
    lib_cmark, 'cmark_iter_reset',
    restype=None,
    argtypes=[c_void_p, c_void_p, c_int]
)

iter_free = wrap_ff(
    lib_cmark, 'cmark_iter_free',
    restype=None,
    argtypes=[c_void_p]
)

# Tree traversal
node_next = wrap_ff(
    lib_cmark, 'cmark_node_next',
    restype=c_void_p,
    argtypes=[c_void_p]
)

node_previous = wrap_ff(
    lib_cmark, 'cmark_node_previous',
    restype=c_void_p,
    argtypes=[c_void_p]
)

node_parent = wrap_ff(
    lib_cmark, 'cmark_node_parent',
    restype=c_void_p,
    argtypes=[c_void_p]
)

node_first_child = wrap_ff(
    lib_cmark, 'cmark_node_first_child',
    restype=c_void_p,
    argtypes=[c_void_p]
)

node_last_child = wrap_ff(
    lib_cmark, 'cmark_node_last_child',
    restype=c_void_p,
    argtypes=[c_void_p]
)

# Creating and destroying nodes
node_new = wrap_ff(
    lib_cmark, 'cmark_node_new',
    restype=c_void_p,
    argtypes=[c_int]
)

# Use find_syntax_extension to get the extension you want
# then use node_new_with_ext to create the custom node.
node_new_with_ext = wrap_ff(
    lib_cmark, 'cmark_node_new_with_ext', 
    restype= c_void_p, 
    argtypes=[c_int, c_void_p]
    )

node_free = wrap_ff(
    lib_cmark, 'cmark_node_free',
    restype=None,
    argtypes=[c_void_p]
)

# Tree manipulation
node_unlink = wrap_ff(
    lib_cmark, 'cmark_node_unlink',
    restype=None,
    argtypes=[c_void_p]
)
node_insert_before = wrap_ff(
    lib_cmark, 'cmark_node_insert_before',
    restype=c_int,
    argtypes=[c_void_p, c_void_p]
)

node_insert_after = wrap_ff(
    lib_cmark, 'cmark_node_insert_after',
    restype=c_int,
    argtypes=[c_void_p, c_void_p]
)

node_append_child = wrap_ff(
    lib_cmark, 'cmark_node_append_child',
    restype=c_int,
    argtypes=[c_void_p, c_void_p]
)

node_prepend_child = wrap_ff(
    lib_cmark, 'cmark_node_prepend_child',
    restype=c_int,
    argtypes=[c_void_p, c_void_p]
)

consolidate_text_nodes = wrap_ff(
    lib_cmark, 'cmark_consolidate_text_nodes',
    restype=None,
    argtypes=[c_void_p]
)

node_replace = wrap_ff(
    lib_cmark, 'cmark_node_replace',
    restype=c_int,
    argtypes=[c_void_p, c_void_p]
)
# Accessors

## Get node type as an integer
node_get_type = wrap_ff(
    lib_cmark, 'cmark_node_get_type',
    restype=c_int,
    argtypes=[c_void_p]
)

## Get string representaion of the node type
node_get_type_string = wrap_ff(
    lib_cmark, 'cmark_node_get_type_string',
    restype=c_char_p,
    argtypes=[c_void_p,]
)

node_get_heading_level = wrap_ff(
    lib_cmark, 'cmark_node_get_heading_level',
    restype=c_int,
    argtypes=[c_void_p]
)

node_set_heading_level = wrap_ff(
    lib_cmark, 'cmark_node_set_heading_level',
    restype=c_int,
    argtypes=[c_void_p, c_int]
)

# This gets the string value of the node
node_get_literal = wrap_ff(
    lib_cmark, 'cmark_node_get_literal',
    restype=c_char_p,
    argtypes=[c_void_p]
)

# This sets the string value of the node
node_set_literal = wrap_ff(
    lib_cmark, 'cmark_node_set_literal',
    restype=c_int,
    argtypes=[c_void_p, c_char_p]
)

# List node operations

## Check whether or not a node is a list and return the list type if it is.
node_get_list_type = wrap_ff(
    lib_cmark, 'cmark_node_get_list_type',
    restype=c_int,
    argtypes=[c_void_p]
)

node_set_list_type = wrap_ff(
    lib_cmark, 'cmark_node_set_list_type',
    restype=c_int,
    argtypes=[c_void_p, c_int]
)

node_get_list_delim = wrap_ff(
    lib_cmark, 'cmark_node_get_list_delim',
    restype=c_int,
    argtypes=[c_void_p]
)

node_set_list_delim = wrap_ff(
    lib_cmark, 'cmark_node_set_list_delim',
    restype=c_int,
    argtypes=[c_void_p, c_int]
)

node_get_list_start = wrap_ff(
    lib_cmark, 'cmark_node_get_list_start',
    restype=c_int,
    argtypes=[c_void_p]
)

node_set_list_start = wrap_ff(
    lib_cmark, 'cmark_node_set_list_start',
    restype=c_int,
    argtypes=[c_void_p, c_int]
)

## gets tightness of list, lakes a node and an int 0 for loose, 1 for tight
node_get_list_tight = wrap_ff(
    lib_cmark, 'cmark_node_get_list_tight',
    restype=c_int,
    argtypes=[c_void_p]
)

## Sets tightness of list, lakes a node and an int 0 for loose, 1 for tight
node_set_list_tight = wrap_ff(
    lib_cmark, 'cmark_node_set_list_tight',
    restype=c_int,
    argtypes=[c_void_p]
)

# Checks if node has a url (when it is either an image or a link)
node_get_url = wrap_ff(
    lib_cmark, 'cmark_node_get_url',
    restype=c_char_p,
    argtypes=[c_void_p]
)

# Set the node url if it is an image or link
node_set_url = wrap_ff(
    lib_cmark, 'cmark_node_set_url',
    restype=c_int,
    argtypes=[c_void_p, c_char_p]
)

# Get title attribute on a node is it is is a link or image
node_get_title = wrap_ff(
    lib_cmark, 'cmark_node_get_title',
    restype=c_char_p,
    argtypes=[c_void_p]
)

# Set title attribute on a node is it is is a link or image
node_set_title = wrap_ff(
    lib_cmark, 'cmark_node_set_title',
    restype=c_int,
    argtypes=[c_void_p, c_char_p]
)

# Returns the info string from a fenced code block
node_get_fence_info = wrap_ff(
    lib_cmark, 'cmark_node_get_fence_info',
    restype=c_char_p,
    argtypes=[c_void_p]
)

# Sets the info string in a fenced code block, returning 1 on success and 0 on failure
node_set_fence_info = wrap_ff(
    lib_cmark, 'cmark_node_set_fence_info',
    restype=c_int,
    argtypes=[c_void_p, c_char_p]
)

# This returns the line number of the node as it was found in the source text
node_get_start_line = wrap_ff(
    lib_cmark, 'cmark_node_get_start_line',
    restype=c_int,
    argtypes=[c_void_p]
)

# This returns the line number on which node ends as it was found in the source text
node_get_end_line = wrap_ff(
    lib_cmark, 'cmark_node_get_end_line',
    restype=c_int,
    argtypes=[c_void_p]
)

# This returns the column on which node starts as it was found in the source text
node_get_start_column = wrap_ff(
    lib_cmark, 'cmark_node_get_start_column',
    restype=c_int,
    argtypes=[c_void_p]
)

# This returns the column on which node ends as it was found in the source text
node_get_end_column= wrap_ff(
    lib_cmark, 'cmark_node_get_end_column',
    restype=c_int,
    argtypes=[c_void_p]
)

# Extensions, gfm specific
find_syntax_extension = wrap_ff(
    lib_cmark, 'cmark_find_syntax_extension',
    restype=c_void_p,
    argtypes=[c_char_p]
)

# Renderers
render_html = wrap_ff(
    lib_cmark, 'cmark_render_html',
    restype=c_char_p,
    argtypes=[c_void_p, c_int, c_void_p]
)

render_xml = wrap_ff(
    lib_cmark, 'cmark_render_xml',
    restype=c_char_p,
    argtypes=[c_void_p, c_int]
)

render_latex = wrap_ff(
    lib_cmark, 'cmark_render_latex',
    restype=c_char_p,
    argtypes=[c_void_p, c_int, c_int]
)

render_man = wrap_ff(
    lib_cmark, 'cmark_render_man',
    restype=c_char_p,
    argtypes=[c_void_p, c_int, c_int]
)

render_commonmark = wrap_ff(
    lib_cmark, 'cmark_render_commonmark',
    restype=c_char_p,
    argtypes=[c_void_p, c_int, c_int]
)

# Set up the libcmark-gfm library and its extensions
register = wrap_ff(
    lib_ext, 'cmark_gfm_core_extensions_ensure_registered'
)
register()

# Constants and options
CMARK_OPT_DEFAULT = 0
CMARK_OPT_SOURCEPOS = 1 << 1
CMARK_OPT_HARDBREAKS = 1 << 2
CMARK_OPT_UNSAFE = 1 << 17
CMARK_OPT_NOBREAKS = 1 << 4
CMARK_OPT_VALIDATE_UTF8 = 1 << 9
CMARK_OPT_SMART = 1 << 10
CMARK_OPT_GITHUB_PRE_LANG = 1 << 11
CMARK_OPT_LIBERAL_HTML_TAG = 1 << 12
CMARK_OPT_FOOTNOTES = 1 << 13
CMARK_OPT_STRIKETHROUGH_DOUBLE_TILDE = 1 << 14
CMARK_OPT_TABLE_PREFER_STYLE_ATTRIBUTES = 1 << 15
CMARK_OPT_FULL_INFO_STRING = 1 << 16


CMARK_NODE_TYPE_PRESENT = 0x8000
CMARK_NODE_TYPE_BLOCK = CMARK_NODE_TYPE_PRESENT | 0x0000
CMARK_NODE_TYPE_INLINE = CMARK_NODE_TYPE_PRESENT | 0x4000
CMARK_NODE_TYPE_MASK = 0xc000
CMARK_NODE_VALUE_MASK = 0x3fff


# Error status
NODE_NONE = 0x0000,
# Block
NODE_DOCUMENT       = CMARK_NODE_TYPE_BLOCK | 0x0001
NODE_BLOCK_QUOTE    = CMARK_NODE_TYPE_BLOCK | 0x0002
NODE_LIST           = CMARK_NODE_TYPE_BLOCK | 0x0003
NODE_ITEM           = CMARK_NODE_TYPE_BLOCK | 0x0004
NODE_CODE_BLOCK     = CMARK_NODE_TYPE_BLOCK | 0x0005
NODE_HTML_BLOCK     = CMARK_NODE_TYPE_BLOCK | 0x0006
NODE_CUSTOM_BLOCK   = CMARK_NODE_TYPE_BLOCK | 0x0007
NODE_PARAGRAPH      = CMARK_NODE_TYPE_BLOCK | 0x0008
NODE_HEADING        = CMARK_NODE_TYPE_BLOCK | 0x0009
NODE_THEMATIC_BREAK = CMARK_NODE_TYPE_BLOCK | 0x000a
NODE_FOOTNOTE_DEFINITION = CMARK_NODE_TYPE_BLOCK | 0x000b
# Inline
NODE_TEXT          = CMARK_NODE_TYPE_INLINE | 0x0001
NODE_SOFTBREAK     = CMARK_NODE_TYPE_INLINE | 0x0002
NODE_LINEBREAK     = CMARK_NODE_TYPE_INLINE | 0x0003
NODE_CODE          = CMARK_NODE_TYPE_INLINE | 0x0004
NODE_HTML_INLINE   = CMARK_NODE_TYPE_INLINE | 0x0005
NODE_CUSTOM_INLINE = CMARK_NODE_TYPE_INLINE | 0x0006
NODE_EMPH          = CMARK_NODE_TYPE_INLINE | 0x0007
NODE_STRONG        = CMARK_NODE_TYPE_INLINE | 0x0008
NODE_LINK          = CMARK_NODE_TYPE_INLINE | 0x0009
NODE_IMAGE         = CMARK_NODE_TYPE_INLINE | 0x000a
NODE_FOOTNOTE_REFERENCE = CMARK_NODE_TYPE_INLINE | 0x000b

# These  need to be pulled from the shared library
NODE_STRIKETHROUGH = c_int.in_dll(lib_ext, 'CMARK_NODE_STRIKETHROUGH')
NODE_TABLE = c_int.in_dll(lib_ext, 'CMARK_NODE_TABLE')
NODE_TABLE_CELL = c_int.in_dll(lib_ext, 'CMARK_NODE_TABLE_CELL')
NODE_TABLE_ROW = c_int.in_dll(lib_ext, 'CMARK_NODE_TABLE_ROW')

# Iterator event types
EVENT_NONE = 0
EVENT_DONE = 1
EVENT_ENTER = 2
EVENT_EXIT = 3

# Lists
CMARK_NO_LIST = 0 
CMARK_BULLET_LIST = 1 
CMARK_ORDERED_LIST = 2

CMARK_NO_DELIM = 0
CMARK_PERIOD_DELIM = 1
CMARK_PAREN_DELIM = 2

