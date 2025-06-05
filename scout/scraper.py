import arxiv
import asyncio
from uuid import uuid4
from PyPDF2 import PdfReader
from concurrent.futures import ProcessPoolExecutor
import os
import aiohttp
import tempfile


class PaperScraper:
    def __init__(self):
        self.client = arxiv.Client()
        self.cache_dir = "./paper_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_metadata(self, query, n):
        papers = []
        results = self._search_papers(query, n)
        for result in results:
            paper_id = str(uuid4())
            papers.append({
                "id": paper_id,
                "title": result.title,
                "pdf_url": result.pdf_url,
                "result": result
            })
        return papers

    async def download_and_parse(self, paper):
        pdf_path = os.path.join(self.cache_dir, f"{paper['id']}.pdf")

        try:
            # Download PDF
            async with aiohttp.ClientSession() as session:
                async with session.get(paper["pdf_url"]) as response:
                    if response.status != 200:
                        return {
                            "id": paper["id"],
                            "title": paper["title"],
                            "text": f"[Error downloading PDF]: HTTP {response.status}"
                        }
                    
                    with open(pdf_path, 'wb') as f:
                        f.write(await response.read())

            # Parse PDF
            try:
                text = await self._parse_pdf(pdf_path)
                if not text.strip():
                    return {
                        "id": paper["id"],
                        "title": paper["title"],
                        "text": "[Error]: PDF appears to be empty or contains no text"
                    }
                return {
                    "id": paper["id"],
                    "title": paper["title"],
                    "text": text
                }
            except Exception as e:
                return {
                    "id": paper["id"],
                    "title": paper["title"],
                    "text": f"[Error parsing PDF]: {str(e)}"
                }
            finally:
                # Clean up the PDF file
                try:
                    os.remove(pdf_path)
                except:
                    pass

        except Exception as e:
            return {
                "id": paper["id"],
                "title": paper["title"],
                "text": f"[Error downloading PDF]: {str(e)}"
            }
    
    def extract_page_text(self, path, page_number):
        try:
            reader = PdfReader(path)
            if page_number >= len(reader.pages):
                return ""
            page = reader.pages[page_number]
            return page.extract_text() or ""
        except Exception as e:
            return f"[Error on page {page_number + 1}]: {str(e)}"

    async def _parse_pdf(self, filepath):
        try:
            reader = PdfReader(filepath)
            total_pages = len(reader.pages)

            if total_pages == 0:
                return "[Error]: PDF has no pages"

            loop = asyncio.get_event_loop()
            with ProcessPoolExecutor() as executor:
                tasks = [
                    loop.run_in_executor(executor, self.extract_page_text, filepath, i)
                    for i in range(total_pages)
                ]
                results = await asyncio.gather(*tasks)

            # Filter out error messages and join valid text
            valid_texts = [text for text in results if not text.startswith("[Error")]
            if not valid_texts:
                return "[Error]: Could not extract any text from the PDF"

            return "\n\n".join(valid_texts)

        except Exception as e:
            return f"[Error parsing PDF]: {str(e)}"

    def _search_papers(self, query, n):
        search = arxiv.Search(
            query=query,
            max_results=n,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        return list(self.client.results(search))


async def main():
    scraper = PaperScraper()

    papers = scraper.get_metadata("quantum computing", 2)
    print("Found papers:")
    for paper in papers:
        print("-", paper["title"])

    tasks = [scraper.download_and_parse(paper) for paper in papers]
    results = await asyncio.gather(*tasks)

    print("\nAll done.")
    print(type(results), len(results))
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
