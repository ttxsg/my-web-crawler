import asyncio
import re
import google.generativeai as genai
from crawl4ai import AsyncWebCrawler

# 配置 API 密钥
genai.configure(api_key="AIzaSyDFcOopTKMXLiDf-5IfvT1TFJJ5X0CjeKU")

async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        # 爬取网页内容
        result = await crawler.arun(url="https://36kr.com/p/3058349754115460")
        
        # 获取原始 markdown 内容
        raw_markdown = result.markdown_v2.raw_markdown
        
        # 正则表达式提取正文内容
        text_content = re.findall(r'##?.*?([\s\S]+?)(?=36氪经授权发布)', raw_markdown)
        
        # 合并所有正文内容
        if text_content:
            body = "\n".join(text_content).strip()
        else:
            body = "未找到正文部分"
        
        print("提取的正文内容：")
        print(body)
        
        # 通过 Google Gemini 模型生成总结
        try:
            # 创建模型实例
            model = genai.GenerativeModel("gemini-1.5-flash")
            # 生成总结
            summary_response = model.generate_content(f"Summarize the following news: {body}")
            print("\n总结：")
            print(summary_response.text)
        except Exception as e:
            print(f"生成总结时出错: {e}")

# 在 Jupyter Notebook 或 IPython 环境中使用 await 代替 asyncio.run()
await main()
