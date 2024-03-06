
import logging.config

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'jsonFormatter': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'jsonFormatter',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'jsonFormatter',
            'filename': 'app.log',
            'maxBytes': 1048576,  # 1MB
            'backupCount': 3,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}


logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger(__name__)
