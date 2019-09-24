from Jumpscale import j


class caldav_actor(j.baseclasses.threebot_actor):
    def _init(self, **kwargs):
        pass
    
    def add_event(self, username, title, content):
        """
        ```in
        name = (S)
        do_token = (S)
        do_project_name = (S)
        ssh_key = (S)
        ```
        This actor method is used to add event (only used to add invitation)
        """
        user_path = f"/var/lib/radicale/collections/collection-root/{username}"
        calendars = j.sal.bcdbfs.list_files_and_dirs(user_path) 
        if calendars:
            calendar = calendar[0]
            j.sal.bcdbfs.write_file(f"{calendar}/{title}", content)
        
        
