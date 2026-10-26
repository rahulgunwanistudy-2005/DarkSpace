<script lang="ts">
  import '@fontsource/ibm-plex-sans/400.css';
  import '@fontsource/ibm-plex-sans/500.css';
  import '@fontsource/ibm-plex-mono/400.css';
  import '@fontsource-variable/bodoni-moda/opsz.css';
  import '@fontsource-variable/bodoni-moda/opsz-italic.css';
  import '../lib/tokens.css';
  let { children } = $props();
</script>

{@render children()}
