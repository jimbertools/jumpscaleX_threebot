from Jumpscale import j


class Package(j.baseclasses.threebot_package):
    def _init(self, *args, **kwargs):
       self.bcdb = self._package.threebot_server.bcdb_get('appstore')

    def prepare(self):
        """
        Dependencies
        """
         #write 4 apps to database
        bcdb = j.data.bcdb.get('appstore')
        appModel = bcdb.model_get(url='appstore.app')

        appsList = [{"appname" : "Mail", "installed" : False, "description" : "3bot-to-3bot mail service. Convenience of e-mail meets privacy, no man in the middle.", "image" : "upcoming"},
                    {"appname" : "Contacts", "installed" : False, "description" : "Your personal contacts list, integration with other apps possible.", "image" : "upcoming"},
                    {"appname" : "Calendar", "installed" : False, "description" : "Standard private calendar.", "image" : "upcoming"},
                    {"appname" : "Wallet", "installed" : False, "description" : "TFT, BTC, GFT, ... Keep them safe, keep them here.", "image" : "upcoming"},
                    {"appname" : "Browser", "installed" : False, "description" : "Private browsing without limits.", "image" : "upcoming"},
                    {"appname" : "FF Connect", "installed" : False, "description" : "Peer to peer and group video conferencing, straight from the browser.", "image" : "upcoming"}]

        appsInDb = appModel.iterate()

        for application in appsList:
            found = False
            for installedApp in appsInDb:
                print("application " + application['appname'])
                print("installedap " + installedApp.appname)
                if application['appname'] == installedApp.appname:
                    found = True
                    break
            if not found:
                application = appModel.new(application)
                application.save()
                
                
        
    def start(self):
        self.bcdb.models_add(path=self.package_root + '/models')
        self.gedis_server.actors_add(path=self.package_root + '/actors')
        
    def stop(self):
        pass

    def uninstall(self):
        """
        Remove Dependencies
        """
        # clear database
