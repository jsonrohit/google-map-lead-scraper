from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
from dotenv import load_dotenv
from app.models.llm import get_llm
from app.tools.search_place import search_place

load_dotenv()





# Initialize LLM
llm = get_llm()

tools_by_name = {tool.name: tool for tool in [search_place]}

llm_with_tools =llm.bind_tools([search_place])
user_input = input("Press Enter to continue...")
response = llm_with_tools.invoke(user_input)
print("Result for user input:", f"{response.tool_calls}")

for tool_call in response.tool_calls:
    tool = tools_by_name[tool_call["name"]]
    print(f"Invoking tool '{tool_call['name']}' with arguments:", f"{tool_call['args']}")

    result = tool.invoke(tool_call["args"])

    print(f"Result for tool '{tool_call['name']}':", f"{result}")




# # Define the expected JSON structure
# parser = JsonOutputParser(pydantic_object={
#     "type": "object",
#     "properties": {
#         "name": {"type": "string"},
#         "price": {"type": "number"},
#         "features": {
#             "type": "array",
#             "items": {"type": "string"}
#         }
#     }
# })

# # Create a simple prompt
# prompt = ChatPromptTemplate.from_messages([
#     ("system", """Extract product details into JSON with this structure:
#         {{
#             "name": "product name here",
#             "price": number_here_without_currency_symbol,
#             "features": ["feature1", "feature2", "feature3"]
#         }}"""),
#     ("user", "{input}")
# ])

# # Create the chain that guarantees JSON output
# chain = prompt | llm | parser

# def parse_product(description: str) -> dict:
#     result = chain.invoke({"input": description})
#     print(json.dumps(result, indent=2))

        
# # Example usage
# description = """The Kees Van Der Westen Speedster is a high-end, single-group espresso machine known for its precision, performance, 
# and industrial design. Handcrafted in the Netherlands, it features dual boilers for brewing and steaming, PID temperature control for 
# consistency, and a unique pre-infusion system to enhance flavor extraction. Designed for enthusiasts and professionals, it offers 
# customizable aesthetics, exceptional thermal stability, and intuitive operation via a lever system. The pricing is approximatelyt $14,499 
# depending on the retailer and customization options."""

# parse_product(description)