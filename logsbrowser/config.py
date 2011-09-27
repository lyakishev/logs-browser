import ConfigParser
import os

_config_dir = "config"

def get_path(path):
    if not os.path.dirname(path):
        return os.path.abspath(os.path.join(_config_dir, path))
    else:
        return os.path.abspath(path)

_config = ConfigParser.RawConfigParser()
_config.read(os.path.join(_config_dir, "logsbrowser.cfg"))

SQL_URI = _config.get("db", 'sql_uri')
BLINK_MS = _config.getint("colors", 'blink_ms')
COLOR_RECT_WIDTH = _config.getint("colors", 'color_rectangle_width')
BOLD_SELECTED = _config.getboolean("colors", 'bold_selected')

FLOGS_CFG = get_path(_config.get("config_files", 'file_logs'))
ELOGS_CFG = get_path(_config.get("config_files", 'event_logs'))
SYNTAX_CFG = get_path(_config.get("config_files", 'syntax'))
SOURCES_XML = get_path(_config.get("config_files", 'sources_xml'))
SELECTS = get_path(_config.get("config_files", 'selects'))

FTSINDEX = _config.getboolean('ui', 'default_ftsindex')

SYNCRONIZE_TIME = _config.getboolean('time', 'syncronize')
SYNCRONIZE_SERVER = _config.get('time', 'syncronize_server')
SERVER_TIME_FORMAT = _config.get('time', 'server_time_format')

MULTIPROCESS = _config.getboolean('multiprocessing', 'multiprocess')
XMLRPC = _config.getboolean('rpc', 'enable_xml_rpc')
RPC_PORT = _config.getint('rpc', 'xml_rpc_port')
GRID_LINES = _config.getboolean('table', 'grid_default')
FILL_LOGSTREE_AT_START = _config.getboolean('tree', 'fill_at_start')

EXT_CONFIG_EDITOR = _config.get('config_editor', 'external_config_editor')
EXTERNAL_LOG_VIEWER = _config.get('logwindow', 'external_log_viewer')

DEFAULT_WHERE_OPERATOR = _config.get('query', 'default_where_operator')
DEFAULT_WHERE_OPERATOR_FTS = _config.get('query', 'default_where_operator_fts')

QUERIES_FILE = get_path(_config.get("config_files", 'queries'))

HELP_INDEX = _config.get("docs", 'doc_index_file')
MAX_LINES_FOR_DETECT_FORMAT = _config.getint('parse_files', 'max_lines_for_detect_format')

WIDTH_MAIN_WINDOW = _config.getint('window_size', 'width_main_window')
HEIGHT_MAIN_WINDOW = _config.getint('window_size', 'height_main_window')
WIDTH_LOG_WINDOW = _config.getint('window_size', 'width_log_window')
HEIGHT_LOG_WINDOW = _config.getint('window_size', 'height_log_window')
