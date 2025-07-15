import pdfplumber
import pandas as pd
import re
import os

folder_path = "./pdfs"
all_transactions = []

for filename in os.listdir(folder_path):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(folder_path, filename)
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                # Extract confirmation date
                match_date = re.search(r"Confirmation Date\s*:\s*(\d{1,2}/\d{1,2}/\d{4})", text)
                confirmation_date = match_date.group(1) if match_date else None

                # Extract account number and name
                match_account = re.search(r"Account Number:(.*?)Account Name:(.*)", text)
                account_number = match_account.group(1).strip() if match_account else None
                account_name = match_account.group(2).strip() if match_account else None

                
                # Extract transactions
                transaction_pattern = r"([A-Z]+)\s+(.+?)\s+(Buy|Sell)\s+([\d:APM ]+)\s+(-?[\d\.]+)\s+([\d\.]+)\s+([\d/]+)\s+([\d/]+)\s+(Agency|Principal)"
                
                for match in re.finditer(transaction_pattern, text):
                    transaction = {
                        "symbol": match.group(1),
                        "company": match.group(2).strip(),
                        "action": match.group(3),
                        "execution_time": match.group(4).strip(),
                        "quantity": float(match.group(5)),
                        "price": float(match.group(6)),
                        "trade_date": match.group(7),
                        "settle_date": match.group(8),
                        "capacity": match.group(9),
                        "confirmation_date": confirmation_date,
                        "account_number": account_number,
                        "account_name": account_name,
                        "source_file": filename,
                        "net_amount": ""
                    }

                    # Extract net amount near transaction (simplified: optional refinement needed for accuracy)
                    #net_amount_match = re.search(r"Net Amount\s*\(\$(-?[\d\.]+)\)", text)
                    #transaction["net_amount"] = float(net_amount_match.group(1)) if net_amount_match else None

                    all_transactions.append(transaction)
                    
# Convert to DataFrame
df = pd.DataFrame(all_transactions)
#net amount provided this way to avoid regex duplication
df['net_amount'] = df['quantity'] * df['price']

# Save to Excel
df.to_excel("all_company_transactions.xlsx", index=False)
