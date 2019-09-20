from Jumpscale import j
import binascii
from io import BytesIO


class tft_explorer(j.baseclasses.threebot_actor):
    def _init(self, *args, **kwargs):
        bcdb = j.data.bcdb.get("ffbrowser")
        self.tft_ex_t = bcdb.model_get(url="ffbrowser.transaction.1")

    def launch(self, event, schema_out=None, user_session=None):
        """
        ```in
        event = (O) !calendar.people.1
        ```

        ```out
        !calendar.people.1
        ```

        """
    
    def get_cookie(self, text, schema_out=None, user_session=None):

    def set_cookie(self, text, schema_out=None, user_session=None):

    #put here the needed functions to interface with ffbrowser
