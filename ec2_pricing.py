import boto3
import json
import requests
import pandas as pd
from datetime import datetime
import os

class EC2Pricing:
    def __init__(self, region='us-east-1'):           #for us-east-1
        self.pricing_client = boto3.client('pricing', region_name=region)
        self.currency_code = 'USD'
        self.service_code = 'AmazonEC2'
        
    def get_ec2_pricing(self, instance_type=None, operating_system='Linux'):
        """
        Fetch EC2 pricing information for specified instance type and OS
        """
        try:
            # Get the price list for EC2
            response = self.pricing_client.get_products(
                ServiceCode=self.service_code,
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
                    {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                    {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                ]
            )
            
            pricing_data = []
            for product in response['PriceList']:
                product_data = json.loads(product)
                
                # Extract instance type if specified
                if instance_type:
                    if product_data['product']['attributes'].get('instanceType') != instance_type:
                        continue
                
                # Extract pricing information
                for term in product_data['terms'].get('OnDemand', {}).values():
                    for price_dimension in term['priceDimensions'].values():
                        price_data = {
                            'Instance Type': product_data['product']['attributes'].get('instanceType'),
                            'Region': product_data['product']['attributes'].get('regionCode'),
                            'Operating System': product_data['product']['attributes'].get('operatingSystem'),
                            'Price per Hour': price_dimension['pricePerUnit']['USD'],
                            'Unit': price_dimension['unit'],
                        }
                        pricing_data.append(price_data)
            
            return pd.DataFrame(pricing_data)
            
        except Exception as e:
            print(f"Error fetching pricing data: {str(e)}")
            return None

def main():
    # Initialize the EC2Pricing class
    ec2_pricing = EC2Pricing()
    
    # Get pricing for all EC2 instances
    pricing_df = ec2_pricing.get_ec2_pricing()
    
    if pricing_df is not None:
        # Save to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'ec2_pricing_{timestamp}.csv'
        pricing_df.to_csv(output_file, index=False)
        print(f"Pricing data saved to {output_file}")
        
        # Display some basic statistics
        print("\nPricing Summary:")
        print(f"Total number of instance types: {len(pricing_df['Instance Type'].unique())}")
        print(f"Average price per hour: ${pricing_df['Price per Hour'].astype(float).mean():.4f}")
        print(f"Minimum price per hour: ${pricing_df['Price per Hour'].astype(float).min():.4f}")
        print(f"Maximum price per hour: ${pricing_df['Price per Hour'].astype(float).max():.4f}")

if __name__ == "__main__":
    main() 