<script lang="ts">
  let { size = 24 }: { size?: number } = $props();
</script>

<svg class="mark" width={size} height={size} viewBox="0 0 24 24" aria-hidden="true" focusable="false">
  <circle cx="12" cy="12" r="10.5" fill="none" stroke="currentColor" stroke-opacity=".35" stroke-width=".8"/>
  <path d="M12 2.5 13.4 10.6 21.5 12 13.4 13.4 12 21.5 10.6 13.4 2.5 12 10.6 10.6Z" fill="currentColor"/>
</svg>
