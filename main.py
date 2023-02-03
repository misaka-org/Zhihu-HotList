from bs4 import BeautifulSoup
import datetime
import asyncio
import logging
import httpx
import json

NOW = datetime.datetime.now()+datetime.timedelta(hours=8)


class Zhihu(object):
    """ 知乎热榜爬虫 """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    proxy = None
    timeout = None

    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            http2=True, timeout=self.timeout, headers=self.headers, verify=False, proxies=self.proxy)

    async def __access(self) -> str:
        """ 访问热榜网页, 返回HTML """
        url = "https://www.zhihu.com/billboard"
        try:
            resp = await self.client.get(url)
            assert resp.status_code == 200, f"状态码: {resp.status_code}"
        except (Exception, BaseException) as e:
            logging.warning(f"Error! {e}")
            await asyncio.sleep(60)  # 获取失败时暂停60秒
            return await self.__access()
        else:
            return resp.text

    def __handle(self, html) -> list[dict]:
        """ 解析HTML """
        soup = BeautifulSoup(html, 'html.parser')
        hotList: list[dict] = []
        data = soup.find_all('a', attrs={"class": "HotList-item"})
        for value in data:
            try:
                hotList.append({
                    'index': value.find('div', attrs={"class": "HotList-itemIndex"}).next_element.get_text().strip(),
                    'title': value.find('div', attrs={"class": "HotList-itemTitle"}).next_element.get_text().strip(),
                    'metrics': value.find('div', attrs={"class": "HotList-itemMetrics"}).next_element.get_text().strip(),
                    'img': value.find('img').get('src') if value.find('img') else None,
                    'time': f"数据更新时间: {NOW.strftime(r'%Y-%m-%d %H:%M:%S')}"
                })
            except Exception as e:
                print(f"Error! {e} {value}")
        return hotList

    async def get(self):
        """ 获取JSON格式的热榜列表 """
        html = await self.__access()
        return self.__handle(html)


if __name__ == "__main__":
    zhihu = Zhihu()
    res = asyncio.run(zhihu.get())
    with open("Zhihu-HotList.json", 'w', encoding='utf-8') as fw:
        fw.write(json.dumps(res, indent=4, ensure_ascii=False))
    with open("package.json", "w", encoding='utf-8') as fw:
        fw.write(json.dumps({
            'version': NOW.strftime(r"%Y-%m-%d %H:00")
        }, indent=4, ensure_ascii=False))
    print(f"Python Sucessed! {NOW.strftime(r'%Y-%m-%d %H:%M:%S')}")
