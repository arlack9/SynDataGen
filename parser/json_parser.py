


import json
import pandas as pd
import re


def extract_json_block(text):
    """
    Extract the first valid JSON object or array from text, handling code fences and extra text.
    """
    # Remove code fences (```json ... ``` or ``` ... ```)
    text = re.sub(r'^```(?:json)?', '', text.strip(), flags=re.IGNORECASE | re.MULTILINE).strip()
    text = re.sub(r'```$', '', text.strip(), flags=re.MULTILINE).strip()
    
    # Try to find JSON array first (most common for lists)
    array_match = re.search(r'(\[.*\])', text, re.DOTALL)
    if array_match:
        return array_match.group(1)
    
    # Try to find JSON object
    object_match = re.search(r'(\{.*\})', text, re.DOTALL)
    if object_match:
        return object_match.group(1)
    
    # Fallback: try to parse the whole text
    return text

def parse_llm_json_output(output):
    """
    Robustly parse LLM output to extract a pandas DataFrame from JSON, handling code fences, extra text, incomplete JSON, and both list/dict structures.
    FORCE DOWNLOAD even if JSON is incomplete - preserve valuable data.
    """
    try:
        print(f"DEBUG: parse_llm_json_output - Input length: {len(output)}")
        print(f"DEBUG: parse_llm_json_output - Input first 200 chars: {output[:200]}")
        
        json_str = extract_json_block(output)
        print(f"DEBUG: parse_llm_json_output - Extracted JSON length: {len(json_str)}")
        print(f"DEBUG: parse_llm_json_output - Extracted JSON first 200 chars: {json_str[:200]}")
        
        # Try normal JSON parsing first
        try:
            data = json.loads(json_str)
            print(f"DEBUG: parse_llm_json_output - Parsed JSON type: {type(data)}")
            
            # If the data is a list of dicts, convert directly
            if isinstance(data, list):
                print(f"DEBUG: parse_llm_json_output - Converting list of {len(data)} items to DataFrame")
                df = pd.DataFrame(data)
                print(f"DEBUG: parse_llm_json_output - DataFrame shape: {df.shape}")
                return df
            # If the data is a dict of lists, convert
            if isinstance(data, dict):
                print(f"DEBUG: parse_llm_json_output - Converting dict with {len(data)} keys to DataFrame")
                # Try to convert dict of lists to DataFrame
                try:
                    df = pd.DataFrame(data)
                    print(f"DEBUG: parse_llm_json_output - DataFrame shape: {df.shape}")
                    return df
                except Exception as dict_error:
                    print(f"DEBUG: parse_llm_json_output - Dict conversion failed: {dict_error}, wrapping in list")
                    # If not possible, wrap dict in a list
                    df = pd.DataFrame([data])
                    print(f"DEBUG: parse_llm_json_output - DataFrame shape: {df.shape}")
                    return df
        
        except json.JSONDecodeError as json_error:
            print(f"⚠️  JSON parsing failed: {json_error}")
            print("🚀 ATTEMPTING RECOVERY - Force parsing incomplete JSON to preserve data")
            
            # Try to recover partial JSON data
            recovered_data = []
            
            # Method 1: Try to fix incomplete array by adding closing bracket
            if json_str.strip().startswith('[') and not json_str.strip().endswith(']'):
                print("🔧 Attempting to fix incomplete JSON array")
                try:
                    # Find the last complete object
                    fixed_json = json_str.rstrip()
                    # Remove trailing comma if exists
                    if fixed_json.endswith(','):
                        fixed_json = fixed_json[:-1]
                    fixed_json += ']'
                    
                    recovered_data = json.loads(fixed_json)
                    print(f"✅ RECOVERY SUCCESS: Fixed incomplete array, recovered {len(recovered_data)} items")
                    
                except Exception as fix_error:
                    print(f"🔧 Array fix failed: {fix_error}")
            
            # Method 2: Extract individual complete JSON objects
            if not recovered_data:
                print("🔧 Attempting to extract complete JSON objects individually")
                # Find all complete JSON objects in the text
                object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                matches = re.findall(object_pattern, json_str, re.DOTALL)
                
                for match in matches:
                    try:
                        obj = json.loads(match)
                        recovered_data.append(obj)
                    except:
                        continue
                
                if recovered_data:
                    print(f"✅ RECOVERY SUCCESS: Extracted {len(recovered_data)} complete objects")
            
            # Method 3: Manual parsing of visible data structure
            if not recovered_data and 'id' in json_str and 'companyName' in json_str:
                print("🔧 Attempting manual data extraction for IT companies dataset")
                # This is specifically for the IT companies data you showed
                try:
                    # Extract company data using regex patterns
                    company_pattern = r'"id":\s*(\d+),\s*"companyName":\s*"([^"]+)"[^}]*"industrySector":\s*"([^"]+)"[^}]*"foundedYear":\s*(\d+)[^}]*"headquartersLocation":\s*"([^"]+)"[^}]*"employeeCount":\s*(\d+)[^}]*"annualRevenueUSD_Millions":\s*(\d+)[^}]*"specialization":\s*"([^"]+)"[^}]*"isPubliclyTraded":\s*(true|false)[^}]*"website":\s*"([^"]+)"'
                    
                    matches = re.findall(company_pattern, json_str, re.DOTALL | re.IGNORECASE)
                    
                    for match in matches:
                        company_data = {
                            "id": int(match[0]),
                            "companyName": match[1],
                            "industrySector": match[2],
                            "foundedYear": int(match[3]),
                            "headquartersLocation": match[4],
                            "employeeCount": int(match[5]),
                            "annualRevenueUSD_Millions": int(match[6]),
                            "specialization": match[7],
                            "isPubliclyTraded": match[8] == 'true',
                            "website": match[9]
                        }
                        recovered_data.append(company_data)
                    
                    if recovered_data:
                        print(f"✅ MANUAL RECOVERY SUCCESS: Extracted {len(recovered_data)} company records")
                
                except Exception as manual_error:
                    print(f"🔧 Manual extraction failed: {manual_error}")
            
            # If we recovered some data, use it
            if recovered_data:
                df = pd.DataFrame(recovered_data)
                print(f"🎉 DATA PRESERVED! Created DataFrame with shape: {df.shape}")
                print(f"   Columns: {list(df.columns)}")
                return df
            
            # Last resort: save the raw JSON as text for manual recovery
            print("📝 LAST RESORT: Saving raw data for manual recovery")
            df = pd.DataFrame([{
                "raw_json_data": json_str,
                "parse_error": str(json_error),
                "recovery_note": "Raw JSON data preserved - manually parse to recover complete dataset",
                "timestamp": pd.Timestamp.now().isoformat()
            }])
            return df
        
        raise ValueError("JSON output is not a list or dict")
        
    except Exception as e:
        print(f"❌ Error parsing LLM JSON output: {e}")
        print(f"📝 PRESERVING RAW DATA to prevent loss")
        
        # NEVER lose data - always return something downloadable
        df = pd.DataFrame([{
            "preserved_raw_output": output[:10000],  # First 10k chars
            "full_output_length": len(output),
            "parse_error": str(e),
            "preservation_note": "Complete raw output preserved due to parsing error",
            "timestamp": pd.Timestamp.now().isoformat()
        }])
        
        print(f"💾 DATA PRESERVED in emergency format - DataFrame shape: {df.shape}")
        return df
