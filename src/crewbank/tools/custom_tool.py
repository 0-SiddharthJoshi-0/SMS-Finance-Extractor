import os
import json
import pandas as pd
from typing import Type, List, Dict
from typing import Type, List, Dict, ClassVar
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# ---------------- CSV Reader Tool -------------------------------------------------
class CSVReaderToolInput(BaseModel):
    filepath: str = Field(..., description="Path to the Excel file.")

class CSVReaderTool(BaseTool):
    tool_only: ClassVar[bool] = True
    name: str = "Excel Reader Tool"
    description: str = "Reads an Excel file and returns a list of dicts for each row."
    args_schema: Type[BaseModel] = CSVReaderToolInput

    def _run(self, filepath: str) -> List[Dict]:
        try:
            base_path = os.path.abspath(__file__)
        except NameError:
            base_path = os.getcwd()

        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(base_path))))

        possible_paths = [
            filepath,
            os.path.join(workspace_root, filepath),
            os.path.abspath(filepath),
            os.path.join(workspace_root, "knowledge", "TransactionMemo.csv"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                try:
                    if path.lower().endswith('.csv'):
                        df = pd.read_csv(path, dtype=str)
                    else:
                        df = pd.read_excel(path, dtype=str)
                    df = df.fillna('')
                    return df.to_dict(orient='records')
                except Exception as e:
                    print(f"[ExcelReaderTool] Failed reading {path}: {e}")
                    continue

        raise FileNotFoundError(f"File not found or couldn't be read. Tried: {possible_paths}")
    

# ----------------------------- NER TOOL ----------------------------------------------
# Load BERT model and tokenizer for NER (loaded once)
BERT_MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "knowledge", "bert-sms-ner-2")
try:
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(BERT_MODEL_PATH)
    ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
except Exception as e:
    print(f"[NERTool] Failed to load BERT model: {e}")
    ner_pipeline = None

class NERToolInput(BaseModel):
    data: List[Dict] = Field(..., description="List of dicts with SMS data.")
    output_json: str = Field('SMS_NER.json', description="Path to output JSON file.")

class NERTool(BaseTool):
    name: str = "NER Tool"
    description: str = "Performs NER on SMS data using a trained BERT model and writes to JSON, including the Date column if present."
    args_schema: Type[BaseModel] = NERToolInput

    def _run(self, data: List[Dict], output_json: str = 'SMS_NER.json') -> str:
        if not isinstance(data, list) or not data:
            raise ValueError("[NERTool] 'data' must be a non-empty list of dicts.")
        if ner_pipeline is None:
            raise RuntimeError("[NERTool] BERT NER pipeline is not available.")

        extracted = []
        id_order = []

        # Mapping from entity labels to output fields
        label_map = {
            "AMOUNT": "Amount",
            "CURRENCY": "Currency",
            "CREDITORDEBIT": "Credit_or_Debit",
            "ACCOUTNO": "AccoutNo",
            "BALANCE": "Balance",
            "LOCATION": "Location"
        }
        output_fields = ["Amount", "Currency", "Credit_or_Debit", "AccoutNo", "Balance", "Location"]

        for row in data:
            if not isinstance(row, dict):
                continue
            row = {k: str(v) for k, v in row.items()}
            sms_text = row.get("SMS", "")
            row_id = row.get("ID")
            date_val = row.get("Date", "N/A")
            if not row_id:
                continue
            id_order.append(str(row_id))

            # Run NER
            try:
                entities = ner_pipeline(sms_text)
                print(f"[NERTool][DEBUG] Entities for '{sms_text}': {entities}")
            except Exception as e:
                print(f"[NERTool] BERT NER failed for ID {row_id}: {e}")
                entities = []

            # Map entities to output fields (take the first occurrence for each field)
            ner_result = {field: "N/A" for field in output_fields}
            for ent in entities:
                label = ent.get("entity_group") or ent.get("entity")
                if label and (label.startswith("B-") or label.startswith("I-")):
                    label = label[2:]
                value = ent.get("word") or ent.get("entity_text")
                mapped_field = label_map.get(label.replace('_','').upper())
                if mapped_field and mapped_field != "Credit_or_Debit" and ner_result[mapped_field] == "N/A":
                    ner_result[mapped_field] = value
            # Custom logic for Credit_or_Debit
            if "credited" in sms_text.lower():
                ner_result["Credit_or_Debit"] = "credited"
            elif "debited" in sms_text.lower():
                ner_result["Credit_or_Debit"] = "debited"
            else:
                ner_result["Credit_or_Debit"] = "N/A"
            ner_result["ID"] = str(row_id)
            ner_result["Date"] = date_val
            extracted.append(ner_result)

        if not extracted:
            raise ValueError("[NERTool] No valid rows processed.")

        # Write to JSON if .json extension, else fallback to CSV
        if output_json.endswith('.json'):
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(extracted, f, ensure_ascii=False, indent=2)
        else:
            import pandas as pd
            df = pd.DataFrame(extracted)
            df["ID"] = df["ID"].astype(str)
            df = df.set_index("ID").loc[id_order].reset_index()
            df.to_csv(output_json, index=False, na_rep="N/A")

        return output_json

if __name__ == "__main__":
    # print("[NERTool][DEBUG] Running direct test of NERTool with sample data...")
    # sample_data = [
    #     {
    #         "ID": "1",
    #         "SMS": "Dear Customer AED 173.00 was credited to your account *535. Your available account balance is AED 9054.32"
    #     },
    #     {
    #         "ID": "2",
    #         "SMS": "Trx. of AED 50.00 on your a/c ****0535 at ABU DHABI NATIONAL OIL ABU DHABI AE. Avl Bal is AED 12956.50"
    #     },
    #     {
    #         "ID": "3",
    #         "SMS": "Dear Customer ATM Cash Withdrawal for AED 100.00 was debited from your account ****0535. Your Avl Bal is AED 12777.75."
    #     },
    #     {
    #         "ID": "4",
    #         "SMS": "Dear Customer AED 310.00 was debited from your account ****0535. Your available account balance is AED 22.60"
    #     },
    #     {
    #         "ID": "5",
    #         "SMS": "Dear Customer AED 16000.00 was credited to your account ****0535. Your available account balance is AED 16022.60"
    #     }
    # ]
    # tool = NERTool()
    # results = tool._run(data=sample_data, output_json="test_SMS_NER.json")
    # print("\n[NERTool][DEBUG] Final mapped results:")
    # for res in results:
    #     print(res)
    # print("[NERTool][DEBUG] Test run complete. Check test_SMS_NER.json and terminal output.")
    pass
