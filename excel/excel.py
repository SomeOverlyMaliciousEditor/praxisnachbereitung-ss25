# save_as_csv.py 
import pandas as pd 
from datetime import datetime 
 
xlsx_path = "Praxis Nachbereitung Übung Tag 1.xlsx" 
sheet     = "C.2-Gesamt"
out_path  = f"exports/gesamttabelle_{datetime.now():%Y-%m-%d}.csv" 
 
df = pd.read_excel(xlsx_path, sheet) 
df.columns = [c.strip() for c in df.columns] 
df.to_csv(out_path, index=False, sep=";", encoding="utf-8") 
print(f"Export ok → {out_path}")
