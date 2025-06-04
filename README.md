你的前端通过如下代码向后端发起接口请求：

```ts
const res = await axios.post('http://localhost:5000/ask', {
  question: userQuestion
})
```

---

### ✅ 所需接口格式说明（Flask 后端）

**请求接口：**

```
POST /ask
Content-Type: application/json
```

**请求体：**

```json
{
  "question": "我家猫咪今天一直呕吐，是怎么回事？"
}
```

**后端返回格式（建议）：**

```json
{
  "answer": "你描述的症状可能是猫咪肠胃炎，也可能误食异物。建议观察精神状态和排便情况，并尽快带去兽医检查。"
}
```

---

### ✅ Flask 端接口示例代码

你可以将已有 `ask_module(...)` 封装成如下 Flask 接口：

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域请求

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get("question", "")
    if not question.strip():
        return jsonify({"answer": "❗ 请提供一个有效的问题。"}), 400

    # 这里调用你的大模型问答模块
    result = ask_module(question, context, DEEPSEEK_KEY)
    return jsonify({"answer": result})

if __name__ == '__main__':
    app.run(debug=True)
```

---

如果你使用的是 `Flask + pdf转图 + OCR + 大模型问答` 流程，建议你将 `context` 缓存在内存中，并在 `/ask` 接口中引用，这样可以节省重复OCR的时间。

是否需要我帮你改写你之前的 Python 脚本，使其与这个前端接口完全兼容？
