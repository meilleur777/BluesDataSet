# Blues Artist Data Collector

A comprehensive data collection and analysis pipeline that traces the evolution of blues music through the web of influences between artists across generations.

## Project Overview

The Blues Artist Data Collector explores the rich tapestry of musical heritage and lineage in blues music. By systematically gathering and analyzing connections between artists, this project illuminates how musical ideas, techniques, and styles have been passed down and transformed through generations of musicians.

The project consists of two integrated components:

1. **URL Scraper**: 
   - Collects and consolidates URLs linked to individual blues artists from diverse sources
   - Processes CSV files containing artist names and web references

2. **Text Collector**:
   - Harvests rich textual information from the collected URLs
   - Focuses on biographical elements, musical style descriptions, career highlights, and collaborations
   - Employs intelligent content filtering to identify influence relationships between artists
   - Extracts mentions of musical techniques, signature styles, and innovations

3. **IR_System**:
   - Make Information Retrieval system using Boolean model.
   - Allows user to perform simple searches with Boolean opeartors.

## Long-Term Vision

The ultimate goal of this project is to create relationship graphs among blues artists. In blues music, there are clear instances of artists influencing one another, similar to how professors pass knowledge to their students. For example, Stevie Ray Vaughan was influenced by artists such as Albert King, Otis Rush, and Muddy Waters. By analyzing these relationships, we can trace how musical techniques, licks, and riffs evolved over generations.

## Project Structure

The repository is organized into two main components:

```
blues-artist-data/
├── URL_Scraper/       # Component for collecting artist URLs
├── Text_Collector/    # Component for extracting text information
├── IR_System/         # Component for Information Retrieval System
└── README.md          # This file
```

Each component has its own dedicated README.md file with specific installation and usage instructions.

## Getting Started

1. First, use the URL_Scraper component to collect artist URLs
2. Then, use the Text_Collector component to gather detailed information about each artist
3. Use IR_System component to make IR system with .txt files

See the README.md files in each component directory for detailed instructions.

There are sample input and output files in each components.

## License

This project is available for personal research and educational purposes. Always respect the terms of service of any websites you scrape.
