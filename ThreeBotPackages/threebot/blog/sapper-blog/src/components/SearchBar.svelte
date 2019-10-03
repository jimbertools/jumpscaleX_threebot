<script>
  import axios from "axios";
  axios.defaults.headers.get["Content-Type"] = "application/json";

  import { stores } from "@sapper/app";
  const { preloading, page, session } = stores();
  export let blogName = $page.params.theuser;
  let query = "";
  let search_res = "";

  const BLOG_API = `blog/search.json`;

  export async function search_method(e) {
    if (!query) {
      alert("empty search !");
    }
    e.preventDefault();
    search_res = await axios.get(BLOG_API, {
      params: {
        blog_name: blogName,
        query: query
      }
    });
    search_res = search_res.data;
  }
</script>

<div class="col-sm-3 col-md-3 pull-right">
  <form class="navbar-form form-inline" role="search" on:submit={search_method}>
    <!-- <i class="fas fa-search" aria-hidden="true" /> -->
    <input
      class="form-control"
      type="text"
      bind:value={query}
      placeholder="Search"
      aria-label="Search" />
    <!-- <button>Search</button> -->
  </form>
</div>

{#if search_res}
  <p>Search Result</p>
  <ul>
    {#each search_res as res}
      <li>
        <a href="blog/{res.blog}/{res.type}/{res.slug}">
          {res.slug} - Type: {res.type}
        </a>
      </li>
    {/each}
  </ul>
{/if}
