import ConfigParser
import os
from urlparse import urlunparse
import sys

_config_dir = "config"

def get_path(path):
    if not os.path.dirname(path):
        return os.path.abspath(os.path.join(_config_dir, path))
    else:
        return os.path.abspath(path)

app_path = os.path.dirname(os.path.abspath(__file__))

_config = ConfigParser.RawConfigParser()
_config.read(os.path.join(_config_dir, "logsbrowser.cfg"))

SQL_URI = _config.get("db", 'sql_uri')
COLOR_RECT_WIDTH = _config.getint("colors", 'color_rectangle_width')
BOLD_SELECTED = _config.getboolean("colors", 'bold_selected')

SYNTAX_CFG = get_path(_config.get("config_files", 'syntax'))
SOURCES_XML = get_path(_config.get("config_files", 'sources_xml'))
SELECTS = get_path(_config.get("config_files", 'selects'))
QUERIES_FILE = get_path(_config.get("config_files", 'queries'))

PROGRAM_CONFIG_EDITOR = _config.get("config_editors", 'program')
SOURCES_XML_EDITOR = _config.get("config_editors", 'sources_xml')
SELECTS_EDITOR = _config.get("config_editors", 'selects')
QUERIES_FILE_EDITOR = _config.get("config_editors", 'queries')

FTSINDEX = _config.getboolean('ui', 'default_ftsindex')

SYNCRONIZE_TIME = _config.getboolean('time', 'synchronize')
SYNCRONIZE_SERVER = _config.get('time', 'synchronize_server')
SERVER_TIME_FORMAT = _config.get('time', 'server_time_format')

MULTIPROCESS = _config.getboolean('multiprocessing', 'multiprocess')
XMLRPC = _config.getboolean('rpc', 'enable_xml_rpc')
RPC_PORT = _config.getint('rpc', 'xml_rpc_port')
GRID_LINES = _config.getboolean('table', 'grid_default')

EXTERNAL_LOG_VIEWER = _config.get('logwindow', 'external_log_viewer')

HELP_INDEX = os.path.realpath(_config.get("docs", 'doc_index_file'))

MAX_LINES_FOR_DETECT_FORMAT = _config.getint('parse_files', 'max_lines_for_detect_format')

WIDTH_MAIN_WINDOW = _config.getint('window_size', 'width_main_window')
HEIGHT_MAIN_WINDOW = _config.getint('window_size', 'height_main_window')
WIDTH_LOG_WINDOW = _config.getint('window_size', 'width_log_window')
HEIGHT_LOG_WINDOW = _config.getint('window_size', 'height_log_window')
