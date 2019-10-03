<script>
  export let header = "";
  export let links = [];
</script>

{#if header}
  <h3>{header}</h3>
{/if}

{#if links}
  <ul>
    {#each links as link}
      <li>
        <span>

          {#if link.faclass}
            <i class={link.faclass}>
              <a href={link.link}>{link.title}</a>
            </i>
          {:else}
            <a href={link.link}>{link.title}</a>
            <!-- else content here -->
          {/if}
        </span>
      </li>
    {/each}
  </ul>
{/if}
