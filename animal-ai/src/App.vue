<template>
  <div class="app">
    <h1>🐾 宠物AI问诊助手</h1>
    <ChatPanel />
  </div>
</template>

<script setup>
import ChatPanel from './components/ChatPanel.vue'
</script>

<style>
body {
  margin: 0;
  font-family: 'Arial', sans-serif;
  background-color: #ffffff;
}

.app {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100px;
}

h1 {
  font-size: 32px;
  margin-bottom: 40px;
}
</style>
