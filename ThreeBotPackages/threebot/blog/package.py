from Jumpscale import j
from os.path import dirname, abspath, join, splitext
import re
import unicodedata

__version__ = "0.0.1"


class BlogLoader(j.baseclasses.object):

    __jslocation__ = "j.tools.blogloader"

    def _init(self, **kwargs):
        self.blog = kwargs["blog"]
        self.meta = kwargs["meta"]
        self.dest = kwargs["dest"]
        self.blog_name = kwargs["blog_name"]
        self.repo_url = kwargs["repo_url"]
        self.post_model = kwargs["post_model"]
        self.posts_dir_path = j.sal.fs.joinPaths(self.dest, self.meta.get("posts_dir", "posts"))

    def remove_date(self, filename):
        return re.sub(r"(\d+\-)+", "", filename)

    def published_date(self, filename):
        found = re.findall(r"^(\d+\-\d+\-\d+)", filename)
        if found:
            return found[0]
        else:
            today = j.data.time.epoch
            return j.data.time.epoch2pythonDate(today).replace("/", "-")

    def slugify(self, string):
        """
        Slugify a unicode string.
        Example:
            >>> slugify(u"Héllø Wörld")
            u"hello-world"
        """
        string = self.remove_date(string)
        return re.sub(
            r"[-\s]+",
            "-",
            re.sub(r"[^\w\s-]", "", unicodedata.normalize("NFKD", string).encode("ascii", "ignore").decode())
            .strip()
            .lower(),
        )

    # populate posts
    def create_blog(self):
        self.blog.metadata.blog_title = self.meta.get("blog_title", "blog title")
        self.blog.metadata.blog_description = self.meta.get("blog_description", "blog desc")
        self.blog.metadata.author_name = self.meta["author_name"]
        self.blog.metadata.author_email = self.meta["author_email"]
        self.blog.metadata.author_image = self.meta["author_image_filename"]
        self.blog.metadata.posts_dir = self.posts_dir_path

        sidebar_links = self.blog.metadata.sidebar_links
        sidebar_social_links = self.blog.metadata.sidebar_social_links
        sidebar_navlinks = self.blog.metadata.nav_links

        for link_obj in self.meta.get("sidebar_links", []):
            if link_obj not in sidebar_links:
                sidebar_links.append(link_obj)
        for link_obj in self.meta.get("sidebar_social_links", []):
            if link_obj not in sidebar_social_links:
                sidebar_social_links.append(link_obj)
        for link_obj in self.meta.get("nav_links", []):
            if link_obj not in sidebar_navlinks:
                sidebar_navlinks.append(link_obj)

        self.blog.metadata.github_username = self.meta["github_username"]
        self.blog.metadata.posts_per_page = int(self.meta.get("posts_per_page", "3"))
        self.blog.metadata.github_repo_url = self.repo_url
        self.blog.metadata.blog_name = self.blog_name
        self.blog.posts = []
        self.blog.save()

    def create_posts(self):
        posts = j.sal.fs.listFilesInDir(self.posts_dir_path)
        for post in posts:
            basename = j.sal.fs.getBaseName(post)
            basename = splitext(basename)[0]
            content = j.sal.fs.readFile(post)
            parsed = j.data.markdown.document_get(content)
            meta = parsed.meta

            post_title = self.remove_date(basename)

            the_title = post_title
            if "title" in meta:
                the_title = meta["title"][0]
            get_post = self.post_model.find(title=the_title)

            if get_post:
                post_obj = get_post[0]
            else:
                post_obj = self.post_model.new()

            post_obj.title = the_title
            post_obj.slug = self.slugify(post_title)
            post_obj.content_with_meta = content
            post_obj.content = parsed.strip_meta(content)

            tags = meta.get("tags", [""])[0]
            tags = [t.strip() for t in tags.split(",")]
            post_obj.tags = tags

            the_author_name = meta.get("author_name", [self.blog.metadata.author_name])[0]
            the_author_email = meta.get("author_email", [self.blog.metadata.author_email])[0]
            the_author_image = meta.get("author_image", [self.blog.metadata.author_image])[0]

            post_obj.author_name = the_author_name
            post_obj.author_email = the_author_email
            post_obj.author_image = the_author_image

            post_obj.save()
            # print("POST INFO: ", post_obj)

            self.blog.posts.append(post_obj)
            self.blog.save()

    def create_pages(self):
        pages_dir_path = j.sal.fs.joinPaths(self.dest, self.meta.get("pages_dir", "pages"))
        pages = j.sal.fs.listFilesInDir(pages_dir_path)
        for post in pages:
            basename = j.sal.fs.getBaseName(post)
            basename = splitext(basename)[0]
            content = j.sal.fs.readFile(post)
            parsed = j.data.markdown.document_get(content)
            meta = parsed.meta

            post_title = self.remove_date(basename)

            the_title = post_title
            if "title" in meta:
                the_title = meta["title"][0]

            get_post = self.post_model.find(title=the_title)
            if get_post:
                post_obj = get_post[0]
            else:
                post_obj = self.post_model.new()

            post_obj.title = meta.get("title", [the_title])[0]
            post_obj.slug = self.slugify(post_title)
            post_obj.content_with_meta = content
            post_obj.content = parsed.strip_meta(content)
            tags = meta.get("tags", [""])[0]
            tags = [t.strip() for t in tags.split(",")]
            post_obj.tags = tags
            post_obj.save()
            print("POST INFO: ", post_obj)

            self.blog.pages.append(post_obj)
            self.blog.save()


class Package(j.baseclasses.threebot_package):
    def _init(self, **kwargs):
        self.branch = kwargs["package"].branch or "master"

        # load models
        self.bcdb = j.data.bcdb.system
        models_location = j.sal.fs.joinPaths(self.package_root, "models")
        self.bcdb.models_add(models_location)
        self.blog_dest = ""

    def prepare(self, blog_name, repo_url):
        """
        is called at install time
        :return:
        """
        self.blog_name = blog_name
        self.blog_dest = dest = j.clients.git.pullGitRepo(repo_url)

        # JSX> j.sal.fs.listDirsInDir(dest)
        # ['/sandbox/code/gitlab/xmonader/sample-blog-jsx/.git', '/sandbox/code/gitlab/xmonader/sample-blog-jsx/posts']
        # JSX> j.sal.fs.listFilesInDir(dest)
        # ['/sandbox/code/gitlab/xmonader/sample-blog-jsx/metadata.yml']
        # link_model = self.bcdb.model_get(url="jumpscale.blog.link")
        # metadata = self.bcdb.model_get(url="jumpscale.blog.metadata")

        post_model = self.bcdb.model_get(url="jumpscale.blog.post")
        blog_model = self.bcdb.model_get(url="jumpscale.blog")

        # dirs = j.sal.fs.listDirsInDir(dest)
        files = j.sal.fs.listFilesInDir(dest)
        metafiles = [f for f in files if j.sal.fs.getBaseName(f) == "metadata.yml"]
        if metafiles:
            metafile = metafiles[0]
        else:
            raise j.exceptions.RuntimeError("no metadata.yml file found in the repo.")
        meta = j.data.serializers.yaml.load(metafile)

        found = blog_model.find(name=self.blog_name)
        if not found:
            blog = blog_model.new()
            blog.name = self.blog_name
        else:
            blog = found[0]

        # population
        blogobj = BlogLoader(
            blog=blog, meta=meta, dest=dest, post_model=post_model, blog_name=self.blog_name, repo_url=repo_url
        )
        blogobj.create_blog()
        blogobj.create_posts()
        blogobj.create_pages()

        self.gedis_server.actors_add(j.sal.fs.joinPaths(self.package_root, "actors"))

    def start(self):
        """
        called when the 3bot starts
        :return:
        """
        server = self.openresty
        j.builders.runtimes.nodejs.install()

        server.install()
        server.configure()

        website = server.websites.get("blog")
        website.ssl = False
        website.port = 8084
        locations = website.locations.get("blog")

        # website_location_assets = locations.locations_static.new()
        # website_location_assets.name = f"blogs_static"
        # website_location_assets.path_url = f"/blog/static"
        # fullpath = j.sal.fs.joinPaths(self.package_root, "sapper-blog", "static")
        # website_location_assets.path_location = fullpath

        website_location_assets = locations.locations_static.new()
        website_location_assets.name = f"blog_{self.blog_name}_assets"
        website_location_assets.path_url = f"/blog/{self.blog_name}/assets"
        fullpath = j.sal.fs.joinPaths(self.blog_dest, "assets")
        website_location_assets.path_location = fullpath

        ## START BOTTLE ACTORS ENDPOINT
        rack = j.servers.rack.get()
        app = j.servers.gedishttp.get_app()
        rack.bottle_server_add(name="gedishttp", port=9201, app=app)

        proxy_location = locations.locations_proxy.new()
        proxy_location.name = "gedishttp"
        proxy_location.path_url = "/actors"
        proxy_location.ipaddr_dest = "0.0.0.0"
        proxy_location.port_dest = 9201
        proxy_location.scheme = "http"
        ## END BOTTLE ACTORS ENDPOINT

        proxy_location = locations.locations_proxy.new()
        proxy_location.name = "nodeapp"
        proxy_location.path_url = f"/"

        proxy_location.ipaddr_dest = "0.0.0.0"
        proxy_location.port_dest = 3000
        proxy_location.scheme = "http"

        locations.configure()
        website.configure()

        server.start()

    def stop(self):
        """
        called when the 3bot stops
        :return:
        """
        pass

    def uninstall(self):
        """
        called when the package is no longer needed and will be removed from the threebot
        :return:
        """
        # TODO: clean up bcdb ?
        pass
