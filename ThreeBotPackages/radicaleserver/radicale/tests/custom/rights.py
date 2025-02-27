# This file is part of Radicale Server - Calendar Server
# Copyright © 2017-2018 Unrud <unrud@outlook.com>
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
Custom rights management.

"""

from radicale import pathutils, rights


class Rights(rights.BaseRights):
    def authorized(self, user, path, permissions):
        sane_path = pathutils.strip_path(path)
        if sane_path not in ("tmp", "other"):
            return ""
        return rights.intersect_permissions(permissions)
