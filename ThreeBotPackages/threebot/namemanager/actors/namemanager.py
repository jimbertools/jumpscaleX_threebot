from Jumpscale import j


class namemanager(j.baseclasses.threebot_actor):
    def _init(self, **kwargs):
        pass

    def tcpservice_register(self, name, domain, endpoint, user_session=None):
        """
        Registers a tcpservice to be used by tcprouter in j.core.db

        ```in
        name = (S) # service name
        domain = (S) # (Server Name Indicator SNI) (e.g a.b.3bots.grid.tf)
        endpoint = (S) # TLS endpoint 102.142.96.34:443 "ip:port" 3bot private wireguard ip
        ```
        """
        j.tools.tf_gateway.tcpservice_register(name, domain, endpoint)
        return True

    def domain_register(self, name, domain, gateway_domain, user_session=None):
        """
        Registers a domain in coredns (needs to be authoritative)

        ```in
        name = (S) # 3bot subdomain name
        domain = (S) # defaults to "3bots.grid.tf"
        gateway_domain = "gateway.grid.tf" (S)
        ```
        """
        j.tools.tf_gateway.domain_register_cname(name, domain, gateway_domain)
        return True
