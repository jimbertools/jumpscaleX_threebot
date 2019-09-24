from Jumpscale import j


class RadicaleFactory(j.baseclasses.object, j.baseclasses.testtools):

    __jslocation__ = "j.threebot.package.radicale"

    def install(self):
        server = j.servers.threebot.default
        server.save()

        package = j.tools.threebot_packages.get("radicale", path=self._dirpath, threebot_server_name=server.name)
        package.prepare()
        package.save()
        self._log_info("Radicale loaded")

        return "OK"

    def start(self, background=True, web=True, ssl=False):
        self.install()
        server = j.servers.threebot.default
        server.web = web
        server.ssl = ssl
        server.start(background=background)

    def test(self, name=""):
        self.client = j.servers.threebot.local_start_default()

        if not j.tools.threebot_packages.exists("threebot_radicale"):
            self.client.actors.package_manager.package_add(
                "threebot_radicale",
                git_url="https://github.com/threefoldtech/jumpscaleX_threebot/tree/master/ThreeBotPackages/radicalserver",
            )
        self.client.reload()
        print(name)
        self.start(background=True, web=True)
        self._test_run(name=name)

        self._log_info("All TESTS DONE")
        return "OK"
