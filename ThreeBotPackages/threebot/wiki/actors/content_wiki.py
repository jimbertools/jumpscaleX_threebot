from Jumpscale import j
import binascii
from io import BytesIO


class ffcontent(j.baseclasses.threebot_actor):
    def _init(self, *args, **kwargs):
        bcdb = j.data.bcdb.get("ffcontent")


# let's take the blog actor ?
