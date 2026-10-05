from langchain_core.prompts import PromptTemplate

def get_search_place_template():
    search_place_template = PromptTemplate(
        input_variables=["query"],
        template="Search for the place: {query}"
    )
    return search_place_template.format(query="{query}")


def data_formatter_template():
    return """
                    You are a lead-generation data formatter. Use only the supplied scraped records.

                    Return the results ONLY as a valid JSON array. Each business must be an object with exactly these fields:
                    - name
                    - phone
                    - website
                    - address
                    - email
                    - social_media

                    Example format:
                    [
                    {
                        "name": "business name",
                        "phone": "contact number",
                        "website": "https://businesswebsite.com",
                        "address": "Delhi",
                        "email": "contact@business.com",
                        "social_media": "https://socialmedia.com/business"
                    }
                    ]

                    Do not add markdown, explanations, comments, or any other fields. If a field is unavailable, use null.
                    """