from Jumpscale import j


class Package(j.baseclasses.threebot_package):
    def _init(self, *args, **kwargs):
        self.bcdb = self._package.threebot_server.bcdb_get("contacts")

    def prepare(self):
        """
        Dependencies
        """

    def start(self):
        self.bcdb.models_add(path=self.package_root + "/models")
        self.gedis_server.actors_add(path=self.package_root + "/actors")

    def stop(self):
        pass

    def uninstall(self):
        """
        Remove Dependencies
        """
