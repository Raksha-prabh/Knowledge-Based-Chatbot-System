# Ray: Multi-Tool AI Assistant

A Python-based chatbot framework powered by the Groq AI API that orchestrates real-time external tools and maintains a persistent local memory system.

## Features

* **Dynamic Tool Orchestration:** Automatically triggers external APIs for live data without manual routing.
* **Real-Time Weather Tracking:** Extracts live temperatures, wind speeds, and regional metrics using the Open-Meteo API.
* **Pop-Culture Search:** Fetches TV show and movie summaries, genres, and ratings via the TVMaze API.
* **Global Holiday Calendar:** Checks upcoming bank and national holidays for specific countries using Nager.Date.
* **Local Memory Cache:** Uses a JSON knowledge base to store conversations, saving API costs by instantly answering repeated questions.

## Technologies Used

* Python
* Groq AI API (Llama 3 Engine)
* Flask (Web Framework)
* JSON Persistence Storage
* HTML5 / CSS3 (Frontend)

## Use Case

This system serves as a lightweight template for building zero-maintenance, serverless AI assistants capable of gathering live real-time information.
