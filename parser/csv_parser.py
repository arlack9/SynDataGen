import re
import pandas as pd

def parse_llm_csv_output(output):
    """
    Robustly parse LLM output to extract a pandas DataFrame from CSV, handling extra text and malformed rows.
    """
    print("Parsing CSV output...")
    try:
        lines = output.strip().split('\n')
        header_index = next((i for i, line in enumerate(lines) if ',' in line and all(c.isalnum() or c in ['_', ',', ' ', '"'] for c in line.strip())), -1)
        if header_index == -1:
            raise ValueError("Could not find a valid CSV header.")
        clean_lines = lines[header_index:]
        header = [h.strip().strip('"') for h in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', clean_lines[0])]
        num_columns = len(header)
        data = []
        for row in clean_lines[1:]:
            if not row.strip():
                continue
            vals = [val.strip().strip('"') for val in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', row)]
            if len(vals) > num_columns:
                first_part = vals[:num_columns - 1]
                last_part = ", ".join(vals[num_columns - 1:])
                corrected_vals = first_part + [last_part]
                data.append(corrected_vals)
            elif len(vals) == num_columns:
                data.append(vals)
        if not data:
            raise ValueError("No valid data rows could be parsed.")
        return pd.DataFrame(data, columns=header)
    except Exception as e:
        print(f"Error parsing LLM output: {e}\n--- Raw Output ---\n{output}\n------------------")
        raise
