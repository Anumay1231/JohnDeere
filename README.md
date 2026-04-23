# JD Dealership Executive Analytics

**Live Application:** [https://johndeere-ggfl75gs88ikngmj4psx6c.streamlit.app/](https://johndeere-ggfl75gs88ikngmj4psx6c.streamlit.app/)

## Overview
This project is a custom business intelligence dashboard built specifically for the General Manager of a multi-district tractor dealership. The goal was to replace time-consuming manual spreadsheet analysis with a "Management by Exception" approach. Instead of scrolling through thousands of rows of sales and inventory data, management can now view the most critical financial and operational risks instantly during brief daily reviews.

## How It Works
The application uses a secure, drag-and-drop interface. Users upload their raw, locally generated Excel reports. The backend Python pipeline automatically parses the files, handles inconsistent data formatting, and structures the data for immediate visual inference. 

Because the data contains sensitive business information, the application processes everything in-memory. Files are never stored on a server and are completely discarded the moment the browser session ends.

## Key Features
- **Trapped Capital Tracking:** Instantly calculates the total amount of cash tied up in unsold used tractor inventory, specifically flagging critical capital that has been sitting on the lot for over a year.
- **Sales Executive Accountability:** Ranks sales executives not just by total delivery volume, but by the financial risk of their acquired stock. It highlights the oldest and most expensive unsold units tied to each individual.
- **Used Market Economics:** Aggregates historical exchange data to determine average purchase prices, average sale prices, and overall loss rates, helping management identify poor purchasing trends.
- **Dynamic Exploration:** Provides collapsible sections with in-depth scatter plots and composite scorecards for deeper investigation only when needed.

## Technical Stack
- **Python:** Core logic and data manipulation.
- **Pandas:** Heavy lifting for data cleaning, merging, and aggregation.
- **Streamlit:** Frontend web framework for rapid deployment and interactive UI.
- **Plotly:** Rendering dynamic, customizable charts.

## Local Development
To run this project on your own machine:
```bash
pip install -r requirements.txt
streamlit run app.py
```
