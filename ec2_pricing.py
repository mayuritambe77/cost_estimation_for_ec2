import boto3
import json
import requests
import pandas as pd
from datetime import datetime
import os

class EC2Pricing:
    def __init__(self, region='us-east-1'):
        try:
            self.region = region
            # Initialize the pricing client with explicit credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            print(f"Using AWS credentials from: {credentials.method}")
            
            self.pricing_client = boto3.client('pricing', region_name=region)
            self.currency_code = 'USD'
            self.service_code = 'AmazonEC2'
            print(f"Successfully initialized pricing client for region: {region}")
        except Exception as e:
            print(f"Error initializing pricing client: {str(e)}")
            print("Please make sure you have configured AWS credentials using 'aws configure'")
            raise
        
    def get_ec2_pricing(self, instance_type=None, operating_system='Linux'):
        """
        Fetch EC2 pricing information for specified instance type and OS
        """
        try:
            print(f"Fetching pricing information for {instance_type if instance_type else 'all instances'}...")
            
            # First, let's try to describe the services to verify API access
            try:
                services = self.pricing_client.describe_services()
                print(f"Successfully connected to AWS Pricing API. Available services: {len(services.get('Services', []))}")
            except Exception as e:
                print(f"Error describing services: {str(e)}")
                return None
            
            # Get the price list for EC2 with simpler filters
            filters = [
                {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': self.region},
                {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            ]
            
            if instance_type:
                filters.append({'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type})
            
            print("Using filters:", json.dumps(filters, indent=2))
            
            response = self.pricing_client.get_products(
                ServiceCode=self.service_code,
                Filters=filters
            )
            
            print(f"Received response with {len(response.get('PriceList', []))} items")
            
            if not response.get('PriceList'):
                print("No pricing data found. Please check your AWS credentials and permissions.")
                return None
                
            pricing_data = []
            for product in response['PriceList']:
                try:
                    product_data = json.loads(product)
                    instance_type = product_data['product']['attributes'].get('instanceType')
                    print(f"Processing instance type: {instance_type}")
                    
                    # Extract pricing information
                    for term in product_data['terms'].get('OnDemand', {}).values():
                        for price_dimension in term['priceDimensions'].values():
                            price_data = {
                                'Instance Type': instance_type,
                                'Region': product_data['product']['attributes'].get('location'),
                                'Operating System': product_data['product']['attributes'].get('operatingSystem'),
                                'Price per Hour': price_dimension['pricePerUnit']['USD'],
                                'Unit': price_dimension['unit'],
                            }
                            pricing_data.append(price_data)
                except Exception as e:
                    print(f"Error processing product data: {str(e)}")
                    continue
            
            if not pricing_data:
                print(f"No pricing data found for the specified criteria.")
                return None
                
            return pd.DataFrame(pricing_data)
            
        except Exception as e:
            print(f"Error fetching pricing data: {str(e)}")
            print("Please check your AWS credentials and permissions.")
            return None

def main():
    try:
        # Initialize the EC2Pricing class
        ec2_pricing = EC2Pricing()
        
        # First try to get pricing for t2.micro
        print("\nTrying to fetch pricing for t2.micro...")
        pricing_df = ec2_pricing.get_ec2_pricing(instance_type='t2.micro')
        
        if pricing_df is not None and not pricing_df.empty:
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
        else:
            print("\nTrying to fetch pricing for all instances...")
            pricing_df = ec2_pricing.get_ec2_pricing()
            
            if pricing_df is not None and not pricing_df.empty:
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
            else:
                print("No pricing data was retrieved. Please check your AWS credentials and permissions.")
                print("\nTroubleshooting steps:")
                print("1. Verify your AWS credentials using 'aws configure list'")
                print("2. Make sure your AWS user has the necessary permissions")
                print("3. Check if you can access the AWS Pricing API in your region")
                print("4. Try using a different region")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your AWS configuration and try again.")

if __name__ == "__main__":
    main()