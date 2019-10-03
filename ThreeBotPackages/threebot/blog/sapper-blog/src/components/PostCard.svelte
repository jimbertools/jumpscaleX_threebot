<script>
  import showdown from "showdown";
  import { excerptOf } from "../_helper.js";
  export let post;
  import { stores } from "@sapper/app";
  const { preloading, page, session } = stores();
  export let username = $page.params.theuser;
  let converter = new showdown.Converter({ metadata: true });
  converter.setFlavor("github");
  let mdtext = converter.makeHtml(post.content);
  export let showExcerpt = true;
  //   let summary = mdtext
  //     .split("\n")
  //     .splice(1)
  //     .join("\n")
  //     .slice(0, 300);

  let summary = excerptOf(mdtext);
  //   import { fly } from "svelte/transition";
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
            <span><h2>{post.title}</h2> by {post.author_name}</span>
        </a>
    </div>

</div>
{#if showExcerpt}
  <div class="post-card-content">
    {@html summary}

    <a rel="prefetch" href="blog/{username}/posts/{post.slug}">

      <h5 class="continue-reading">Continue reading</h5>
    </a>
  </div>
{/if}
