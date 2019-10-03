<script>
  import showdown from "showdown";
  export let post;
  import { stores } from "@sapper/app";
  const { preloading, page, session } = stores();
  export let username = $page.params.theuser;
  let converter = new showdown.Converter({ metadata: true });
  converter.setFlavor("github");
  let mdtext = converter.makeHtml(post.content);

</script>

<!-- <div in:fly={{ x: -60, duration: 100 }} class="post-card-title">
 -->

<style>
.author-img {
  border-radius: 50%;
  width:50px;
  height:50px
}
</style>

<div class="post-card-header">
    <div class="post-card-title">
        <a rel="prefetch" href="blog/{username}/posts/{post.slug}">
            <span><h2>{post.title}  <span class="h6"><i class="fas fa-at"><a href="mailto:{post.author_email}" target="_top">{post.author_name}</a></i></span></h2>
        </a>
    </div>
    <div class="post-info">
        <img class="author-img" src="/blog/blog_{username}/assets/me.jpg" onerror="this.src='me.jpg'"><span class="published-at">Published at {post.published_at}</span>
    </div>

</div>
<div class="post-content">
    {@html mdtext}
</div>    
