import os
import requests
import base64
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pdf2image import convert_from_path

app = Flask(__name__)
CORS(app)  # 添加CORS支持
UPLOAD_FOLDER = 'uploads'
IMAGE_FOLDER = 'output_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# 全局变量存储上下文
global_context = ""


# ========== PDF转图片 ==========
def pdf_to_images(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    image_paths = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.jpg')]
    if image_paths:
        return sorted(image_paths)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i + 1}.jpg")
        img.save(img_path, 'JPEG')
        image_paths.append(img_path)
    return image_paths


# ========== 百度OCR ==========
def get_baidu_token(api_key, secret_key):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    response = requests.post(url, params=params)
    return response.json().get("access_token")


def ocr_image(image_path, access_token):
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read())
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {"image": img_data}
    response = requests.post(url, data=data, headers=headers)
    return response.json()


def batch_ocr(image_paths, access_token):
    all_text = ""
    for img_path in image_paths:
        txt_path = img_path.replace('.jpg', '.txt')
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                page_text = f.read()
        else:
            result = ocr_image(img_path, access_token)
            words = [item['words'] for item in result.get('words_result', [])]
            page_text = "\n".join(words)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(page_text)
        all_text += page_text + "\n"
    return all_text


# ========== DeepSeek问答 ==========
def ask_deepseek(question, context, api_key):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个动物初诊助手，面向普通宠物主人，用通俗易懂的语言回答问题。"},
            {"role": "user", "content": f"参考以下资料：{context}\n\n问题：{question}"}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    if "choices" in resp_json:
        return resp_json["choices"][0]["message"]["content"]
    else:
        return f"出错了，API返回：{resp_json}"


# ========== Flask 路由 ==========
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    pdf = request.files['pdf']
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(pdf_path)
    # 转图片
    image_paths = pdf_to_images(pdf_path, IMAGE_FOLDER)
    return jsonify({'msg': f'PDF上传并转换为{len(image_paths)}张图片成功！'})


@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        baidu_api_key = request.form['baidu_api_key']
        baidu_secret_key = request.form['baidu_secret_key']
        access_token = get_baidu_token(baidu_api_key, baidu_secret_key)
        image_paths = [os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER) if f.endswith('.jpg')]

        # 更新全局上下文
        global global_context
        global_context = batch_ocr(image_paths, access_token)

        return jsonify({'msg': 'OCR识别完成！', 'context': global_context})
    except Exception as e:
        return jsonify({"msg": f"❗ OCR识别失败：{str(e)}"}), 500


@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        question = data.get("question", "")

        if not question.strip():
            return jsonify({"answer": "❗ 请提供一个有效的问题。"}), 400

        if not global_context:
            return jsonify({"answer": "❗ 请先上传PDF并进行OCR识别。"}), 400

        # 使用全局存储的上下文
        answer = ask_deepseek(question, global_context, os.getenv('DEEPSEEK_API_KEY'))
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"❗ 发生错误：{str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
