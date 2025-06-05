from model import model
from langchain_core.messages import HumanMessage, SystemMessage
import asyncio

class Summariser:
    def __init__(self):
        self.model = model
        self.system_prompt = """You are a helpful assistant that summarises papers. Emphasise the key points and the main contributions of the paper.
                                Make sure to cover all the sections of the paper. Generate the summary in markdown format. Paper:"""

    async def summarise_one(self, paper):
        response = await self.model.ainvoke([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=paper)
        ])
        print('done')
        return response.content

    async def summarise(self, papers):
        tasks = [self.summarise_one(paper["text"]) for paper in papers]
        return [{"summary": summary, "id": paper["id"], "title": paper["title"]} for summary, paper in zip(await asyncio.gather(*tasks), papers)]

if __name__ == "__main__":
    print(asyncio.run(Summariser().summarise(['paper1', 'paper2'])))