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

FTSINDEX = _config.getboolean('ui', 'default_ftsindex')

SYNCRONIZE_TIME = _config.getboolean('time', 'syncronize')
SYNCRONIZE_SERVER = _config.get('time', 'syncronize_server')
SERVER_TIME_FORMAT = _config.get('time', 'server_time_format')

MULTIPROCESS = _config.getboolean('multiprocessing', 'multiprocess')
GRID_LINES = _config.getboolean('table', 'grid_default')
FILL_LOGSTREE_AT_START = _config.getboolean('tree', 'fill_at_start')

EXT_CONFIG_EDITOR = _config.get('config_editor', 'external_config_editor')
EXTERNAL_LOG_VIEWER = _config.get('logwindow', 'external_log_viewer')

DEFAULT_WHERE_OPERATOR = _config.get('query', 'default_where_operator_fts')
DEFAULT_WHERE_OPERATOR_FTS = _config.get('query', 'default_where_operator_fts')

QUERIES_FILE = get_path(_config.get("config_files", 'queries'))
