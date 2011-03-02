import sys, os, re
SAGE_ROOT = os.environ['SAGE_ROOT']
SAGE_DOC = os.path.join(SAGE_ROOT, 'devel/sage/doc')

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath(os.path.join(SAGE_DOC, 'common')))

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sage_autodoc',  'sphinx.ext.graphviz',
              'sphinx.ext.inheritance_diagram']
#, 'sphinx.ext.intersphinx', 'sphinx.ext.extlinks']

if 'SAGE_DOC_JSMATH' in os.environ:
    extensions.append('sphinx.ext.jsmath')
else:
    extensions.append('sphinx.ext.pngmath')
jsmath_path = 'jsmath_sage.js'

# Add any paths that contain templates here, relative to this directory.
templates_path = [os.path.join(SAGE_DOC, 'common/templates'), 'templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u""
copyright = u'2005--2011, The Sage Development Team'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
from sage.version import version
release = version

#version = '3.1.2'
# The full version, including alpha/beta/rc tags.
#release = '3.1.2'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directory, that shouldn't be searched
# for source files.
exclude_trees = ['.build']

# The reST default role (used for this markup: `text`) to use for all documents.
default_role = 'math'

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.  NOTE:
# This overrides a HTML theme's corresponding setting (see below).
pygments_style = 'sphinx'

# GraphViz includes dot, neato, twopi, circo, fdp.
graphviz_dot = 'dot'
inheritance_graph_attrs = { 'rankdir' : 'BT' }
inheritance_node_attrs = { 'height' : 0.5, 'fontsize' : 12, 'shape' : 'oval' }
inheritance_edge_attrs = {}

# Sage trac ticket shortcuts. For example, :ticket:`7549` .
#extlinks = {'ticket': ('http://trac.sagemath.org/sage_trac/ticket/', 'Ticket ')}

# Options for HTML output
# -----------------------

# HTML theme (e.g., 'default', 'sphinxdoc').  We use a custom Sage
# theme to set a Pygments style, stylesheet, and insert jsMath macros. See
# the directory doc/common/themes/sage/ for files comprising the custom Sage
# theme.
html_theme = 'sage'

# Theme options are theme-specific and customize the look and feel of
# a theme further.  For a list of options available for each theme,
# see the documentation.
html_theme_options = {}

if 'SAGE_DOC_JSMATH' in os.environ:
    from sage.misc.latex_macros import sage_jsmath_macros_easy
    html_theme_options['jsmath_macros'] = sage_jsmath_macros_easy

    from sage.misc.package import is_package_installed
    html_theme_options['jsmath_image_fonts'] = is_package_installed('jsmath-image-fonts')

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [os.path.join(SAGE_DOC, 'common/themes')]

# HTML style sheet NOTE: This overrides a HTML theme's corresponding
# setting.
#html_style = 'default.css'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (within the static path) to place at the top of
# the sidebar.
#html_logo = 'sagelogo-word.ico'

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = 'favicon.ico'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [os.path.join(SAGE_DOC, 'common/static'), 'static']

# If we're using jsMath, we prepend its location to the static path
# array.  We can override / overwrite selected files by putting them
# in the remaining paths.
if 'SAGE_DOC_JSMATH' in os.environ:
    from pkg_resources import Requirement, working_set
    sagenb_path = working_set.find(Requirement.parse('sagenb')).location
    jsmath_static = os.path.join(sagenb_path, 'sagenb', 'data', 'jsmath')
    html_static_path.insert(0, jsmath_static)

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = True

# If true, the reST sources are included in the HTML build as _sources/<name>.
#html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
#htmlhelp_basename = ''

# Cross-links to other project's online documentation.
#intersphinx_mapping = {'http://docs.python.org/dev': None}

# Options for LaTeX output
# ------------------------
# See http://sphinx.pocoo.org/config.html#confval-latex_elements
latex_elements = {}

# Extended UTF-8 scheme
latex_elements['inputenc'] = '\\usepackage[utf8x]{inputenc}'

# Prevent Sphinx from by default inserting the following LaTeX
# declaration into the preamble of a .tex file:
#
# \DeclareUnicodeCharacter{00A0}{\nobreakspace}
#
# This happens in the file src/sphinx/writers/latex.py in the sphinx
# spkg.  This declaration is known to result in a failure to build the
# PDF version of a document in the Sage standard documentation. See
# ticket #8183 for further information on this issue.
latex_elements['utf8extra'] = ''

# The paper size ('letterpaper' or 'a4paper').
#latex_elements['papersize'] = 'letterpaper'

# The font size ('10pt', '11pt' or '12pt').
#latex_elements['pointsize'] = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = []

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = 'sagelogo-word.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
latex_elements['preamble'] = '\usepackage{amsmath}\n\usepackage{amssymb}\n'

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True

#####################################################
# add LaTeX macros for Sage

from sage.misc.latex_macros import sage_latex_macros

try:
    pngmath_latex_preamble  # check whether this is already defined
except NameError:
    pngmath_latex_preamble = ""

for macro in sage_latex_macros:
    # used when building latex and pdf versions
    latex_elements['preamble'] += macro + '\n'
    # used when building html version
    pngmath_latex_preamble += macro + '\n'

#####################################################

def process_docstring_aliases(app, what, name, obj, options, docstringlines):
    """
    Change the docstrings for aliases to point to the original object.
    """
    basename = name.rpartition('.')[2]
    if hasattr(obj, '__name__') and obj.__name__ != basename:
        docstringlines[:] = ['See :obj:`%s`.' % name]

def process_directives(app, what, name, obj, options, docstringlines):
    """
    Remove 'nodetex' and other directives from the first line of any
    docstring where they appear.
    """
    if len(docstringlines) == 0:
        return
    first_line = docstringlines[0]
    directives = [ d.lower() for d in first_line.split(',') ]
    if 'nodetex' in directives:
        docstringlines.pop(0)

def process_docstring_cython(app, what, name, obj, options, docstringlines):
    """
    Remove Cython's filename and location embedding.
    """
    if len(docstringlines) <= 1:
        return

    first_line = docstringlines[0]
    if first_line.startswith('File:') and '(starting at' in first_line:
        #Remove the first two lines
        docstringlines.pop(0)
        docstringlines.pop(0)

def process_docstring_module_title(app, what, name, obj, options, docstringlines):
    """
    Removes the first line from the beginning of the module's docstring.  This
    corresponds to the title of the module's documentation page.
    """
    if what != "module":
        return

    #Remove any additional blank lines at the beginning
    title_removed = False
    while len(docstringlines) > 1 and not title_removed:
        if docstringlines[0].strip() != "":
            title_removed = True
        docstringlines.pop(0)

    #Remove any additional blank lines at the beginning
    while len(docstringlines) > 1:
        if docstringlines[0].strip() == "":
            docstringlines.pop(0)
        else:
            break

skip_picklability_check_modules = [
    #'sage.misc.nested_class_test', # for test only
    'sage.misc.latex',
    'sage.misc.explain_pickle',
    '__builtin__',
]

def check_nested_class_picklability(app, what, name, obj, skip, options):
    """
    Print a warning if pickling is broken for nested classes.
    """
    import types
    if hasattr(obj, '__dict__') and hasattr(obj, '__module__'):
        # Check picklability of nested classes.  Adapted from
        # sage.misc.nested_class.modify_for_nested_pickle.
        module = sys.modules[obj.__module__]
        for (nm, v) in obj.__dict__.iteritems():
            if (isinstance(v, (type, types.ClassType)) and
                v.__name__ == nm and
                v.__module__ == module.__name__ and
                getattr(module, nm, None) is not v and
                v.__module__ not in skip_picklability_check_modules):
                # OK, probably this is an *unpicklable* nested class.
                app.warn('Pickling of nested class %r is probably broken. '
                         'Please set __metaclass__ of the parent class to '
                         'sage.misc.nested_class.NestedClassMetaclass.' % (
                        v.__module__ + '.' + name + '.' + nm))

def skip_member(app, what, name, obj, skip, options):
    """
    To suppress Sphinx warnings / errors, we

    - Don't include [aliases of] builtins.

    - Don't include the docstring for any nested class which has been
      inserted into its module by
      :class:`sage.misc.NestedClassMetaclass` only for pickling.  The
      class will be properly documented inside its surrounding class.

    - Don't include
      sagenb.notebook.twist.userchild_download_worksheets.zip.

    - Optionally, check whether pickling is broken for nested classes.

    - Optionally, include objects whose name begins with an underscore
      ('_'), i.e., "private" or "hidden" attributes, methods, etc.

    Otherwise, we abide by Sphinx's decision.  Note: The object
    ``obj`` is excluded (included) if this handler returns True
    (False).
    """
    if 'SAGE_CHECK_NESTED' in os.environ:
        check_nested_class_picklability(app, what, name, obj, skip, options)

    if getattr(obj, '__module__', None) == '__builtin__':
        return True

    if (hasattr(obj, '__name__') and obj.__name__.find('.') != -1 and
        obj.__name__.split('.')[-1] != name):
        return True

    if name.find("userchild_download_worksheets.zip") != -1:
        return True

    if 'SAGE_DOC_UNDERSCORE' in os.environ:
        if name.split('.')[-1].startswith('_'):
            return False

    return skip

def process_dollars(app, what, name, obj, options, docstringlines):
    r"""
    Replace dollar signs with backticks.
    See sage.misc.sagedoc.process_dollars for more information
    """
    if len(docstringlines) > 0 and name.find("process_dollars") == -1:
        from sage.misc.sagedoc import process_dollars as sagedoc_dollars
        s = sagedoc_dollars("\n".join(docstringlines))
        lines = s.split("\n")
        for i in range(len(lines)):
            docstringlines[i] = lines[i]

def process_mathtt(app, what, name, obj, options, docstringlines):
    r"""
    Replace \mathtt{BLAH} with \verb|BLAH| if using jsMath.
    See sage.misc.sagedoc.process_mathtt for more information
    """
    if (len(docstringlines) > 0 and 'SAGE_DOC_JSMATH' in os.environ
        and name.find("process_mathtt") == -1):
        from sage.misc.sagedoc import process_mathtt as sagedoc_mathtt
        s = sagedoc_mathtt("\n".join(docstringlines), True)
        lines = s.split("\n")
        for i in range(len(lines)):
            docstringlines[i] = lines[i]

def process_inherited(app, what, name, obj, options, docstringlines):
    """
    If we're including inherited members, omit their docstrings.
    """
    if not options.get('inherited-members'):
        return

    if what in ['class', 'data', 'exception', 'function', 'module']:
        return

    name = name.split('.')[-1]

    if what == 'method' and hasattr(obj, 'im_class'):
        if name in obj.im_class.__dict__.keys():
            return

    if what == 'attribute' and hasattr(obj, '__objclass__'):
        if name in obj.__objclass__.__dict__.keys():
            return

    for i in xrange(len(docstringlines)):
        docstringlines.pop()

from sage.misc.sageinspect import sage_getargspec
autodoc_builtin_argspec = sage_getargspec

def setup(app):
    app.connect('autodoc-process-docstring', process_docstring_cython)
    app.connect('autodoc-process-docstring', process_directives)
    app.connect('autodoc-process-docstring', process_docstring_module_title)
    app.connect('autodoc-process-docstring', process_dollars)
    app.connect('autodoc-process-docstring', process_mathtt)
    app.connect('autodoc-process-docstring', process_inherited)
    app.connect('autodoc-skip-member', skip_member)
