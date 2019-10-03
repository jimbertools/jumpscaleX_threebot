from Jumpscale import j


class TFTokenFactory(j.baseclasses.threebot_factory):
    __jslocation__ = "j.threebot.package.token"
    _web = False

    def start(self):
        gedis_client = j.servers.threebot.local_start_default(web=True)
        gedis_client.actors.package_manager.package_add(path=self._dirpath)

    def client_get(self):
        """
        j.threebot.package.token.client_get()
        :return:
        """
        j.servers.threebot.local_start_default(web=True)
        self.client = j.servers.threebot.current.client
        self.client.actors.package_manager.package_add(
            git_url="https://github.com/threefoldtech/jumpscaleX_threebot/tree/master/ThreeBotPackages/threefold/tfgrid_token"
        )
        self.client.reload()
        """ self.client.reload(namespace="token") """

        return self.client

    """ def _generate_dummy_data(self, bcdb, timeframe, price_from=0.06):
        res = []
        tframe = timeframe.lower()
        if tframe == "year":
            count = 5
        elif tframe == "month":
            count = 12
        elif tframe == "day":
            count = 31
        elif tframe == "hour":
            count = 24
        else:
            count = 0

        for x in range(count):
            price = bcdb.model_get(url="tfgrid.token.price.1")
            t = price.new()
            t.timeframe = timeframe
            percent = random.uniform(0.000001, 99.99999)
            percent_less = random.uniform(0.000001, 99.99999)
            while percent_less > percent:
                percent = random.uniform(0.000001, 99.99999)
                percent_less = random.uniform(0.000001, 99.99999)
            sign = random.uniform(-99, 99)
            t.low = str((price_from - (price_from / 100) * percent)) + " USD"
            t.high = str((price_from + (price_from / 100) * percent)) + " USD"
            if sign > 0:
                # bull opening < closing
                t.opening = str((price_from - (price_from / 100) * percent_less)) + " USD"
                t.closing = str((price_from + (price_from / 100) * percent_less)) + " USD"
            else:
                # bear opening > closing
                t.closing = str((price_from - (price_from / 100) * percent_less)) + " USD"
                t.opening = str((price_from + (price_from / 100) * percent_less)) + " USD"

            if tframe == "year":
                t.time = str(2014 + x) + "/01/01"
            elif tframe == "month":
                t.time = "2019/" + str(x + 1) + "/01"
            elif tframe == "day":
                t.time = "2019/10/" + str(x + 1)
            elif tframe == "hour":
                t.time = 1569888000 + x * 3600
            res.append(t)
        return res """

    def test(self, name=""):
        """
        kosmos 'j.threebot.package.token.test()'
        """

        if "tf_grid_token" in [b.name for b in j.data.bcdb.instances]:
            m = j.data.bcdb.get("tf_grid_token")
        else:
            m = j.data.bcdb.new("tf_grid_token")
        m.models_add(path=self._dirpath + "/models")

        gedis_cli = self.client_get()

        cl = j.clients.redis.get(port=8901)
        assert cl.execute_command("PING")
        assert gedis_cli.actors.token.delete_all()

        gedis_cli.actors.token.feed_dummy_data_prices("year", 2019, 10, 1, 0.06)

        res = gedis_cli.actors.token.list()
        assert len(res.prices) == 5

        res = gedis_cli.actors.token.get_market()
        print("****************************get_market*********res****:%s" % res)
        assert res.max_supply == 100000000000
        assert res.potential_revenue_per_token_usd > 0

        res = gedis_cli.actors.token.get_capacity()
        print("****************************get_capacity*********res****:%s" % res)
        assert res.compute_units > 19000
        assert res.cores > 0

        res = gedis_cli.actors.token.find_prices("year")
        assert len(res) == 5

        res = gedis_cli.actors.token.find_prices("year", from_date="2018/02/02")
        assert len(res) == 0
        res = gedis_cli.actors.token.find_prices("year", from_date="2018/01/01")
        assert len(res) == 1
        res = gedis_cli.actors.token.find_prices("year", from_date="2016/02/02", to_date="2018/05/05")
        assert len(res) == 2

        print("****************************find*********res****:%s" % res)
        gedis_cli.actors.token.feed_dummy_data_prices("month", 2019, 10, 1, 0.06)
        assert len(gedis_cli.actors.token.find_prices("month")) == 12
        gedis_cli.actors.token.feed_dummy_data_prices("day", 2019, 10, 1, 0.06)
        assert len(gedis_cli.actors.token.find_prices("day")) == 31
        gedis_cli.actors.token.feed_dummy_data_prices("hour", 2019, 10, 1, 0.06)
        assert len(gedis_cli.actors.token.find_prices("hour")) == 24

        res = gedis_cli.actors.token.find_prices("hour", from_date="2019/10/01 01:55", to_date="2019/10/01 05:42")
        assert len(res) == 4
        self._log_info("All TESTS DONE")
        return "OK"
