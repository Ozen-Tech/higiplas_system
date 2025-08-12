#!/usr/bin/env python3
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Test API with proper authentication
try:
    # First, login to get a token
    login_data = {
        "username": "admin@higiplas.com",
        "password": "admin123"
    }
    
    login_response = requests.post('http://localhost:8000/users/token', data=login_data)
    print(f"Login Status Code: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        access_token = token_data.get('access_token')
        print(f"Token obtained: {access_token[:20]}...")
        
        # Now test the produtos endpoint with authentication
        headers = {'Authorization': f'Bearer {access_token}'}
        produtos_response = requests.get('http://localhost:8000/produtos', headers=headers)
        
        print(f"\nProdutos API Status Code: {produtos_response.status_code}")
        
        if produtos_response.status_code == 200:
            produtos_data = produtos_response.json()
            print(f"Number of products returned: {len(produtos_data)}")
            
            if produtos_data:
                print("\nFirst product data:")
                first_product = produtos_data[0]
                for key, value in first_product.items():
                    print(f"  {key}: {value}")
        else:
            print(f"Error response: {produtos_response.text}")
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()