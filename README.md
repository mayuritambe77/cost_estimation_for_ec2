# EC2 Instance Pricing Tool

This tool fetches and analyzes pricing information for Amazon EC2 instances using the AWS Price List API.

## Prerequisites

- Python 3.7 or higher
- AWS CLI configured with appropriate credentials
- Required Python packages (install using `pip install -r requirements.txt`)

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:
```bash
aws configure
```
Enter your AWS Access Key ID, Secret Access Key, default region, and output format when prompted.

## Usage

Run the script to fetch EC2 pricing information:
```bash
python ec2_pricing.py
```

The script will:
1. Fetch pricing information for all EC2 instances
2. Save the data to a CSV file with timestamp
3. Display basic statistics about the pricing data

## Output

The script generates a CSV file named `ec2_pricing_YYYYMMDD_HHMMSS.csv` containing:
- Instance Type
- Region
- Operating System
- Price per Hour
- Unit

## Customization

You can modify the script to:
- Filter by specific instance types
- Change the operating system
- Adjust the region
- Add more pricing details

## Notes

- The pricing data is fetched in real-time from AWS
- The script uses the AWS Price List API which may have rate limits
- Make sure your AWS credentials have appropriate permissions to access pricing information