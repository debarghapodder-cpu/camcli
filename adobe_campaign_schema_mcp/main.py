from fastmcp import FastMCP
from scraper import AdobeSchemaScraper
mcp = FastMCP(name="adobe schema mcp" , 
              instructions="You are an expert in Adobe Campaign schemas. Use these tools to find field definitions." , 
              on_duplicate="overwrite",
              version="1.0.0"
        )

schema_scraper = AdobeSchemaScraper()
# @mcp.resource(uri="adobe://doc_links" , version="1.0.0" , description="documentation links for making schema")
# def adobe_links():
#     return schema_scraper.get_doc_links()


print(schema_scraper.get_tag_attributes(tag="Compute string"))

