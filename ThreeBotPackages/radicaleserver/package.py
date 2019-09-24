import sys
import os

from Jumpscale import j


class Package(j.baseclasses.threebot_package):
    def prepare(self):
        """
        is called at install time
        :return:
        """
        j.builders.runtimes.python3.pip_package_install("filetype")
        j.builders.runtimes.python3.pip_package_install("vobject")

    def start(self):
        """
        called when the 3bot starts
        :return:
        """
        # TODO: ADD REVERSE PROXY
        sys.path.append(os.path.dirname(__file__))
        import radicale
        import logging

        radicale.log.logger.setLevel(logging.DEBUG)
        from radicale import application

        rack = j.servers.rack.get()

        rack.bottle_server_add(name="radicale", port=8851, app=application)
        website = self.openresty.websites.get("radicale")
        website.ssl = False
        website.port = 8850

        locations = website.locations.get("radicale")
        proxy_location = locations.locations_proxy.new()
        proxy_location.name = "radicale"
        proxy_location.path_url = "/"
        proxy_location.ipaddr_dest = "0.0.0.0"
        proxy_location.port_dest = 8851
        proxy_location.scheme = "http"

        website_location = locations.locations_static.new()
        website_location.name = "static"
        website_location.path_url = "/static/"
        website_location.path_location = f"{self._dirpath}/static"
        # website_location.use_jumpscale_weblibs = True

        locations.configure()
        website.configure()

    def stop(self):
        """
        called when the 3bot stops
        :return:
        """
        pass

    def uninstall(self):
        """
        called when the package is no longer needed and will be removed from the threebot
        :return:
        """
        j.builders.runtimes.python3.pip_package_uninstall("filetype")
