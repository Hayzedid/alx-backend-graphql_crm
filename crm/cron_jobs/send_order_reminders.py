#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

def send_order_reminders():
    """
    Query GraphQL endpoint for orders from the last 7 days and log reminders
    """
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # Calculate date 7 days ago
        seven_days_ago = datetime.now() - timedelta(days=7)
        seven_days_ago_str = seven_days_ago.isoformat()
        
        # GraphQL query to get orders from last 7 days
        query = gql("""
            query GetRecentOrders($orderDateGte: DateTime!) {
                allOrders(orderDate_Gte: $orderDateGte) {
                    edges {
                        node {
                            id
                            orderDate
                            customer {
                                id
                                name
                                email
                            }
                            totalAmount
                        }
                    }
                }
            }
        """)
        
        # Execute query
        variables = {"orderDateGte": seven_days_ago_str}
        result = client.execute(query, variable_values=variables)
        
        # Process results and log reminders
        log_file = "/tmp/order_reminders_log.txt"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Order reminders processing started\n")
            
            orders = result.get('allOrders', {}).get('edges', [])
            
            if not orders:
                f.write(f"[{timestamp}] No recent orders found\n")
            else:
                for edge in orders:
                    order = edge['node']
                    order_id = order['id']
                    customer_email = order['customer']['email']
                    customer_name = order['customer']['name']
                    order_date = order['orderDate']
                    
                    f.write(f"[{timestamp}] Order ID: {order_id}, Customer: {customer_name}, Email: {customer_email}, Date: {order_date}\n")
            
            f.write(f"[{timestamp}] Processed {len(orders)} orders\n")
        
        print("Order reminders processed!")
        
    except Exception as e:
        # Log error
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("/tmp/order_reminders_log.txt", 'a') as f:
            f.write(f"[{timestamp}] ERROR: {str(e)}\n")
        
        print(f"Error processing order reminders: {e}")
        sys.exit(1)

if __name__ == "__main__":
    send_order_reminders()
