import asyncio
from crawl4ai import AsyncWebCrawler, CacheMode
import re
import google.generativeai as genai

async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="https://36kr.com/p/3058349754115460")
        
        # 假设 `result.markdown_v2.raw_markdown` 是你的原始markdown字符串
        raw_markdown = result.markdown_v2.raw_markdown
        
        # 正则表达式提取从第一个标题到“36氪经授权发布”之前的所有正文内容
        # 注意：一旦遇到“36氪经授权发布”，后面的内容都不再提取，包含标题
        text_content = re.findall(r'##?.*?([\s\S]+?)(?=36氪经授权发布)', raw_markdown)
        
        # 如果匹配到正文内容
        if text_content:
            # 合并所有正文内容
            body = "\n".join(text_content).strip()
        else:
            body = "未找到正文部分"
        
        # 调用Google生成AI模型进行总结
        genai.configure(api_key="YOUR_API_KEY")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(body)  # 将文章传递给AI模型进行总结
        print(text_content)

# 使用 asyncio.run 启动异步任务
if __name__ == "__main__":
    asyncio.run(main())
