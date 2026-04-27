from mcp.server.fastmcp import resources
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fastmcp.tools import tool




class AdobeSchemaScraper:
    def __init__(self):
        self.base_link = "https://experienceleague.adobe.com/en/toc/campaign-classic-help.plain.html"
        self.domain = "https://experienceleague.adobe.com"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.tag_urls = None
        self.tag_list = None
        pass
    
    def get_doc_links(self):
        try:
            response = requests.get(self.base_link, headers=self.headers)
            soup = BeautifulSoup(response.content, "html.parser")
            developers_guide = soup.find('a', string="Work with schemas").find_parent('li')
            schema_det = developers_guide.ul.find_all("li")[:5]
            url_list = {}
            for li in schema_det:
                link_tag = li.find('a')
                if link_tag:
                    relative_url = link_tag.get('href')
                    full_url = urljoin(self.domain, relative_url)
                    url_name = link_tag.get_text()
                    url_list[url_name] = full_url
            return url_list
    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def get_tags(self):
        if self.tag_list:
            return self.tag_list
        response = requests.get(self.base_link, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        developers_guide = soup.find('a', string="Elements and attributes").find_parent('li')
        schema_det = developers_guide.ul.find_all("li")[1:]
        self.tag_list=[]
        for li in schema_det:
            link_tag = li.find('a')
            if link_tag:
                self.tag_list.append(link_tag.get_text())
        return self.tag_list

    def get_tag_links(self):
        try:
            response = requests.get(self.base_link, headers=self.headers)
            soup = BeautifulSoup(response.content, "html.parser")
            developers_guide = soup.find('a', string="Elements and attributes").find_parent('li')
            schema_det = developers_guide.ul.find_all("li")[1:]
            url_list = {}
            for li in schema_det:
                link_tag = li.find('a')
                if link_tag:
                    relative_url = link_tag.get('href')
                    full_url = urljoin(self.domain, relative_url)
                    url_name = link_tag.get_text()
                    url_list[url_name] = full_url
            self.tag_urls = url_list
            return url_list
        except Exception as e:
            print(f"❌ Error: {e}")
    
    @tool
    def get_tag_attributes(self , tag:str) -> str:
        try:
            if self.tag_urls is None:
                self.get_tag_links()
            
            response = requests.get(self.tag_urls[tag], headers=self.headers)
            soup = BeautifulSoup(response.content , "html.parser")
            print(soup)
            attributes = soup.find("h2", id=lambda t: "attributes" in t).find_next_sibling("p")
            
            return attributes.get_text()
        except Exception as e:
            return f"[ERROR]: {e}"

        