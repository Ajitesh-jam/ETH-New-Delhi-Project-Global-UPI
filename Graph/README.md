# Substreams Data Export System

This system automatically exports data from the PostgreSQL database (created by substreams-sink-sql) to local JSON and CSV files for analysis and monitoring.

## 🚀 Quick Start

### Prerequisites
- Docker with PostgreSQL running (from substreams setup)
- Python virtual environment with required packages

### Install Dependencies
```bash
cd /Users/ajitesh/Desktop/ETH-New-Delhi-Project-Global-UPI
source .venv/bin/activate
pip install psycopg2-binary pandas
```

## 📊 Usage

### One-time Export
Export all current data from the database:
```bash
cd Graph/
source ../.venv/bin/activate
python load_data.py
```

### Continuous Monitoring
Monitor and export data every 60 seconds:
```bash
python load_data.py --monitor
```

Monitor and export data every 30 seconds:
```bash
python load_data.py --monitor --interval 30
```

### Simulate Sample Data
For testing purposes, add sample data to the database:
```bash
python simulate_data.py
```

## 📁 Output Structure

All exported files are saved to `exported_data/` directory:

### Data Files
- `{table_name}_data.json` - JSON format with all records
- `{table_name}_data.csv` - CSV format for spreadsheet analysis

### Tables Exported
- **`instructions_data`** - Main instruction records
- **`transfers_data`** - Token transfer events
- **`mints_data`** - Token minting events
- **`burns_data`** - Token burning events  
- **`initialized_accounts_data`** - New account creation events
- **`_blocks__data`** - Block information
- **`_cursor__data`** - Cursor/progress tracking

### Summary Files
- **`export_summary.json`** - Export statistics and metadata
- **`sample_queries.json`** - Useful SQL queries for analysis

## 🔍 Data Analysis

### Using CSV Files
Import CSV files into:
- Excel/Google Sheets for basic analysis
- Pandas for Python analysis
- Any data visualization tool

### Using JSON Files  
Perfect for:
- Web applications
- API responses
- JavaScript-based analysis
- Direct import into databases

### Sample Analysis Queries
Check `exported_data/sample_queries.json` for ready-to-use SQL queries:

1. Recent transfers analysis
2. Transfer volume categorization  
3. Most active accounts
4. Minting activity trends
5. Account initialization patterns

## 🗄️ Database Connection

Default connection settings:
- **Host**: localhost
- **Port**: 5432  
- **Database**: substreams
- **User**: postgres
- **Password**: password

To modify connection, edit `DB_CONFIG` in `load_data.py`.

## 📈 Example Output

```
📊 EXPORT SUMMARY
============================================================
Export Time: 2025-09-27T05:38:05.722366
Total Records: 50
Table Breakdown:
  - instructions: 10 rows
  - transfers: 15 rows  
  - mints: 8 rows
  - burns: 5 rows
  - initialized_accounts: 6 rows
  - _blocks_: 5 rows
  - _cursor_: 1 rows
Files saved to: /path/to/exported_data
============================================================
```

## 🔄 Automation

### Cron Job Example
Run export every hour:
```bash
# Add to crontab: crontab -e
0 * * * * cd /Users/ajitesh/Desktop/ETH-New-Delhi-Project-Global-UPI/Graph && source ../.venv/bin/activate && python load_data.py
```

### Background Monitoring
For 24/7 monitoring:
```bash
# Start monitoring in background
nohup python load_data.py --monitor --interval 300 > export.log 2>&1 &
```

## 🛠️ Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL Docker container is running:
   ```bash
   docker ps | grep postgres
   ```
2. Restart container if needed:
   ```bash
   docker start postgres-db
   ```

### Empty Data
If tables are empty:
1. Check if substreams-sink-sql is running with auth token
2. Use `simulate_data.py` to add sample data for testing

### Permission Errors
Ensure write permissions for export directory:
```bash
chmod -R 755 exported_data/
```

## 📋 File Formats

### JSON Format
```json
{
  "_block_number_": 158569587,
  "_block_timestamp_": "2025-09-27T04:37:57.114137", 
  "instruction_id": "instruction_0_xiauau1c",
  "from": "ombcMNamClMmiZ8R0p5rOUtqCj75NvZDfcCQGYjBbGHD",
  "to": "l9QVTxpb2CNa2ylHNnmRL40B1XP9mn2wMNECmAUlpk33",
  "amount": 35.106722
}
```

### CSV Format  
```csv
_block_number_,_block_timestamp_,instruction_id,from,to,amount
158569587,2025-09-27T04:37:57.114137,instruction_0_xiauau1c,omb...,l9Q...,35.106722
```

## 🎯 Integration with Substreams

This export system works with the substreams-sink-sql setup:

1. **Start PostgreSQL**: `docker run --name postgres-db ...`
2. **Run Substreams Sink**: `substreams-sink-sql from-proto "$DSN" solana-spl-token@latest` 
3. **Export Data**: `python load_data.py --monitor`

The system automatically detects new data and exports it for analysis!
