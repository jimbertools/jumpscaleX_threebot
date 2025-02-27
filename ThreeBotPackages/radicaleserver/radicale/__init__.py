# This file is part of Radicale Server - Calendar Server
# Copyright © 2008 Nicolas Kandel
# Copyright © 2008 Pascal Halter
# Copyright © 2008-2017 Guillaume Ayoub
# Copyright © 2017-2019 Unrud <unrud@outlook.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
"""
Radicale WSGI application.

Can be used with an external WSGI server or the built-in server.

"""

import os
import threading

# import pkg_resources
from radicale import config, log
from radicale.app import Application
from Jumpscale import j

# VERSION = pkg_resources.get_distribution("radicale").version

_application = None
_application_config_path = None
_application_lock = threading.Lock()


def _init_application(config_path, wsgi_errors):
    global _application, _application_config_path
    with _application_lock:
        if _application is not None:
            return
        log.setup()
        with log.register_stream(wsgi_errors):
            _application_config_path = config_path
            configuration = config.load(config.parse_compound_paths(config.DEFAULT_CONFIG_PATH, config_path))
            log.set_level(configuration.get("logging", "level"))
            # Inspect configuration after logger is configured
            configuration.inspect()
            _application = Application(configuration)


def application(environ, start_response):
    config_path = environ.get("RADICALE_CONFIG", os.environ.get("RADICALE_CONFIG"))
    if _application is None:
        _init_application(config_path, environ["wsgi.errors"])
    if _application_config_path != config_path:
        raise j.exceptions.Value(
            "RADICALE_CONFIG must not change: %s != %s" % (repr(config_path), repr(_application_config_path))
        )
    return _application(environ, start_response)
