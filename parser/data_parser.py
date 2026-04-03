from parser.csv_parser import parse_llm_csv_output
from parser.json_parser import parse_llm_json_output

def parse_llm_output(output, format='csv'):
    """
    Dispatches to the appropriate parser based on the format.
    """
    if format == 'json':
        return parse_llm_json_output(output)
    else:
        return parse_llm_csv_output(output)
