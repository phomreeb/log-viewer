# Multi-Project JSON Log Viewer

A high-performance, interactive log viewing and analytics application built with Streamlit and DuckDB. This tool is designed to efficiently parse, filter, and visualize large-scale JSON log files across multiple projects in real-time.

## 🚀 Features

- **Blazing Fast Queries:** Powered by DuckDB, enabling high-speed querying and parsing of raw `.json` and `.log` files without pre-indexing.
- **Real-Time Monitoring:** Toggle between `Static` (historical analysis) and `Live` modes with customizable auto-refresh intervals.
- **Advanced Filtering & Search:** Drill down into your logs using Time Range, Log Levels, Search terms, and specific Log Name inclusions/exclusions.
  - *Smart Level Matching:* Automatically groups `WARN` and `WARNING` logs together for seamless querying regardless of the source format.
- **Saved Views (Shareable URLs):** All filter states (Project, File, Search, Levels, etc.) are synchronized with URL query parameters. You can instantly share a link to a specific log view with your team!
- **Interactive Analytics Dashboard:**
  - **Time Series Chart:** Track log volume over time, color-coded by log level (e.g., Red for ERROR, Green for INFO) using Plotly.
  - **Error Breakdown:** Identify problematic services instantly with a donut chart summarizing ERROR logs.
- **Developer-Friendly UI:** Inspect raw JSON payloads with a built-in copy-to-clipboard functionality and syntax highlighting.
- **Export Capabilities:** Export filtered log views directly to CSV for external reporting.

## 📋 Prerequisites

- **Python:** `>= 3.13`
- **Package Manager:** `uv` (Recommended for fast dependency resolution)

## 🛠️ Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd log-viewer
   ```

2. Install dependencies using `uv`:

   ```bash
   uv sync
   ```

## 📂 Directory Structure

The application automatically scans the `./logs` directory at the root of the project. You must organize your log files into subdirectories representing each project.

```text
log-viewer/
├── logs/
│   ├── project_a/
│   │   ├── app.log.2026-09-14
│   │   └── app.json
│   └── project_b/
│       └── error.log
├── app.py
├── pyproject.toml
└── ...
```

*Note: If the `logs/` directory does not exist, the application will create it automatically on the first run.*

## 🚀 Usage

Start the Streamlit server:

```bash
uv run streamlit run app.py
```

The application will be accessible in your browser at `http://localhost:8501`.

## 🏗️ Architecture Stack

- **[Streamlit](https://streamlit.io/):** Frontend framework for the interactive data application.
- **[DuckDB](https://duckdb.org/):** In-process SQL OLAP database management system for querying JSON logs.
- **[Plotly](https://plotly.com/):** Graphing library for rendering interactive analytics charts.
- **[Pandas](https://pandas.pydata.org/):** Data manipulation and analysis.

## 📝 License

This project is open-source and available under the [MIT License](LICENSE).
