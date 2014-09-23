import os
import importlib

SETTINGS_MODULE = os.environ.get('JELLYRISK_SETTINGS_MODULE', 'settings')
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

try:
    mod = importlib.import_module(SETTINGS_MODULE)
except ImportError as e:
    raise ImportError("Could not import settings '%s' (Is it on sys.path?): %s" % (SETTINGS_MODULE, e))

settings = mod

# defaults
settings.LIMIT_ROWS = getattr(settings, 'SETTINGS_LIMIT_ROWS', 15000)
settings.LONG_MIN = getattr(settings, 'LONG_MIN', '-2')
settings.LONG_MAX = getattr(settings, 'LONG_MAX', '4')
settings.LAT_MIN = getattr(settings, 'LAT_MIN', '38')
settings.LAT_MAX = getattr(settings, 'LAT_MAX', '44')
settings.DEPTH_MIN = getattr(settings, 'DEPTH_MIN', '1.4721')
settings.DEPTH_MAX = getattr(settings, 'DEPTH_MAX', '4.58748')
