<script>
  export let tags = [];
  export let title = "";

  import { stores } from "@sapper/app";
  const { preloading, page, session } = stores();
  export let username = $page.params.theuser;
</script>

<style>
  ul {
    margin: 0 0 1em 0;
    line-height: 1.5;
  }
  li {
    text-align: -webkit-match-parent;
  }
  .list-inline {
    padding-left: 0;
    list-style: none;
  }
  .widget.tags .tag {
    padding: 5px 25px;
    border: 1px solid #ddd;
    margin: 5px 0;
    color: #777;
    font-size: 0.75em;
    text-transform: uppercase;
    font-weight: 600;
    text-decoration: none;
    border-radius: 50px;
  }
</style>

<header>
  <h3>{title}</h3>
</header>
<div class="widget tags">

  <ul class="list-inline">
    {#each tags as tag}
      <li class="list-inline-item">
        <a href="blog/{username}/tags/{tag}">#{tag}</a>
      </li>
    {/each}

  </ul>
</div>
