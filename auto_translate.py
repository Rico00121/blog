import openai
import os
import frontmatter

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
)


# 指定 Hugo 文章目录
HUGO_CONTENT_DIR = "content/post"

def translate_text(text, target_lang="en"):
    """使用 OpenAI GPT-4 翻译文本"""
    total_length = len(text)
    translated_text = ""

    print(f"开始翻译正文...")
    # 分段翻译以显示进度
    chunk_size = 1000  # 每次翻译的字符数
    for i in range(0, total_length, chunk_size):
        chunk = text[i:i + chunk_size]
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Translate the following Chinese blog post into English while keeping the original meaning."},
                {"role": "user", "content": chunk}
            ]
        )
        translated_text += response.choices[0].message.content
        progress = min((i + chunk_size) / total_length * 100, 100)  # 确保进度不超过 100%
        print(f"正文翻译进度: {progress:.2f}%")  # 显示进度

    return translated_text

def translate_title(text):
    """使用 OpenAI GPT-4 翻译标题"""

    print(f"开始翻译标题...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Translate the following Chinese blog post title into English while keeping the original meaning."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def translate_sumary(text):
    """使用 OpenAI GPT-4 翻译摘要"""

    print(f"开始翻译摘要...")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Translate the following Chinese blog post summary into English while keeping the original meaning."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def process_hugo_post(file_path):
    """读取 Hugo 文章，翻译正文，并生成英文版本"""
    with open(file_path, "r", encoding="utf-8") as f:
        post = frontmatter.load(f)

     # 创建英文版本
    new_metadata = post.metadata
    new_metadata["title"] = translate_title(new_metadata["title"])
    new_metadata["summary"] = translate_sumary(new_metadata["summary"])

    # 提取正文并翻译
    translated_content = translate_text(post.content)

    # 生成 Hugo 英文版文件
    new_post = frontmatter.Post(translated_content, **new_metadata)
    en_file_path = file_path.replace(".zh.md", ".en.md")

    with open(en_file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(new_post))

    print(f"✅ 翻译完成: {file_path} -> {en_file_path}")

process_hugo_post(os.path.join(HUGO_CONTENT_DIR, 'kubernetes-init-problems/index.zh.md'))