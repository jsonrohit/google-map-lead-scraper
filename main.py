from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
import json
from dotenv import load_dotenv
from app.models.llm import get_llm
from app.tools.search_place import search_place
from app.services.web_scraper import scrape_website
from app.services.export_data import generate_excel_from_scraped_data

load_dotenv()


# Initialize LLM
llm = get_llm()

tools_by_name = {tool.name: tool for tool in [search_place]}

llm_with_tools =llm.bind_tools([search_place])
user_input = input("Press Enter to continue...")
response = llm_with_tools.invoke(user_input)
print("Result for user input:", f"{response.tool_calls}")

scraped_records = []

for tool_call in response.tool_calls:
    tool = tools_by_name[tool_call["name"]]
    print(f"Invoking tool '{tool_call['name']}' with arguments:", f"{tool_call['args']}")

    result = tool.invoke(tool_call["args"])

    places = result.get("places", [])
    for place in places:
        # print(f"Place: {place.get('title', 'Unknown')}")
        for key, value in place.items():
            # print(f"  {key}: {value}")
            if key == "website" and value:
                scrape_result = scrape_website(value)
                scrape_result["name"] = place.get("title")
                scraped_records.append(scrape_result)

                # print(f"    Found website URL: {value}")
                # print(f"    Scraped data from {value}: {scrape_result}")
                try:
                    readable_response = json.dumps(json.loads(scrape_result), indent=2, ensure_ascii=False)
                except (json.JSONDecodeError, TypeError):
                    readable_response = str(scrape_result)
                print(f"scrape result:\n{readable_response}")

if scraped_records:
    prompt =SystemMessage(content="""
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
                    """)
    response = llm.invoke([
        prompt,
        HumanMessage(content=json.dumps(scraped_records, indent=2)),
    ])
    response_text = response.content
    try:
        readable_response = json.dumps(json.loads(response_text), indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        readable_response = str(response_text)
    print(f"LLM response for scraped records:\n{readable_response}")

    excel_buffer = generate_excel_from_scraped_data(json.loads(readable_response))
    output_file = "scraped_leads.xlsx"
    with open(output_file, "wb") as excel_file:
        excel_file.write(excel_buffer.getvalue())
    print(f"Excel sheet saved to: {output_file}")
else:
    print("No website data was scraped; no Excel sheet was created.")

