# This file is part of Radicale Server - Calendar Server
# Copyright © 2008 Nicolas Kandel
# Copyright © 2008 Pascal Halter
# Copyright © 2014 Jean-Marc Martins
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
import math
import sys
from hashlib import md5
from random import getrandbits

import vobject

from radicale import pathutils
from radicale.item import filter as radicale_filter
from Jumpscale import j


def predict_tag_of_parent_collection(vobject_items):
    if len(vobject_items) != 1:
        return ""
    if vobject_items[0].name == "VCALENDAR":
        return "VCALENDAR"
    if vobject_items[0].name in ("VCARD", "VLIST"):
        return "VADDRESSBOOK"
    return ""


def predict_tag_of_whole_collection(vobject_items, fallback_tag=None):
    if vobject_items and vobject_items[0].name == "VCALENDAR":
        return "VCALENDAR"
    if vobject_items and vobject_items[0].name in ("VCARD", "VLIST"):
        return "VADDRESSBOOK"
    if not fallback_tag and not vobject_items:
        # Maybe an empty address book
        return "VADDRESSBOOK"
    return fallback_tag


def check_and_sanitize_items(vobject_items, is_collection=False, tag=None):
    """Check vobject items for common errors and add missing UIDs.

    ``is_collection`` indicates that vobject_item contains unrelated
    components.

    The ``tag`` of the collection.

    """
    if tag and tag not in ("VCALENDAR", "VADDRESSBOOK"):
        raise j.exceptions.Value("Unsupported collection tag: %r" % tag)
    if not is_collection and len(vobject_items) != 1:
        raise j.exceptions.Value("Item contains %d components" % len(vobject_items))
    if tag == "VCALENDAR":
        if len(vobject_items) > 1:
            raise j.exceptions.Base("VCALENDAR collection contains %d " "components" % len(vobject_items))
        vobject_item = vobject_items[0]
        if vobject_item.name != "VCALENDAR":
            raise j.exceptions.Value("Item type %r not supported in %r " "collection" % (vobject_item.name, tag))
        component_uids = set()
        for component in vobject_item.components():
            if component.name in ("VTODO", "VEVENT", "VJOURNAL"):
                component_uid = get_uid(component)
                if component_uid:
                    component_uids.add(component_uid)
        component_name = None
        object_uid = None
        object_uid_set = False
        for component in vobject_item.components():
            # https://tools.ietf.org/html/rfc4791#section-4.1
            if component.name == "VTIMEZONE":
                continue
            if component_name is None or is_collection:
                component_name = component.name
            elif component_name != component.name:
                raise j.exceptions.Value(
                    "Multiple component types in object: %r, %r" % (component_name, component.name)
                )
            if component_name not in ("VTODO", "VEVENT", "VJOURNAL"):
                continue
            component_uid = get_uid(component)
            if not object_uid_set or is_collection:
                object_uid_set = True
                object_uid = component_uid
                if not component_uid:
                    if not is_collection:
                        raise j.exceptions.Value("%s component without UID in object" % component_name)
                    component_uid = find_available_uid(component_uids.__contains__)
                    component_uids.add(component_uid)
                    if hasattr(component, "uid"):
                        component.uid.value = component_uid
                    else:
                        component.add("UID").value = component_uid
            elif not object_uid or not component_uid:
                raise j.exceptions.Value("Multiple %s components without UID in " "object" % component_name)
            elif object_uid != component_uid:
                raise j.exceptions.Value(
                    "Multiple %s components with different UIDs in object: "
                    "%r, %r" % (component_name, object_uid, component_uid)
                )
            # vobject interprets recurrence rules on demand
            try:
                component.rruleset
            except Exception as e:
                raise j.exceptions.Value("invalid recurrence rules in %s" % component.name) from e
    elif tag == "VADDRESSBOOK":
        # https://tools.ietf.org/html/rfc6352#section-5.1
        object_uids = set()
        for vobject_item in vobject_items:
            if vobject_item.name == "VCARD":
                object_uid = get_uid(vobject_item)
                if object_uid:
                    object_uids.add(object_uid)
        for vobject_item in vobject_items:
            if vobject_item.name == "VLIST":
                # Custom format used by SOGo Connector to store lists of
                # contacts
                continue
            if vobject_item.name != "VCARD":
                raise j.exceptions.Value("Item type %r not supported in %r " "collection" % (vobject_item.name, tag))
            object_uid = get_uid(vobject_item)
            if not object_uid:
                if not is_collection:
                    raise j.exceptions.Value("%s object without UID" % vobject_item.name)
                object_uid = find_available_uid(object_uids.__contains__)
                object_uids.add(object_uid)
                if hasattr(vobject_item, "uid"):
                    vobject_item.uid.value = object_uid
                else:
                    vobject_item.add("UID").value = object_uid
    else:
        for i in vobject_items:
            raise j.exceptions.Value(
                "Item type %r not supported in %s collection" % (i.name, repr(tag) if tag else "generic")
            )


def check_and_sanitize_props(props):
    """Check collection properties for common errors."""
    tag = props.get("tag")
    if tag and tag not in ("VCALENDAR", "VADDRESSBOOK"):
        raise j.exceptions.Value("Unsupported collection tag: %r" % tag)


def find_available_uid(exists_fn, suffix=""):
    """Generate a pseudo-random UID"""
    # Prevent infinite loop
    for _ in range(1000):
        r = "%016x" % getrandbits(128)
        name = "%s-%s-%s-%s-%s%s" % (r[:8], r[8:12], r[12:16], r[16:20], r[20:], suffix)
        if not exists_fn(name):
            return name
    # something is wrong with the PRNG
    raise j.exceptions.Base("No unique random sequence found")


def get_etag(text):
    """Etag from collection or item.

    Encoded as quoted-string (see RFC 2616).

    """
    etag = md5()
    etag.update(text.encode("utf-8"))
    return '"%s"' % etag.hexdigest()


def get_uid(vobject_component):
    """UID value of an item if defined."""
    return vobject_component.uid.value if hasattr(vobject_component, "uid") else None


def get_uid_from_object(vobject_item):
    """UID value of an calendar/addressbook object."""
    if vobject_item.name == "VCALENDAR":
        if hasattr(vobject_item, "vevent"):
            return get_uid(vobject_item.vevent)
        if hasattr(vobject_item, "vjournal"):
            return get_uid(vobject_item.vjournal)
        if hasattr(vobject_item, "vtodo"):
            return get_uid(vobject_item.vtodo)
    elif vobject_item.name == "VCARD":
        return get_uid(vobject_item)
    return None


def find_tag(vobject_item):
    """Find component name from ``vobject_item``."""
    if vobject_item.name == "VCALENDAR":
        for component in vobject_item.components():
            if component.name != "VTIMEZONE":
                return component.name or ""
    return ""


def find_tag_and_time_range(vobject_item):
    """Find component name and enclosing time range from ``vobject item``.

    Returns a tuple (``tag``, ``start``, ``end``) where ``tag`` is a string
    and ``start`` and ``end`` are POSIX timestamps (as int).

    This is intened to be used for matching against simplified prefilters.

    """
    tag = find_tag(vobject_item)
    if not tag:
        return (tag, radicale_filter.TIMESTAMP_MIN, radicale_filter.TIMESTAMP_MAX)
    start = end = None

    def range_fn(range_start, range_end, is_recurrence):
        nonlocal start, end
        if start is None or range_start < start:
            start = range_start
        if end is None or end < range_end:
            end = range_end
        return False

    def infinity_fn(range_start):
        nonlocal start, end
        if start is None or range_start < start:
            start = range_start
        end = radicale_filter.DATETIME_MAX
        return True

    radicale_filter.visit_time_ranges(vobject_item, tag, range_fn, infinity_fn)
    if start is None:
        start = radicale_filter.DATETIME_MIN
    if end is None:
        end = radicale_filter.DATETIME_MAX
    try:
        return tag, math.floor(start.timestamp()), math.ceil(end.timestamp())
    except ValueError as e:
        if str(e) == ("offset must be a timedelta representing a whole " "number of minutes") and sys.version_info < (
            3,
            6,
        ):
            raise j.exceptions.Base("Unsupported in Python < 3.6: %s" % e) from e
        raise


class Item:
    def __init__(
        self,
        collection_path=None,
        collection=None,
        vobject_item=None,
        href=None,
        last_modified=None,
        text=None,
        etag=None,
        uid=None,
        name=None,
        component_name=None,
        time_range=None,
    ):
        """Initialize an item.

        ``collection_path`` the path of the parent collection (optional if
        ``collection`` is set).

        ``collection`` the parent collection (optional).

        ``href`` the href of the item.

        ``last_modified`` the HTTP-datetime of when the item was modified.

        ``text`` the text representation of the item (optional if
        ``vobject_item`` is set).

        ``vobject_item`` the vobject item (optional if ``text`` is set).

        ``etag`` the etag of the item (optional). See ``get_etag``.

        ``uid`` the UID of the object (optional). See ``get_uid_from_object``.

        ``name`` the name of the item (optional). See ``vobject_item.name``.

        ``component_name`` the name of the primary component (optional).
        See ``find_tag``.

        ``time_range`` the enclosing time range.
        See ``find_tag_and_time_range``.

        """
        if text is None and vobject_item is None:
            raise j.exceptions.Value("at least one of 'text' or 'vobject_item' must be set")
        if collection_path is None:
            if collection is None:
                raise j.exceptions.Value("at least one of 'collection_path' or " "'collection' must be set")
            collection_path = collection.path
        assert collection_path == pathutils.strip_path(pathutils.sanitize_path(collection_path))
        self._collection_path = collection_path
        self.collection = collection
        self.href = href
        self.last_modified = last_modified
        self._text = text
        self._vobject_item = vobject_item
        self._etag = etag
        self._uid = uid
        self._name = name
        self._component_name = component_name
        self._time_range = time_range

    def serialize(self):
        if self._text is None:
            try:
                self._text = self.vobject_item.serialize()
            except Exception as e:
                raise j.exceptions.Base(
                    "Failed to serialize item %r from %r: %s" % (self.href, self._collection_path, e)
                ) from e
        return self._text

    @property
    def vobject_item(self):
        if self._vobject_item is None:
            try:
                self._vobject_item = vobject.readOne(self._text)
            except Exception as e:
                raise j.exceptions.Base(
                    "Failed to parse item %r from %r: %s" % (self.href, self._collection_path, e)
                ) from e
        return self._vobject_item

    @property
    def etag(self):
        """Encoded as quoted-string (see RFC 2616)."""
        if self._etag is None:
            self._etag = get_etag(self.serialize())
        return self._etag

    @property
    def uid(self):
        if self._uid is None:
            self._uid = get_uid_from_object(self.vobject_item)
        return self._uid

    @property
    def name(self):
        if self._name is None:
            self._name = self.vobject_item.name or ""
        return self._name

    @property
    def component_name(self):
        if self._component_name is not None:
            return self._component_name
        return find_tag(self.vobject_item)

    @property
    def time_range(self):
        if self._time_range is None:
            self._component_name, *self._time_range = find_tag_and_time_range(self.vobject_item)
        return self._time_range

    def prepare(self):
        """Fill cache with values."""
        orig_vobject_item = self._vobject_item
        self.serialize()
        self.etag
        self.uid
        self.name
        self.time_range
        self.component_name
        self._vobject_item = orig_vobject_item
