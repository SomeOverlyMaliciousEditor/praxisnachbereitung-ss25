erDiagram 
  Person ||--o{ Assignment: leiht
  Device ||--o| Assignment: herausgabe
  
  Person {
   int Person-ID PK
   string vorname
   string name
  }
  Device {
   int Device-ID PK
   string Typ
   date Kaufdatum
   currency Kaufpreis
  }
  Assignment {
   int Assignment-ID PK
   int Person-ID FK
   int Device-ID FK
   date Assignment_Date
   date Return-Date }
