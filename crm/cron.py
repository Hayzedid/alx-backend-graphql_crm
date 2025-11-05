from datetime import datetime
import requests
import json

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
            # Query the GraphQL hello field to verify endpoint is responsive
            graphql_query = {
                "query": "{ hello }"
            }
            
            response = requests.post(
                'http://localhost:8000/graphql',
                json=graphql_query,
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('hello'):
                    heartbeat_message += " - GraphQL endpoint responsive"
                else:
                    heartbeat_message += " - GraphQL endpoint error"
            else:
                heartbeat_message += f" - GraphQL endpoint HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            heartbeat_message += f" - GraphQL endpoint unreachable: {str(e)}"
        except Exception as e:
            heartbeat_message += f" - GraphQL check failed: {str(e)}"
        
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

def update_low_stock():
    """
    Execute UpdateLowStockProducts mutation via GraphQL endpoint.
    Logs updated product names and new stock levels.
    """
    try:
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        
        # GraphQL mutation to update low stock products
        mutation_query = {
            "query": """
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
            """
        }
        
        response = requests.post(
            'http://localhost:8000/graphql',
            json=mutation_query,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            mutation_result = data.get('data', {}).get('updateLowStockProducts', {})
            
            if mutation_result.get('success'):
                updated_products = mutation_result.get('updatedProducts', [])
                
                with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                    f.write(f"[{timestamp}] Low stock update successful\n")
                    
                    if updated_products:
                        for product in updated_products:
                            f.write(f"[{timestamp}] Updated: {product['name']} - New stock: {product['stock']}\n")
                    else:
                        f.write(f"[{timestamp}] No products required stock updates\n")
            else:
                error_msg = mutation_result.get('message', 'Unknown error')
                with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                    f.write(f"[{timestamp}] Low stock update failed: {error_msg}\n")
        else:
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(f"[{timestamp}] HTTP Error {response.status_code}: {response.text}\n")
                
    except Exception as e:
        timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(f"[{timestamp}] Exception in update_low_stock: {str(e)}\n")
