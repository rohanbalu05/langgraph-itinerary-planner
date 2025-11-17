# ✈️ AI Travel Itinerary Planner

*A search-augmented, locally powered travel itinerary generator.*

---

## 📌 Overview

The **AI Travel Itinerary Planner** creates personalized travel itineraries using a multi-step agent pipeline.
It takes user preferences, performs real-time web search, converts the results into an optimized prompt, and uses a locally hosted LLM to generate a final itinerary.

---

## 🧠 How It Works

### **1. User Preferences → Search Queries**

The user’s travel goals (budget, cuisine, culture, places, duration, etc.) are transformed by a **Query Converter** into clear search queries.

---

### **2. Automated Web Search (Twaily Agent)**

These queries are sent to a web-search agent that gathers relevant, up-to-date information such as:

* popular places
* food recommendations
* cultural highlights
* timings & travel tips

---

### **3. Prompt Generator**

A Python function processes the collected search results and converts them into an **effective prompt** for the LLM.
This step ensures the model receives structured, accurate context.

---

### **4. Local LLM → Final Itinerary**

The refined prompt is sent to a **locally hosted LLM**, which produces:

* day-wise itinerary
* places to visit
* cultural insights
* food spots
* travel timings & suggestions

This approach avoids hallucinations and ensures the itinerary is based on real-world data.

---

## ✨ Features

* Real-time information using automated search
* Search-augmented itinerary generation
* Local LLM for speed, privacy, and cost-efficiency
* Clean, dark-themed UI
* Modular agent pipeline (query → search → prompt → LLM)

---
