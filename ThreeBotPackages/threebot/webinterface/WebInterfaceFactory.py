from Jumpscale import j


class WebInterfaceFactory(j.baseclasses.object, j.baseclasses.testtools):

    __jslocation__ = "j.threebot.package.webinterface"

    def start(self):
        """
        kosmos 'j.threebot.package.webinterface.start()'
        :return:
        """
        gedis_client = j.servers.threebot.local_start_default(web=True)
        gedis_client.actors.package_manager.package_add(path=j.threebot.package.webinterface._dirpath)

    def test(self, name=""):
        """
        kosmos 'j.threebot.package.webinterface.test()'
        :return:
        """
        self.start()
        # TODO: create a test
        pass
