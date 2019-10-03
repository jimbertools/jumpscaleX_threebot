<script>
  import Links from "./Links.svelte";
  import TagCloud from "./TagCloud.svelte";
  export let metadata = {};
  export let tags = [];
</script>

<div class="container">

  <Links header="Links" links={metadata.sidebar_links} />
  <Links header="Social" links={metadata.sidebar_social_links} />
  <TagCloud {tags} />

</div>
