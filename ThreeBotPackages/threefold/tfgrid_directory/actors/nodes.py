from Jumpscale import j


class nodes(j.baseclasses.threebot_actor):
    def _init(self, **kwargs):

        bcdb = j.data.bcdb.get("tf_directory")
        self.node_model = bcdb.model_get(url="tfgrid.node.2")
        self.farm_model = bcdb.model_get(url="tfgrid.farm.1")

    def _find(self, node_id):
        nodes = self.node_model.find(node_id=node_id)
        if len(nodes) <= 0:
            return None
        return nodes[0]

    def add(self, node, schema_out=None, user_session=None):
        """
        ```in
        node = (O) !tfgrid.node.2
        ```

        ```out
        node = (O) !tfgrid.node.2
        ```

        """
        # TODO check the sender is actually the node itself
        validation_errors = []
        if not node.node_id:
            validation_errors.append("node_id")
        if not node.os_version:
            validation_errors.append("os_version")
        if not node.farm_id:
            validation_errors.append("farm_id")
        if not node.location:
            validation_errors.append("location")
        if validation_errors:
            raise Exception("Can not create node without {}".format(" or ".join(validation_errors)))
        old_node = self._find(node.node_id)
        if old_node:
            return self.node_model.set_dynamic(node._ddict, obj_id=old_node.id)
        return self.node_model.new(data=node).save()

    def list(self, farm_id, country, city, cru, sru, mru, hru, proofs, schema_out=None, user_session=None):
        """
        ```in
        farm_id = (S)
        country = (S)
        city = (S)
        cru = -1 (I)
        mru = -1 (I)
        sru = -1 (I)
        hru = -1 (I)
        proofs = False (B)
        ```

        ```out
        nodes = (LO) !tfgrid.node.2
        ```
        """

        output = schema_out.new()
        for node in self.node_model.iterate():
            if farm_id and farm_id != node.farm_id:
                continue
            if country != "" and node.location.country != country:
                continue
            if city != "" and node.location.city != city:
                continue
            if cru > -1 and node.total_resources.cru < cru:
                continue
            if mru > -1 and node.total_resources.mru < mru:
                continue
            if sru > -1 and node.total_resources.sru < sru:
                continue
            if hru > -1 and node.total_resources.hru < hru:
                continue
            if not proofs:
                node.proofs = []
            output.nodes.append(node)

        return output

    def get(self, node_id, proofs, schema_out=None, user_session=None):
        """
        ```in
        node_id = (S)
        proofs = False (B)
        ```

        ```out
        node = (O) !tfgrid.node.2
        ```
        """
        node = self._find(node_id)
        if not proofs:
            node.proofs = []
        return node

    def update_total_capacity(self, node_id, resource, schema_out=None, user_session=None):
        """
        ```in
        node_id = (S)
        resource = (O) !tfgrid.node.resource.amount.1
        ```

        """
        node = self._find(node_id)
        if not node:
            raise j.exceptions.NotFound("node %s not found" % id)
        node.total_resources.mru = resource.mru
        node.total_resources.cru = resource.cru
        node.total_resources.hru = resource.hru
        node.total_resources.sru = resource.sru
        node.save()
        return True

    def update_reserved_capacity(self, node_id, resource, schema_out=None, user_session=None):
        """
        ```in
        node_id = (S)
        resource = (O) !tfgrid.node.resource.amount.1
        ```
        """
        node = self._find(node_id)
        if not node:
            raise j.exceptions.NotFound("node %s not found" % id)
        node.reserved_resources.mru = resource.mru
        node.reserved_resources.cru = resource.cru
        node.reserved_resources.hru = resource.hru
        node.reserved_resources.sru = resource.sru

        node.save()
        return True

    def update_used_capacity(self, node_id, resource, schema_out=None, user_session=None):
        """
        ```in
        node_id = (S)
        resource = (O) !tfgrid.node.resource.amount.1
        ```
        """

        node = self._find(node_id)
        if not node:
            raise j.exceptions.NotFound("node %s not found" % id)
        node.used_resources.mru = resource.mru
        node.used_resources.cru = resource.cru
        node.used_resources.hru = resource.hru
        node.used_resources.sru = resource.sru
        node.save()
        return True

    def publish_interfaces(self, node_id, ifaces, schema_out=None, user_session=None):
        """
        ```in
        node_id = (S)
        ifaces = (LO) !tfgrid.node.iface.1
        ```
        """

        node = self._find(node_id)
        if not node:
            raise j.exceptions.NotFound("node %s not found" % id)
        node.ifaces = ifaces
        node.save()
        return True

    def set_public_iface(self, node_id, public, schema_out=None, user_session=None):
        """
        ```in
        node_id = (S)
        public = (O) !tfgrid.node.public_iface.1
        ```
        """

        node = self._find(node_id)
        if not node:
            raise j.exceptions.NotFound("node %s not found" % id)

        node.public_config = public
        node.save()
        return True
