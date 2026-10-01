from langchain_core.prompts import PromptTemplate

def get_search_place_template():
    search_place_template = PromptTemplate(
        input_variables=["query"],
        template="Search for the place: {query}"
    )
    return search_place_template.format(query="{query}")