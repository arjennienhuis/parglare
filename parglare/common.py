# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
from parglare.termui import s_attention as _a

if sys.version < '3':
    text = unicode  # NOQA
else:
    text = str


class Location(object):
    """
    Represents a location (point or span) of the object in the source code.

    Args:
    context(Context): Parsing context used to populate this object.
    file_name(str): File name where this location is to be found.
        Takes precendence over `file_name` given in `context`.
    start_position(int): The beginning of the location.
        Takes precendence over `start_position` given in `context`.
    end_position(int): The end of the location.
        Takes precendence over `end_position` given in `context`.
    input_str(str): String representing textual content of the file being
        parsed.
        Takes precendence over `input_str` given in `context`.
    """

    __slots__ = ['file_name', 'start_position', 'end_position', 'line',
                 'column', 'input_str']

    def __init__(self, context=None, file_name=None, start_position=None,
                 end_position=None, input_str=None):

        if not context:
            self.file_name = file_name
            self.start_position = start_position
            self.end_position = end_position
            self.input_str = input_str
        else:
            self.file_name = file_name if file_name else context.file_name
            self.start_position = start_position \
                if start_position is not None else context.start_position
            self.end_position = end_position \
                if end_position is not None else context.end_position
            self.input_str = input_str \
                if input_str is not None else context.input_str

        # Evaluate this only when string representation is needed.
        # E.g. during error reporting
        self.line = None
        self.column = None

    def __str__(self):
        if self.input_str and self.start_position is not None:
            from parglare.parser import pos_to_line_col
            line, col = pos_to_line_col(self.input_str,
                                        self.start_position)
            self.line = line
            self.column = col
            return _a('{}{}:{}:"{}" => '
                      .format("{}:".format(self.file_name)
                              if self.file_name else "",
                              line, col,
                              position_context(
                                  self.input_str,
                                  self.start_position)))
        elif self.file_name:
            return _a('{} => '.format(self.file_name))
        else:
            return "<Unknown location>"


def position_context(input_str, position):
    """
    Returns position context string.
    """
    start = max(position-10, 0)
    c = text(input_str[start:position]) + _a("*") \
        + text(input_str[position:position+10])
    c = c.replace("\n", "\\n")
    return c


def load_python_module(mod_name, mod_path):
    """
    Loads Python module from an arbitrary location.
    See https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path  # noqa
    """
    if sys.version_info >= (3, 5):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            mod_name, mod_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    elif sys.version_info >= (3, 3):
        from importlib.machinery import SourceFileLoader
        module = SourceFileLoader(
            mod_name, mod_path).load_module()
    else:
        import imp
        module = imp.load_source(mod_name, mod_path)

    return module


def get_collector():
    """
    Produces action/recognizers collector/decorator that will collect all
    decorated objects under dictionary attribute `all`.
    """
    all = {}

    class Collector(object):
        def __call__(self, name_or_f=None):
            """
            If called with action/recognizer name return decorator.
            If called over function apply decorator.
            """
            an = {0: name_or_f}

            def decorator(f):
                if isinstance(an[0], text):
                    name = an[0]
                else:
                    name = f.__name__
                objects = all.get(name, None)
                if objects:
                    if type(objects) is list:
                        objects.append(f)
                    else:
                        all[name] = [objects, f]
                else:
                    all[name] = f
                return f
            if name_or_f is None or type(name_or_f) is text:
                return decorator
            else:
                return decorator(name_or_f)

    objects = Collector()
    objects.all = all
    return objects
