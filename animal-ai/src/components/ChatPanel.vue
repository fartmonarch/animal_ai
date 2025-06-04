<template>
    <div class="chat-page">
        <div class="chat-header">
            <img src="../assets/logo.png" class="logo" alt="logo" />
            <div class="title-box">
                <h1>我是 PetAI</h1>
                <p>你的宠物健康问诊小助手</p>
            </div>
        </div>

        <div class="chat-body">
            <div v-if="messages.length > 1" class="chat-messages">
                <div v-for="(msg, index) in messages" :key="index" :class="['chat-msg', msg.role]">
                    <div class="bubble">{{ msg.content }}</div>
                </div>
            </div>

            <div class="chat-input">
                <input v-model="question" placeholder="请输入宠物健康问题..." @keyup.enter="handleSubmit" />
                <button @click="handleSubmit">发送</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const question = ref('')
const messages = ref([
    {
        role: 'ai',
        content: '你好，我是PetAI动物健康助手，有什么可以帮你的吗？'
    }
])

const handleSubmit = async () => {
    if (!question.value.trim()) return

    messages.value.push({ role: 'user', content: question.value })
    const userQuestion = question.value
    question.value = ''

    messages.value.push({ role: 'ai', content: '🤖 正在思考中...' })
    try {
        const res = await axios.post('http://localhost:5000/ask', {
            question: userQuestion
        })
        messages.value.pop() // 移除 "思考中"
        messages.value.push({ role: 'ai', content: res.data.answer })
    } catch (e) {
        messages.value.pop()
        messages.value.push({ role: 'ai', content: '❌ 出现错误，请稍后再试。' })
    }
}
</script>

<style scoped>
.chat-page {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #f7f9fc;
    font-family: 'Segoe UI', sans-serif;
}

.chat-header {
    display: flex;
    align-items: center;
    padding: 20px;
    background: white;
    border-bottom: 1px solid #e0e0e0;
}

.logo {
    height: 48px;
    margin-right: 15px;
}

.title-box h1 {
    margin: 0;
    font-size: 20px;
    color: #333;
}

.title-box p {
    margin: 0;
    color: #888;
    font-size: 14px;
}

.chat-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 20px;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 20px;
}

.chat-msg {
    display: flex;
    margin-bottom: 12px;
}

.chat-msg.user {
    justify-content: flex-end;
}

.chat-msg.ai {
    justify-content: flex-start;
}

.bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    background: #e1f5fe;
    color: #333;
    line-height: 1.5;
    word-break: break-word;
}

.chat-msg.user .bubble {
    background: #d1f0e8;
}

.chat-input {
    display: flex;
    gap: 10px;
}

.chat-input input {
    flex: 1;
    padding: 12px;
    font-size: 16px;
    border-radius: 20px;
    border: 1px solid #ccc;
}

.chat-input button {
    background: #4a90e2;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 20px;
    cursor: pointer;
    transition: 0.3s;
}

.chat-input button:hover {
    background: #357ab9;
}

@media (max-width: 768px) {
    .chat-body {
        padding: 10px;
    }

    .chat-input input {
        font-size: 14px;
    }

    .chat-input button {
        padding: 10px 16px;
        font-size: 14px;
    }
}
</style>
