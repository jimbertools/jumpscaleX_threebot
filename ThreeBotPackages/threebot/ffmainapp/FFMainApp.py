from Jumpscale import j
import os


class FFMainApp(j.baseclasses.object, j.baseclasses.testtools):

    __jslocation__ = "j.threebot.package.ffmainapp"

    def install(self):
        server = j.servers.threebot.default
        website = server.openresty_server.get_from_port(80)
        website.ssl = False

        website.save()

        locations = website.locations.get("locations")

        for pkg in ["ffbrowser", "interface", "contacts","appstore"]:
            print("DIIR PATH: ", self._dirpath)
            package = j.tools.threebot_packages.get(
                pkg, path=os.path.join(os.path.dirname(self._dirpath), pkg), threebot_server_name=server.name
            )
            package.prepare()
            package.start()
            package.save()

        rack = j.servers.rack.get()
        app = j.servers.gedishttp.get_app()
        rack.bottle_server_add(name="gedishttp", port=9201, app=app)

        proxy_location = locations.locations_proxy.new()
        proxy_location.name = "gedishttp"
        proxy_location.path_url = "/actors"
        proxy_location.ipaddr_dest = "0.0.0.0"
        proxy_location.port_dest = 9201
        proxy_location.scheme = "http"

        locations.configure()
        website.configure()
        return "OK"

    def start(self):
        self.install()
        server = j.servers.threebot.default
        server.start(web=True, ssl=False)

    def test(self, name=""):
        pass
