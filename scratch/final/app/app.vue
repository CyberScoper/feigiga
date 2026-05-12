<template>
  <div class="app">
    <SiteHeader />
    <main>
      <NuxtPage />
    </main>
    <SiteFooter />
    <AiChat />
  </div>
</template>

<style>
.app { min-height: 100vh; display: flex; flex-direction: column; }
main { flex: 1; }
</style>
