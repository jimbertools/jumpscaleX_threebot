# This file is part of Radicale Server - Calendar Server
# Copyright © 2008 Nicolas Kandel
# Copyright © 2008 Pascal Halter
# Copyright © 2008-2017 Guillaume Ayoub
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
import itertools
import posixpath
import socket
import sys
from http import client

import vobject

from radicale import httputils
from radicale import item as radicale_item
from radicale import pathutils, storage, xmlutils
from radicale.log import logger
from Jumpscale import j


class ApplicationPutMixin:
    def do_PUT(self, environ, base_prefix, path, user):
        """Manage PUT request."""
        if not self.access(user, path, "w"):
            return httputils.NOT_ALLOWED
        try:
            content = self.read_content(environ)
        except RuntimeError as e:
            logger.warning("Bad PUT request on %r: %s", path, e, exc_info=True)
            return httputils.BAD_REQUEST
        except socket.timeout:
            logger.debug("client timed out", exc_info=True)
            return httputils.REQUEST_TIMEOUT
        # Prepare before locking
        parent_path = pathutils.unstrip_path(posixpath.dirname(pathutils.strip_path(path)), True)
        permissions = self.Rights.authorized(user, path, "Ww")
        parent_permissions = self.Rights.authorized(user, parent_path, "w")

        def prepare(vobject_items, tag=None, write_whole_collection=None):
            if write_whole_collection or permissions and not parent_permissions:
                write_whole_collection = True
                content_type = environ.get("CONTENT_TYPE", "").split(";")[0]
                tags = {value: key for key, value in xmlutils.MIMETYPES.items()}
                tag = radicale_item.predict_tag_of_whole_collection(vobject_items, tags.get(content_type))
                if not tag:
                    raise j.exceptions.Value("Can't determine collection tag")
                collection_path = pathutils.strip_path(path)
            elif (
                write_whole_collection is not None
                and not write_whole_collection
                or not permissions
                and parent_permissions
            ):
                write_whole_collection = False
                if tag is None:
                    tag = radicale_item.predict_tag_of_parent_collection(vobject_items)
                collection_path = posixpath.dirname(pathutils.strip_path(path))
            props = None
            stored_exc_info = None
            items = []
            try:
                if tag:
                    radicale_item.check_and_sanitize_items(vobject_items, is_collection=write_whole_collection, tag=tag)
                    if write_whole_collection and tag == "VCALENDAR":
                        vobject_components = []
                        vobject_item, = vobject_items
                        for content in ("vevent", "vtodo", "vjournal"):
                            vobject_components.extend(getattr(vobject_item, "%s_list" % content, []))
                        vobject_components_by_uid = itertools.groupby(
                            sorted(vobject_components, key=radicale_item.get_uid), radicale_item.get_uid
                        )
                        for uid, components in vobject_components_by_uid:
                            vobject_collection = vobject.iCalendar()
                            for component in components:
                                vobject_collection.add(component)
                            item = radicale_item.Item(collection_path=collection_path, vobject_item=vobject_collection)
                            item.prepare()
                            items.append(item)
                    elif write_whole_collection and tag == "VADDRESSBOOK":
                        for vobject_item in vobject_items:
                            item = radicale_item.Item(collection_path=collection_path, vobject_item=vobject_item)
                            item.prepare()
                            items.append(item)
                    elif not write_whole_collection:
                        vobject_item, = vobject_items
                        item = radicale_item.Item(collection_path=collection_path, vobject_item=vobject_item)
                        item.prepare()
                        items.append(item)

                if write_whole_collection:
                    props = {}
                    if tag:
                        props["tag"] = tag
                    if tag == "VCALENDAR" and vobject_items:
                        if hasattr(vobject_items[0], "x_wr_calname"):
                            calname = vobject_items[0].x_wr_calname.value
                            if calname:
                                props["D:displayname"] = calname
                        if hasattr(vobject_items[0], "x_wr_caldesc"):
                            caldesc = vobject_items[0].x_wr_caldesc.value
                            if caldesc:
                                props["C:calendar-description"] = caldesc
                    radicale_item.check_and_sanitize_props(props)
            except Exception:
                stored_exc_info = sys.exc_info()

            # Use generator for items and delete references to free memory
            # early
            def items_generator():
                while items:
                    yield items.pop(0)

            return (items_generator(), tag, write_whole_collection, props, stored_exc_info)

        try:
            vobject_items = tuple(vobject.readComponents(content or ""))
        except Exception as e:
            logger.warning("Bad PUT request on %r: %s", path, e, exc_info=True)
            return httputils.BAD_REQUEST
        (prepared_items, prepared_tag, prepared_write_whole_collection, prepared_props, prepared_exc_info) = prepare(
            vobject_items
        )

        with self.Collection.acquire_lock("w", user):
            item = next(self.Collection.discover(path), None)
            parent_item = next(self.Collection.discover(parent_path), None)
            if not parent_item:
                return httputils.CONFLICT

            write_whole_collection = isinstance(item, storage.BaseCollection) or not parent_item.get_meta("tag")

            if write_whole_collection:
                tag = prepared_tag
            else:
                tag = parent_item.get_meta("tag")

            if write_whole_collection:
                if not self.Rights.authorized(user, path, "w" if tag else "W"):
                    return httputils.NOT_ALLOWED
            elif not self.Rights.authorized(user, parent_path, "w"):
                return httputils.NOT_ALLOWED

            etag = environ.get("HTTP_IF_MATCH", "")
            if not item and etag:
                # Etag asked but no item found: item has been removed
                return httputils.PRECONDITION_FAILED
            if item and etag and item.etag != etag:
                # Etag asked but item not matching: item has changed
                return httputils.PRECONDITION_FAILED

            match = environ.get("HTTP_IF_NONE_MATCH", "") == "*"
            if item and match:
                # Creation asked but item found: item can't be replaced
                return httputils.PRECONDITION_FAILED

            if tag != prepared_tag or prepared_write_whole_collection != write_whole_collection:
                (
                    prepared_items,
                    prepared_tag,
                    prepared_write_whole_collection,
                    prepared_props,
                    prepared_exc_info,
                ) = prepare(vobject_items, tag, write_whole_collection)
            props = prepared_props
            if prepared_exc_info:
                logger.warning("Bad PUT request on %r: %s", path, prepared_exc_info[1], exc_info=prepared_exc_info)
                return httputils.BAD_REQUEST

            if write_whole_collection:
                try:
                    coll = self.Collection.create_collection(path, prepared_items, props)
                    etag = coll.etag
                except ValueError as e:
                    logger.warning("Bad PUT request on %r: %s", path, e, exc_info=True)
                    return httputils.BAD_REQUEST
            else:
                prepared_item, = prepared_items
                if item and item.uid != prepared_item.uid or not item and parent_item.has_uid(prepared_item.uid):
                    return self.webdav_error_response("C" if tag == "VCALENDAR" else "CR", "no-uid-conflict")

                href = posixpath.basename(pathutils.strip_path(path))
                try:
                    etag = parent_item.upload(href, prepared_item).etag
                except ValueError as e:
                    logger.warning("Bad PUT request on %r: %s", path, e, exc_info=True)
                    return httputils.BAD_REQUEST

            headers = {"ETag": etag}
            return client.CREATED, headers, None
