# Built-in
import inspect
import json
import logging
import os
import socket
import sys
import threading
from typing import Optional

# Requirements
from google.cloud import logging as gcp_log
from google.cloud.logging import handlers

# Local
from gcpwrapper.cloudlogging import exceptions


class Logger:
    SEVERITIES = {
        logging.CRITICAL: 'CRITICAL',
        logging.ERROR: 'ERROR',
        logging.WARNING: 'WARNING',
        logging.INFO: 'INFO',
        logging.DEBUG: 'DEBUG',
        logging.NOTSET: 'NOTSET'
    }
    
    def __init__(self,
                 app_name: str,
                 correlation_id: str='',
                 container_name: str='default',
                 set_level: str='INFO',
                 local_log: bool=False,
                 sink: str = "default",
                 system_log: str='SYSTEM SERVICE',
                 **kwargs
                 ):
        self._app_name = app_name
        self._correlation_id = correlation_id
        self._local_log = local_log
        if set_level.upper() not in Logger.SEVERITIES.values():
            raise exceptions.InvalidSeverityException(set_level)
        self._log_level = logging.getLevelName(set_level.upper())

        self._logger = self._create_logger()
        self._loggers = {
            logging.CRITICAL: self._logger.critical,
            logging.ERROR: self._logger.error,
            logging.WARNING: self._logger.warning,
            logging.INFO: self._logger.info,
            logging.DEBUG: self._logger.debug
        }
        self._json_message = {
            'applicationName': app_name,
            'clientIP': socket.gethostbyname(socket.gethostname()),
            'containerName': container_name,
            'hostName': socket.gethostname(),
            'processID': os.getpid(),
            'sink': sink,
            'systemLog': system_log,
            'threadID': threading.current_thread().ident
        }
        if correlation_id:
            self._json_message['correlationID'] = correlation_id
            
        if kwargs:
            self._json_message.update(**kwargs)
    
    @property
    def correlation_id(self) -> Optional[str]:
        return self._correlation_id
    
    @correlation_id.setter
    def correlation_id(self, correlation_id: str):
        self._correlation_id = correlation_id
        self._json_message['correlationID'] = correlation_id
        
    @property
    def local_log(self) -> bool:
        return self._local_log
    
    @local_log.setter
    def local_log(self, local_log: bool):
        self._local_log = local_log
        
    @property
    def set_level(self) -> str:
        return logging.getLevelName(self._log_level)
    
    @set_level.setter
    def set_level(self, set_level: str):
        if set_level.upper() not in Logger.SEVERITIES.values():
            raise exceptions.InvalidSeverityException(set_level)
        self._log_level = logging.getLevelName(set_level.upper())
            
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
    
    def _create_logger(self) -> logging.Logger:
        logger = logging.getLogger(self._app_name)
        logger.setLevel(self._log_level)
        if self._local_log:
            stream_handler = logging.StreamHandler(sys.stdout)
        else:
            log_client = gcp_log.Client()
            stream_handler = handlers.CloudLoggingHandler(log_client,
                                                          name=self._app_name
                                                          )
        logger.addHandler(stream_handler)
        return logger
    
    def _log(self, level: int, message: str, **kwargs):
        json_message = self._json_message.copy()
        json_message.update(**kwargs)
        json_message['severity'] = Logger.SEVERITIES[level]
        json_message['message'] = message
        exc_info = True if level in (logging.CRITICAL, logging.ERROR) else False
        if self._local_log:
            caller = inspect.getframeinfo(inspect.stack()[2][0])
            prefix = f'[{caller.filename}: {caller.lineno}]'
            msg = json_message['message']
            severity = json_message['severity']
            self._loggers[level](f'{severity} - {prefix} {msg}',
                                 exc_info=exc_info
                                 )
        else:
            self._loggers[level](json.dumps(json_message,
                                            sort_keys=True,
                                            default=str
                                            ),
                                 exc_info=exc_info
                                 )
