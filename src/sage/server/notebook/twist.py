"""
SAGE Notebook (Twisted Version)
"""
import os

from twisted.web2 import server, http, resource, channel
from twisted.web2 import static, http_headers, responsecode

import css, js, keyboards

from sage.misc.misc import SAGE_EXTCODE, walltime

css_path        = SAGE_EXTCODE + "/notebook/css/"
image_path      = SAGE_EXTCODE + "/notebook/images/"
javascript_path = SAGE_EXTCODE + "/notebook/javascript/"

_cols = None
def word_wrap_cols():
    global _cols
    if _cols is None:
        _cols = notebook.defaults()['word_wrap_cols']
    return _cols

############################
# Encoding data to go between the server and client
############################
SEP = '___S_A_G_E___'

def encode_list(v):
    return SEP.join([str(x) for x in v])

############################
# Notebook autosave.
############################
# save if make a change to notebook and at least some seconds have elapsed since last save.
save_interval = 10
last_time = walltime()

def notebook_save_check():
    global last_time
    t = walltime()
    if t > last_time + save_interval:
        notebook.save()
        last_time = t

######################################################################################
# RESOURCES
######################################################################################

############################
# Create a SAGE worksheet from a latex2html'd file
############################
from docHTMLProcessor import DocHTMLProcessor

def doc_worksheet():
    wnames = notebook.worksheet_names()
    name = 'doc_browser_0'
    if name in wnames:
        W = notebook.get_worksheet_with_name(name)
        W.restart_sage()
        W.clear()
        return W
    else:
        return notebook.create_new_worksheet(name)

class WorksheetFile(resource.Resource):
    addSlash = False

    def __init__(self, path):
        self.docpath = path

    def render(self, ctx=None):
        # Create a live SAGE worksheet out of self.path and render it.
        doc_page_html = open(self.docpath).read()
        directory = os.path.split(self.docpath)[0]
        doc_page, css_href = DocHTMLProcessor().process_doc_html(DOC,
                               directory, doc_page_html)
        if css_href:
            css_href = DOC + directory + css_href
        W = doc_worksheet()
        W.edit_save(doc_page)
        s = notebook.html(worksheet_id = W.name())
        return http.Response(stream=s)

    def childFactory(self, request, name):
        path = self.docpath + '/' + name
        if name.endswith('.html'):
            return WorksheetFile(path)
        else:
            return static.File(path)

############################
# The documentation browsers
############################

DOC = os.path.abspath(os.environ['SAGE_ROOT'] + '/doc/')
class DocStatic(resource.Resource):
    addSlash = True
    def render(self, ctx):
        return static.File('%s/index.html'%DOC)

    def childFactory(self, request, name):
        return static.File('%s/%s'%(DOC,name))

class DocLive(resource.Resource):
    addSlash = True

    def render(self, ctx):
        return static.File('%s/index.html'%DOC)

    def childFactory(self, request, name):
        return WorksheetFile('%s/%s'%(DOC,name))

class Doc(resource.Resource):
    addSlash = True
    child_static = DocStatic()
    child_live = DocLive()

    def render(self, ctx):
        s = """
        <h1><font color="darkred">SAGE Documentation</font></h1>
        <br><br><br>
        <font size=+3>
        <a href="static">Static Documentation</a><br><br>
        <a href="live">Interactive Live Documentation</a><br>
        </font>
        """
        return http.Response(stream=s)

############################
# A resource attached to a given worksheet
############################
class WorksheetResource:
    def __init__(self, name):
        self.name = name
        try:
            self.worksheet = notebook.get_worksheet_with_id(name)
        except KeyError:
            # TODO: This should ask if you are sure, require authentication, etc.
            self.worksheet = notebook.create_new_worksheet(name)

    def id(self, ctx):
        return int(ctx.args['id'][0])

###############################################
# Worksheet data -- a file that
# is associated with a cell in some worksheet.
# The file is stored on the filesystem.
#      /ws/worksheet_name/data/cell_number/filename
##############################################
class CellData(resource.Resource):
    def __init__(self, worksheet, number):
        self.worksheet = worksheet
        self.number = number

    def childFactory(self, request, name):
        dir = self.worksheet.directory()
        path = '%s/cells/%s/%s'%(dir, self.number, name)
        return static.File(path)

class Worksheet_data(WorksheetResource, resource.Resource):
    def childFactory(self, request, number):
        return CellData(self.worksheet, number)

########################################################
# Edit the entire worksheet
########################################################
class Worksheet_edit(WorksheetResource, resource.Resource):
    """
    Return a window that allows the user to edit the text of the
    worksheet with the given filename.
    """
    def render(self, ctx):
        return http.Response(stream = notebook.edit_window(self.worksheet))

class Worksheet_save(WorksheetResource, resource.PostableResource):
    """
    Return a window that allows the user to edit the text of the
    worksheet with the given filename.
    """
    def render(self, ctx):
        if ctx.args.has_key('button_save'):
            self.worksheet.edit_save(ctx.args['textfield'][0])
        s = notebook.html(worksheet_id = self.name)
        return http.Response(stream=s)

########################################################
# Set output type of a cell
########################################################
class Worksheet_set_cell_output_type(WorksheetResource, resource.PostableResource):
    """
    Set the output type of the cell.

    This enables the type of output cell, such as to allowing wrapping
    for output that is very long.
    """
    def render(self, ctx):
        id = self.id(ctx)
        typ = ctx.args['type'][0]
        W = self.worksheet
        W.get_cell_with_id(id).set_cell_output_type(typ)
        return http.Response(stream = '')

########################################################
# The new cell command: /ws/worksheet/new_cell?id=number
########################################################
class Worksheet_new_cell(WorksheetResource, resource.PostableResource):
    """
    Adds a new cell before a given cell.
    """
    def render(self, ctx):
        id = self.id(ctx)
        cell = self.worksheet.new_cell_before(id)
        s = encode_list([cell.id(), cell.html(div_wrap=False), id])
        return http.Response(stream = s)

########################################################
# The delete cell command: /ws/worksheet/delete_cell?id=number
########################################################
class Worksheet_delete_cell(WorksheetResource, resource.PostableResource):
    """
    Deletes a notebook cell.

    If there is only one cell left in a given worksheet, the request
    to delete that cell is ignored because there must be a least one
    cell at all times in a worksheet.  (This requirement exists so
    other functions that evaluate relative to existing cells will
    still work, and so one can add new cells.)
    """
    def render(self, ctx):
        id = self.id(ctx)
        W = self.worksheet
        if len(W) <= 1:
            s = 'ignore'
        else:
            prev_id = W.delete_cell_with_id(id)
            s = encode_list(['delete', id, prev_id, W.cell_id_list()])
        return http.Response(stream = s)

############################
# Get the latest update on output appearing
# in a given output cell.
############################
class Worksheet_cell_update(WorksheetResource, resource.PostableResource):
    def render(self, ctx):
        id = self.id(ctx)

        worksheet = self.worksheet

        # update the computation one "step".
        worksheet.check_comp()

        # now get latest status on our cell
        status, cell = worksheet.check_cell(id)

        if status == 'd':
            new_input = cell.changed_input_text()
            out_html = cell.output_html()
        else:
            new_input = ''
            out_html = ''

        if cell.interrupted():
            inter = 'true'
        else:
            inter = 'false'

        raw = cell.output_text(raw=True).split("\n")
        if "Unhandled SIGSEGV" in raw:
            inter = 'restart'
            print "Segmentation fault detected in output!"

        msg = '%s%s %s'%(status, cell.id(),
                       encode_list([cell.output_text(html=True),
                                    cell.output_text(word_wrap_cols(), html=True),
                                    out_html,
                                    new_input,
                                    inter,
                                    cell.introspect_html()]))

        # There may be more computations left to do, so start one if there is one.
        worksheet.start_next_comp()

        return http.Response(stream=msg)

class Worksheet_eval(WorksheetResource, resource.PostableResource):
    """
    Evaluate a worksheet cell.

    If the request is not authorized, (the requester did not enter the
    correct password for the given worksheet), then the request to
    evaluate or introspect the cell is ignored.

    If the cell contains either 1 or 2 question marks at the end (not
    on a comment line), then this is interpreted as a request for
    either introspection to the documentation of the function, or the
    documentation of the function and the source code of the function
    respectively.
    """
    def render(self, ctx):
        newcell = int(ctx.args['newcell'][0])  # whether to insert a new cell or not
        id = self.id(ctx)
        if not ctx.args.has_key('input'):
            input_text = ''
        else:
            input_text = ctx.args['input'][0]
            input_text = input_text.replace('\r\n', '\n')   # DOS

        W = self.worksheet
        cell = W.get_cell_with_id(id)
        cell.set_input_text(input_text)
        cell.evaluate()

        if cell.is_last():
            new_cell = W.append_new_cell()
            s = encode_list([new_cell.id(), 'append_new_cell', new_cell.html(div_wrap=False)])
        elif newcell:
            new_cell = W.new_cell_after(id)
            s = encode_list([new_cell.id(), 'insert_cell', new_cell.html(div_wrap=False), str(id)])
        else:
            s = encode_list([cell.next_id(), 'no_new_cell', str(id)])

        notebook_save_check()
        return http.Response(stream=s)

class Worksheet_restart_sage(WorksheetResource, resource.Resource):
    def render(self, ctx):
        # TODO -- this must not block long (!)
        self.worksheet.restart_sage()
        return http.Response(stream='done')

class Worksheet_interrupt(WorksheetResource, resource.Resource):
    def render(self, ctx):
        # TODO -- this must not block long (!)
        s = self.worksheet.interrupt()
        return http.Response(stream='ok' if s else 'failed')

class Worksheet_plain(WorksheetResource, resource.Resource):
    def render(self, ctx):
        s = notebook.plain_text_worksheet_html(self.name)
        return http.Response(stream=s)

class Worksheet_print(WorksheetResource, resource.Resource):
    def render(self, ctx):
        s = notebook.worksheet_html(self.name)
        return http.Response(stream=s)

class Worksheet(WorksheetResource, resource.Resource):
    addSlash = True

    def render(self, ctx):
        s = notebook.html(worksheet_id = self.name)
        self.worksheet.sage()
        return http.Response(stream=s)

    def childFactory(self, request, op):
        notebook_save_check()
        try:
            R = globals()['Worksheet_%s'%op]
            return R(self.name)
        except NameError:
            return None, ()

class Worksheets(resource.Resource):
    def childFactory(self, request, name):
        return Worksheet(name)

############################
# Adding a new worksheet
############################

class AddWorksheet(resource.Resource):
    def render(self, ctx):
        name = ctx.args['name'][0]
        W = notebook.create_new_worksheet(name)
        v = notebook.worksheet_list_html(W.name())
        return http.Response(stream = encode_list([v, W.name()]))

class Notebook(resource.Resource):
    child_add_worksheet = AddWorksheet()

############################

class Help(resource.Resource):
    def render(self, ctx):
        try:
            s = self._cache
        except AttributeError:
            s = notebook.help_window()
            self._cache = s
        return http.Response(stream=s)

############################

############################

class History(resource.Resource):
    def render(self, ctx):
        s = notebook.history_html()
        return http.Response(stream=s)

############################

class Main_css(resource.Resource):
    def render(self, ctx):
        s = css.css()
        return http.Response(stream=s)

class CSS(resource.Resource):
    def childFactory(self, request, name):
        return static.File(css_path + "/" + name)

setattr(CSS, 'child_main.css', Main_css())

############################

############################
# Javascript resources
############################

class Main_js(resource.Resource):
    def render(self, ctx):
        s = js.javascript()
        return http.Response(stream=s)

class Keyboard_js_specific(resource.Resource):
    def __init__(self, browser_os):
        self.s = keyboards.get_keyboard(browser_os)

    def render(self, ctx):
        return http.Response(stream = self.s)

class Keyboard_js(resource.Resource):
    def childFactory(self, request, browser_os):
        return Keyboard_js_specific(browser_os)

class Javascript(resource.Resource):
    child_keyboard = Keyboard_js()

    def childFactory(self, request, name):
        return static.File(javascript_path + "/" + name)

setattr(Javascript, 'child_main.js', Main_js())

############################
# Image resource
############################

class Images(resource.Resource):
    def childFactory(self, request, name):
        return static.File(image_path + "/" + name)

############################

class Toplevel(resource.Resource):
    addSlash = True

    child_images = Images()
    child_javascript = Javascript()
    child_css = CSS()
    child_ws = Worksheets()
    child_notebook = Notebook()
    child_doc = Doc()

    def render(self, ctx):
        s = notebook.html()
        return http.Response(stream=s)

    def childFactory(self, request, name):
        print request, name

setattr(Toplevel, 'child_help.html', Help())
setattr(Toplevel, 'child_history.html', History())

site = server.Site(Toplevel())
notebook = None  # this gets set on startup.

##########################################################
# This actually serves up the notebook.
  ##########################################################

from   sage.server.misc import print_open_msg
import os, socket

def notebook_twisted(directory='sage_notebook',
             port=8000,
             address='localhost',
             port_tries=1,
             multisession=True,
             jsmath      =True):
    r"""
    Experimental twisted version of the SAGE Notebook.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    port = int(port)
    conf = '%s/twistedconf.py'%directory

    def run(port):
        ## Create the config file
        config = open(conf, 'w')
        config.write("""

import sage.server.notebook.notebook
sage.server.notebook.notebook.JSMATH=%s
import sage.server.notebook.notebook as notebook
import sage.server.notebook.twist as twist
twist.notebook = notebook.load_notebook('%s')
import sage.server.notebook.worksheet as worksheet
worksheet.init_sage_prestart()
worksheet.multisession = %s

import signal, sys
def my_sigint(x, n):
    twist.notebook.save()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    print "(Notebook cleanly saved. Press control-C again to exit.)"

signal.signal(signal.SIGINT, my_sigint)

from twisted.web2 import channel
from twisted.application import service, strports
application = service.Application("SAGE Notebook")
s = strports.service('tcp:%s', channel.HTTPFactory(twist.site))
s.setServiceParent(application)
"""%(jsmath, os.path.abspath(directory), multisession, port))
        config.close()

        ## Start up twisted
        print_open_msg(address, port)
        e = os.system('cd "%s" && sage -twistd -ny twistedconf.py'%directory)
        if e == 256:
            raise socket.error

    for i in range(int(port_tries)):
        try:
            run(port + i)
        except socket.error:
            print "Port %s is already in use.  Trying next port..."%port
        else:
            break

    return True
