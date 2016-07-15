"""
(C) 2014-2015 Roman Sirokov
Licensed under BSD license

http://github.com/r0x0r/pywebview/
"""

import logging
from webview import OPEN_DIALOG, FOLDER_DIALOG, SAVE_DIALOG

logger = logging.getLogger(__name__)

try:
    # Try GTK 3
    from gi.repository import Gtk as gtk
    from gi.repository import Gdk
    from gi.repository import GLib as glib
    from gi.repository import WebKit as webkit
except ImportError as e:
    import_error = True
    logger.warn("PyGObject is not found", exc_info=True)
else:
    import_error = False


class BrowserView:
    instance = None

    def __init__(self, title, url, width, height, resizable, fullscreen, min_size):
        BrowserView.instance = self

        Gdk.threads_init()
        window = gtk.Window(title=title)

        if resizable:
            window.set_size_request(min_size[0], min_size[1])
            window.resize(width, height)
        else:
            window.set_size_request(width, height)

        window.set_resizable(resizable)
        window.set_position(gtk.WindowPosition.CENTER)

        if fullscreen:
            window.fullscreen()

        window.connect("delete-event", gtk.main_quit)

        scrolled_window = gtk.ScrolledWindow()
        window.add(scrolled_window)

        webview = webkit.WebView()
        webview.props.settings.props.enable_default_context_menu = False
        scrolled_window.add_with_viewport(webview)
        window.show_all()

        if url != None:
            webview.load_uri(url)

        self.window = window
        self.webview = webview

    def show(self):
        Gdk.threads_enter()
        gtk.main()
        Gdk.threads_leave()

    def destroy(self):
        Gdk.threads_enter()
        self.window.destroy()
        Gdk.threads_leave()

    def create_file_dialog(self, dialog_type, directory, allow_multiple, save_filename):
        Gdk.threads_enter()

        if dialog_type == FOLDER_DIALOG:
            gtk_dialog_type = gtk.FileChooserAction.SELECT_FOLDER
            title = "Open folder"
            button = gtk.STOCK_OPEN
        elif dialog_type == OPEN_DIALOG:
            gtk_dialog_type = gtk.FileChooserAction.OPEN
            title = "Open file"
            button = gtk.STOCK_OPEN
        elif dialog_type == SAVE_DIALOG:
            gtk_dialog_type = gtk.FileChooserAction.SAVE
            title = "Save file"
            button = gtk.STOCK_SAVE

        dialog = gtk.FileChooserDialog(title, self.window, gtk_dialog_type,
                                       (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, button, gtk.ResponseType.OK))

        dialog.set_select_multiple(allow_multiple)
        dialog.set_current_folder(directory)

        if dialog_type == SAVE_DIALOG:
            dialog.set_current_name(save_filename)

        response = dialog.run()

        if response == gtk.ResponseType.OK:
            if not allow_multiple or len(dialog.get_filenames()) == 1:
                file_name = dialog.get_filename()
            else:
                file_name = dialog.get_filenames()
        else:
            file_name = None

        dialog.destroy()

        Gdk.threads_leave()

        return file_name

    def load_url(self, url):
        self.webview.load_uri(url)

    def load_string(self, content, mime_type, encoding, base_uri):
        glib.idle_add(self.webview.load_string, content, mime_type, encoding, base_uri)


def create_window(title, url, width, height, resizable, fullscreen, min_size):
    browser = BrowserView(title, url, width, height, resizable, fullscreen, min_size)
    browser.show()


def destroy_window():
    BrowserView.instance.destroy()


def load_url(url):
    BrowserView.instance.load_url(url)

def load_string(content, mime_type, encoding, base_uri=""):
    BrowserView.instance.load_string(content, mime_type, encoding, base_uri)


def create_file_dialog(dialog_type, directory, allow_multiple, save_filename):
    return BrowserView.instance.create_file_dialog(dialog_type, directory, allow_multiple, save_filename)
