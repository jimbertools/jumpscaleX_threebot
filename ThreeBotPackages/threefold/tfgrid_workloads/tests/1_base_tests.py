import gevent
from gevent import monkey

monkey.patch_all(thread=False)
import logging
from nacl import signing

import binascii
from Jumpscale import j


def main(self):
    customer_signing_key = signing.SigningKey.generate()
    farmer_signing_key = signing.SigningKey.generate()
    signer_signing_key = signing.SigningKey.generate()

    try:
        bcdb = j.data.bcdb.new("tf_workloads")
    except:
        bcdb = j.data.bcdb.get("tf_workloads")
    reservation_model = bcdb.model_get(url="tfgrid.reservation.1")
    reservation_model.destroy()  # ensure it's empty

    try:
        ph_bcdb = j.data.bcdb.new("threebot_phonebook")
    except:
        ph_bcdb = j.data.bcdb.get("threebot_phonebook")

    model = ph_bcdb.model_get(url="threebot.phonebook.user.1")
    model.destroy()

    threebots = [
        {"role": "signer", "pubkey": binascii.hexlify(signer_signing_key.verify_key.encode())},
        {"role": "farmer", "pubkey": binascii.hexlify(farmer_signing_key.verify_key.encode())},
        {"role": "customer", "pubkey": binascii.hexlify(customer_signing_key.verify_key.encode())},
    ]
    tbots = {}
    for threebot in threebots:
        tbot = model.new()
        role = threebot["role"]
        tbot.name = role
        tbot.email = "{}@{}.com".format(role, role)
        tbot.pubkey = threebot["pubkey"]
        tbot.save()
        tbots[role] = tbot

    # TEST01: REGISTER RESERVATION
    reservation_model = bcdb.model_get(url="tfgrid.reservation.1")
    reservation_model.destroy()

    reservation = reservation_model.new()
    reservation.customer_tid = tbots["customer"].id

    container_model = bcdb.model_get(url="tfgrid.reservation.container.1")
    volume_model = bcdb.model_get(url="tfgrid.reservation.volume.1")
    zdb_model = bcdb.model_get(url="tfgrid.reservation.zdb.1")
    # create container
    container = container_model.new()
    container.node_id = 1
    container.workload_id = 2
    container.farmer_tid = tbots["farmer"].id
    # create volume
    volume = volume_model.new()
    volume.node_id = 1
    volume.workload_id = 1
    volume.farmer_tid = tbots["farmer"].id
    # create zdb
    zdb = zdb_model.new()
    zdb.node_id = 2
    zdb.workload_id = 3
    zdb.farmer_tid = tbots["farmer"].id

    reservation.data_reservation.containers.append(container)
    reservation.data_reservation.volumes.append(volume)
    reservation.data_reservation.zdbs.append(zdb)
    # create sigining request
    request_model = bcdb.model_get(url="tfgrid.reservation.signing.request.1")
    request = request_model.new()
    request.signers = [tbots["signer"].id]
    request.quorum_min = 1
    request.save()
    reservation.data_reservation.signing_request_provision = request
    reservation.data_reservation.signing_request_delete = request
    reservation.customer_tid = tbots["customer"].id
    reservation.data_reservation.expiration_provisioning = int(j.data.time.epoch + 3 * 60)
    reservation.data_reservation.expiration_reservation = int(j.data.time.epoch + 5 * 60)
    reservation.json = j.data.serializers.json.dumps(reservation.data_reservation._ddict)

    reservation_data = reservation._ddict
    # Register reservation
    cl = j.clients.gedis.get(name="threebot")
    reservation = cl.actors.workload_manager.reservation_register(reservation_data)
    assert reservation.next_action == "CREATE"

    # TEST02: GET RESERVATION
    reservation = cl.actors.workload_manager.reservation_get(reservation.id)
    assert reservation.next_action == "CREATE"

    # TEST03: LIST RESERVATION
    reservations = cl.actors.workload_manager.reservations_list()
    assert len(reservations) == 1

    reservations = cl.actors.workload_manager.reservations_list(node_id=1)
    assert len(reservations) == 1

    reservations = cl.actors.workload_manager.reservations_list(node_id=3)
    assert len(reservations) == 0

    reservations = cl.actors.workload_manager.reservations_list(epoch=j.data.time.epoch + 1000)
    assert len(reservations) == 0

    # TEST04: SING RESERVATION
    signature = customer_signing_key.sign(reservation.json.encode())
    cl.actors.workload_manager.sign_customer(reservation.id, binascii.hexlify(signature.signature))
    reservation = cl.actors.workload_manager.reservation_get(reservation.id)
    assert reservation.next_action == "SIGN"

    # TEST05: FILL SIGNING REQUESTS
    signature = signer_signing_key.sign(reservation.json.encode())
    cl.actors.workload_manager.sign_provision(reservation.id, tbots["signer"].id, binascii.hexlify(signature.signature))
    reservation = cl.actors.workload_manager.reservation_get(reservation.id)
    assert reservation.next_action == "PAY"

    # TEST06: FILL FARMER SIGNATURE
    signature = farmer_signing_key.sign(reservation.json.encode())
    cl.actors.workload_manager.sign_farmer(reservation.id, tbots["farmer"].id, binascii.hexlify(signature.signature))
    reservation = cl.actors.workload_manager.reservation_get(reservation.id)
    assert reservation.next_action == "DEPLOY"

    # TEST07: LIST WORKLOADS
    workloads = cl.actors.workload_manager.workloads_list(node_id=1)
    assert len(workloads) == 2

    workloads = cl.actors.workload_manager.workloads_list(node_id=2)
    assert len(workloads) == 1

    workloads = cl.actors.workload_manager.workloads_list(node_id=0)
    assert len(workloads) == 0

    # TEST08: FILL SING DELETE
    signature = signer_signing_key.sign(reservation.json.encode())
    cl.actors.workload_manager.sign_delete(reservation.id, tbots["signer"].id, binascii.hexlify(signature.signature))
    reservation = cl.actors.workload_manager.reservation_get(reservation.id)
    assert reservation.next_action == "DELETE"
