import os
import requests
import base64
from pdf2image import convert_from_path

# ========== 1. PDF转图片 ==========
def pdf_to_images(pdf_path, output_folder):
    """
    将PDF每一页转换为图片，保存在output_folder文件夹下。
    如果图片已存在则直接跳过。
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # 检查是否已经有图片文件
    image_paths = [os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.jpg')]
    if image_paths:
        print("检测到已存在图片，跳过PDF转图片。")
        return sorted(image_paths)
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, img in enumerate(images):
        img_path = os.path.join(output_folder, f"page_{i+1}.jpg")
        img.save(img_path, 'JPEG')
        image_paths.append(img_path)
    return image_paths

# ========== 2. 百度OCR ==========
def get_baidu_token(api_key, secret_key):
    """
    获取百度OCR的access_token
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    response = requests.post(url, params=params)
    return response.json().get("access_token")

def ocr_image(image_path, access_token):
    """
    对单张图片进行OCR识别
    """
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read())
    url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {"image": img_data}
    response = requests.post(url, data=data, headers=headers)
    return response.json()

def batch_ocr(image_paths, access_token, output_folder):
    """
    对每一页图片进行OCR识别，结果分别保存为txt文件，已识别过的直接跳过。
    返回所有页的文本合并结果。
    """
    all_text = ""
    for img_path in image_paths:
        txt_path = img_path.replace('.jpg', '.txt')
        if os.path.exists(txt_path):
            print(f"{os.path.basename(txt_path)} 已存在，跳过OCR。")
            with open(txt_path, "r", encoding="utf-8") as f:
                page_text = f.read()
        else:
            print(f"正在识别 {os.path.basename(img_path)} ...")
            result = ocr_image(img_path, access_token)
            words = [item['words'] for item in result.get('words_result', [])]
            page_text = "\n".join(words)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(page_text)
        all_text += page_text + "\n"
    return all_text

# ========== 3. DeepSeek问答 ==========
def ask_module(question, context, api_key):
    """
    调用大模型API进行问答
    """
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
    print("DeepSeek返回内容：", resp_json)
    if "choices" in resp_json:
        return resp_json["choices"][0]["message"]["content"]
    else:
        return f"出错了，API返回：{resp_json}"

# ========== 4. 主程序 ==========
def main():
    pdf_path =  r"C:\Users\Shawn7\Desktop\animals.pdf" # 你的PDF文件名
    output_folder = "output_images"
    print("正在将PDF转为图片（如已存在则跳过）...")
    image_paths = pdf_to_images(pdf_path, output_folder)
    print(f"共检测到{len(image_paths)}页图片。")

    baidu_api_key =  "RqMJi8BE4DfmqdbEjeLjdst"        # 需要更改为你的百度API Key
    baidu_secret_key =  "XsbuU30j2BYrDyeocneISJEVPt2tL4E8"   # 需要更改为你的百度Secret Key
    print("正在获取百度OCR token...")
    access_token = get_baidu_token(baidu_api_key, baidu_secret_key)
    print("正在识别图片文字（已识别过的会自动跳过）...")
    context = batch_ocr(image_paths, access_token, output_folder)
    print("文字识别完成。")

    deepseek_api_key = "sk-f22ddf0e3a7244bc9a85cb90b61b2e42" # 需要更改为你的DeepSeek API Key
    print("动物初诊AI助手已启动。")
    while True:
        question = input("请输入你的宠物健康问题（输入q退出）：")
        if question.lower() == 'q':
            break
        print("AI助手正在思考，请稍候...")
        answer = ask_deepseek(question, context, deepseek_api_key)
        print("AI助手答：", answer)

if __name__ == "__main__":
    main() 