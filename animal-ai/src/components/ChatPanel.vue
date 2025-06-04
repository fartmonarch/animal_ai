<template>
    <div class="chat-panel">
        <input v-model="question" placeholder="请输入您的宠物健康问题" @keyup.enter="handleSubmit" />
        <button @click="handleSubmit">提交</button>
        <div v-if="loading">🤖 AI助手思考中...</div>
        <div v-if="answer" class="answer">{{ answer }}</div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const answer = ref('')
const loading = ref(false)

const handleSubmit = async () => {
    if (!question.value.trim()) return
    loading.value = true
    answer.value = ''
    try {
        const res = await axios.post('http://localhost:5000/ask', {
            question: question.value
        })
        answer.value = res.data.answer
    } catch (e) {
        answer.value = '❌ 出现错误，请稍后再试'
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.chat-panel {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}

input {
    width: 400px;
    padding: 12px;
    font-size: 16px;
}

button {
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}

.answer {
    margin-top: 20px;
    max-width: 500px;
    text-align: left;
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 8px;
}
</style>
