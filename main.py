import os
import google.generativeai as genai

# 从环境变量中读取 API 密钥
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="https://36kr.com/p/3058349754115460")
        
        raw_markdown = result.markdown_v2.raw_markdown
        text_content = re.findall(r'##?.*?([\s\S]+?)(?=36氪经授权发布)', raw_markdown)
        
        if text_content:
            body = "\n".join(text_content).strip()
        else:
            body = "未找到正文部分"
        
        print("提取的正文内容：")
        print(body)
        
        # 通过 Google Gemini 模型生成总结
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            summary_response = model.generate_content(f"Summarize the following news: {body}")
            print("\n总结：")
            print(summary_response.text)
        except Exception as e:
            print(f"生成总结时出错: {e}")

# 在 Jupyter Notebook 或 IPython 环境中使用 await 代替 asyncio.run()
await main()
