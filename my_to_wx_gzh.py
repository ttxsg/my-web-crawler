import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup
import asyncio
from crawl4ai import AsyncWebCrawler
import re
import google.generativeai as genai



# 从环境变量中读取邮件配置
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")
recipient_email2 = os.getenv("RECIPIENT_EMAIL2")
appid = os.getenv("APPID_WX")
appsecret = os.getenv("APPSECRET_WX")
recipient_emails = [
    os.getenv("RECIPIENT_EMAIL"),
    "2310100910@qq.com"
]

# 从环境变量中读取 API 密钥
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# 定义需要爬取的网址和对应的主题
urls = [
    ("https://tophub.today/n/Q1Vd5Ko85R", "前沿科技 AI 速览：36K 热点全梳理"),
    ("https://tophub.today/n/WnBe01o371", "这些内容最容易10万+？AI 盘点今日爆款话题"),
    ("https://tophub.today/n/Y2KeDGQdNP","好用不踩雷，少数派热门科技与工具推荐"),
    ("https://tophub.today/n/NKGoRAzel6", "解锁实用利器：吾爱破解今日热门软件与工具分享"),
    ("https://tophub.today/n/WYKd6jdaPj", "豆瓣小组精选每日更新：今天的有趣分"),
    ("https://tophub.today/n/rYqoXQ8vOD","Github:今日热门项目")
]

# 定义生成总结的异步函数
async def generate_summary(url: str):
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)

        # 假设 `result.markdown.raw_markdown` 是你的原始markdown字符串
        raw_markdown = result.markdown.raw_markdown

        # 正则表达式提取从第一个标题到“36氪经授权发布”之前的所有正文内容
        # text_content = re.findall(r'##?.*?([\s\S]+?)(?=36氪经授权发布)', raw_markdown)
        # text_content = re.findall(r'##?\s?.*?([\s\S]+?)(?=36氪经授权发布|原创出品|(?=##))', raw_markdown)
        text_content = re.findall(r'##?\s?.*?([\s\S]+?)(?=36氪经授权发布|原创出品|轻触阅读原文|(?=##))', raw_markdown)
        if text_content:
            body = "\n".join(text_content).strip()
        else:
            body = "未找到正文部分"

        # 通过 Google Gemini 模型生成总结
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            summary_response = model.generate_content(f"用中文总结下面的文章,排除网页元素和网站信息等无关内容,最终给我html格式的总结，其中我不需要标题，重点内容，你可以给颜色样式，我不需要开头的```html 和结尾的```: 根据下面的内容开始进行{body}")
            return summary_response.text
        except Exception as e:
            print(f"生成总结时出错: {e}")
            return "未能生成总结"

# 遍历每个网址和对应的主题
for url, subject in urls:
    # 初始化邮件内容
    email_content = ""

    # 发送请求并检查是否成功
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
    
    if response.status_code == 200:
        # 使用 BeautifulSoup 解析 HTML 页面
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找包含热点数据的 table 标签
        table = soup.find('table', class_='table')
        
        if table:
            hotspots = []

            # 获取所有的行
            rows = table.find_all('tr')

            for row in rows:
                # 获取每一行的各个列
                cols = row.find_all('td')
                
                # 确保这一行有足够的列数
                if len(cols) >= 3:
                    # 提取标题（第二列）、链接和访问量（第三列）
                    title_tag = cols[1].find('a')
                    if title_tag:
                        title = title_tag.get_text(strip=True)  # 获取标题文本
                        link = title_tag['href']  # 获取链接

                        # 获取访问量（第三列）
                        views = cols[2].get_text(strip=True)

                        # 保存提取的信息
                        hotspots.append({
                            'title': title,
                            'link': link,
                            'views': views
                        })

            # 输出爬取到的数据
            if hotspots:
                for idx, hotspot in enumerate(hotspots, 1):
                    # 使用HTML格式化，标题带样式
                    email_content +=f"<div style='font-size:24px; color:#2F4F4F; background-color:#e0f7fa; border-radius:3px; padding:1px; display:block; width: 100%; text-align: left;margin: 0;'><b>{idx}: {hotspot['title']}</b></div>"
                    # 链接带样式
                    email_content += f"<font style='font-size:16px; color:#FF6347;'>链接: <a href='{hotspot['link']}' target='_blank'>{hotspot['link']}</a></font><br>"
  
                    # 调用异步函数生成总结
                    summary = asyncio.run(generate_summary(hotspot['link']))
                  
                    # 总结部分带样式
                    email_content += f"<font style='font-size:16px; color:#333333;'>总结: {summary}</span></font><br>"
                    email_content += '<hr style="border: 1px solid #ccc; margin: 20px 0;">'  # 使用水平线分隔不同热点数据
            else:
                email_content = f"没有找到任何{subject}热点信息"
        else:
            email_content = f"未找到{subject}目标表格"
    else:
        email_content = f"请求失败，状态码: {response.status_code}"
    # 请求数据
    data = {
        "secret": "your-secret-key",
        "action": "draft",
        "appid": appid,
        "appsecret": appsecret,
        "draft": {
            "articles": [
                {
                    "article_type": "news",
                    "title": subject,
                    "digest": subject,
                    "content": email_content,  # 这里赋值
                    "thumb_media_id": 0,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                }
            ]
        }
    }
    # 请求 Cloudflare Workers 服务
    url = "https://lingering-base-ecf8.zhengxinlilili.workers.dev/"  # Cloudflare Worker 的 URL
    response = requests.post(url, json=data)
    
    # 处理响应
    if response.status_code == 200:
        result = response.json()
        if 'message' in result:
            print(result['message'])
        else:
            print("Failed to create draft.")
    else:
        print(f"Failed to create draft. Status Code: {response.status_code}")
    # 创建邮件对象
    message = MIMEMultipart()
    message["From"] = sender_email
    # message["To"] = recipient_email
    # 将收件人列表转换为逗号分隔的字符串
    
    message["To"] = ",".join(recipient_emails)
    message["Subject"] = f"{subject}"

    # 附加文本内容
    message.attach(MIMEText(email_content, "plain", "utf-8"))
    
    # 将收件人列表转换为逗号分隔的字符串
    
    # 邮件发送
    try:
        # 连接到 QQ 的 SMTP 服务器
        with smtplib.SMTP("smtp.qq.com", 587) as server:
            server.starttls()  # 启用加密传输
            server.login(sender_email, sender_password)  # 登录
            
              # 发送邮件
            server.sendmail(sender_email, recipient_emails, message.as_string())
        print(f"邮件发送成功！({subject})")
    except Exception as e:
        print(f"邮件发送失败: {e}")

  
