from Jumpscale import j


class SmtpdFactory(j.baseclasses.object, j.baseclasses.testtools):

    __jslocation__ = "j.threebot.package.smtp"

    def start(self):
        """
        called when the 3bot starts
        :return:
        """
        # TODO: ADD REVERSE PROXY

        # Couldn't import file app.py directly!
        from .app import MailServer

        rack = j.servers.rack.get()
        server = MailServer(("0.0.0.0", 7002))
        rack.add(name="smtp", server=server)
        rack.start()

    def test(self, name=""):
        self.client = j.servers.threebot.local_start_default()

        if not j.tools.threebot_packages.exists("threebot_smtp"):
            self.client.actors.package_manager.package_add(
                "threebot_smtp",
                git_url="https://github.com/threefoldtech/jumpscaleX_threebot/tree/master/ThreeBotPackages/smtp",
            )
        self.client.reload()
        print(name)
        self._test_run(name=name)
        self._log_info("All TESTS DONE")
        return "OK"
