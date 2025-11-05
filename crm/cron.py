from datetime import datetime
import requests
import json
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Log heartbeat message every 5 minutes to confirm CRM application health.
    Optionally queries GraphQL hello field to verify endpoint responsiveness.
    """
    try:
        # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # Basic heartbeat message
        heartbeat_message = f"{timestamp} CRM is alive"
        
        # Optional: Test GraphQL endpoint responsiveness
        try:
            # Setup GraphQL client
            transport = RequestsHTTPTransport(
                url="http://localhost:8000/graphql",
                use_json=True,
            )
            client = Client(transport=transport, fetch_schema_from_transport=False)
            
            # Query the GraphQL hello field to verify endpoint is responsive
            query = gql("{ hello }")
            result = client.execute(query)
            
            if result.get('hello'):
                heartbeat_message += " - GraphQL endpoint responsive"
            else:
                heartbeat_message += " - GraphQL endpoint error"
                
        except Exception as e:
            heartbeat_message += f" - GraphQL endpoint unreachable: {str(e)}"
        
        # Append to log file (does not overwrite)
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(heartbeat_message + '\n')
            
    except Exception as e:
        # Fallback logging in case of any errors
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        error_message = f"{timestamp} CRM heartbeat error: {str(e)}"
        
        try:
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(error_message + '\n')
        except:
            # If file writing fails, at least print to console
            print(error_message)

def updatelowstock():
    """
    Execute UpdateLowStockProducts mutation via GraphQL endpoint.
    Logs updated product names and new stock levels.
    """
    try:
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # Setup GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # GraphQL mutation to update low stock products
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    success
                    message
                    updatedProducts {
                        id
                        name
                        stock
                    }
                }
            }
        """)
        
        result = client.execute(mutation)
        mutation_result = result.get('updateLowStockProducts', {})
        
        if mutation_result.get('success'):
            updated_products = mutation_result.get('updatedProducts', [])
            
            with open('/tmp/lowstockupdates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] Low stock update successful\n")
                
                if updated_products:
                    for product in updated_products:
                        f.write(f"[{timestamp}] Updated: {product['name']} - New stock: {product['stock']}\n")
                else:
                    f.write(f"[{timestamp}] No products required stock updates\n")
        else:
            error_msg = mutation_result.get('message', 'Unknown error')
            with open('/tmp/lowstockupdates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] Low stock update failed: {error_msg}\n")
                
    except Exception as e:
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        with open('/tmp/lowstockupdates_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Exception in updatelowstock: {str(e)}\n")
