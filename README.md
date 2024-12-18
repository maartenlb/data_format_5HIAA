# 5HIAA Data Reformatter

## Overview
This script processes and reformats 5-HIAA data related to plasma and urine collection, aiming to detect correlations between these two measurements. The data files provided for demonstration are dummy data, but the script is designed to handle real-world data effectively. It has already been applied successfully in real-world use cases involving unorganized datasets.

The script is a little messy and not computationally efficient (no problem, as it only needs to be ran once every 6 months). This script was made as a favour to a friend in med school! ;)

## Key Features
- **Reformats Data**: Aligns plasma and urine data into a unified structure for easier analysis.
- **Handles Patient-Specific Data**: Ensures each measurement is paired correctly with its respective patient.
- **Edge Case Management**: Accounts for irregularities in data formats and mismatched entries.
- **Time-Sensitive Pairing**: Only considers measurements taken within **six months** of each other as valid pairs.
- **Modular Design**: Facilitates seamless integration of new data for future scalability.

## Usage
1. **Input Files**:  
   - The script expects data files in a specific format. Ensure plasma and urine datasets are prepared as per the examples provided in the dummy files.

2. **Execution**:  
   - Run the script in a Python environment. Modify the data file paths in the script as necessary.
