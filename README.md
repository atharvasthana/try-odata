 🔗 ISBN Book API via OData for Salesforce Connect

This project provides a live OData 4.0-compliant API built with Flask to serve ISBN book data (10,000+ records) in real time. It integrates seamlessly with Salesforce using **Salesforce Connect** to expose external objects without data replication.

---

## 📌 Features

- ✅ Serves 10,000+ ISBN records from a JSON file
- ✅ Exposes an **OData 4.0 API** endpoint with `$metadata` and data routes
- ✅ Hosted for free on [Render](https://render.com)
- ✅ Pulls large data dynamically from **Google Drive** at build time via `.sh` script
- ✅ Fully compatible with **Salesforce Connect** External Data Source
- ✅ Supports OData operations:  
  - `$top`, `$skip` for pagination  
  - `$filter` for query conditions (e.g., Title, Serial, etc.)
- ✅ Enables SOQL queries on external objects in Salesforce

---

## 📁 Project Structure
