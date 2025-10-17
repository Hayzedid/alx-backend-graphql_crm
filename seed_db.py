#!/usr/bin/env python
"""
Database seeding script for CRM system
Run this script to populate the database with sample data
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_customers():
    """Create sample customers"""
    customers_data = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Davis", "email": "carol@example.com", "phone": "+1987654321"},
        {"name": "David Wilson", "email": "david@example.com", "phone": "987-654-3210"},
        {"name": "Eve Brown", "email": "eve@example.com", "phone": "+1122334455"},
    ]
    
    created_customers = []
    for customer_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=customer_data["email"],
            defaults=customer_data
        )
        if created:
            print(f"Created customer: {customer.name}")
        else:
            print(f"Customer already exists: {customer.name}")
        created_customers.append(customer)
    
    return created_customers

def seed_products():
    """Create sample products"""
    products_data = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Mouse", "price": Decimal("29.99"), "stock": 50},
        {"name": "Keyboard", "price": Decimal("79.99"), "stock": 25},
        {"name": "Monitor", "price": Decimal("299.99"), "stock": 15},
        {"name": "Headphones", "price": Decimal("149.99"), "stock": 30},
        {"name": "Webcam", "price": Decimal("89.99"), "stock": 20},
        {"name": "Desk Chair", "price": Decimal("199.99"), "stock": 8},
        {"name": "USB Cable", "price": Decimal("12.99"), "stock": 100},
    ]
    
    created_products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data["name"],
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name} - ${product.price}")
        else:
            print(f"Product already exists: {product.name}")
        created_products.append(product)
    
    return created_products

def seed_orders(customers, products):
    """Create sample orders"""
    orders_data = [
        {"customer_index": 0, "product_indices": [0, 1, 2]},  # Alice: Laptop, Mouse, Keyboard
        {"customer_index": 1, "product_indices": [3, 4]},     # Bob: Monitor, Headphones
        {"customer_index": 2, "product_indices": [1, 2, 5]}, # Carol: Mouse, Keyboard, Webcam
        {"customer_index": 3, "product_indices": [6, 7]},     # David: Desk Chair, USB Cable
        {"customer_index": 4, "product_indices": [0, 3, 4]}, # Eve: Laptop, Monitor, Headphones
    ]
    
    created_orders = []
    for order_data in orders_data:
        customer = customers[order_data["customer_index"]]
        order_products = [products[i] for i in order_data["product_indices"]]
        
        # Check if order already exists for this customer with these products
        existing_order = None
        for existing in customer.orders.all():
            if set(existing.products.all()) == set(order_products):
                existing_order = existing
                break
        
        if not existing_order:
            order = Order.objects.create(customer=customer)
            order.products.set(order_products)
            order.calculate_total()
            order.save()
            
            product_names = ", ".join([p.name for p in order_products])
            print(f"Created order for {customer.name}: {product_names} (Total: ${order.total_amount})")
            created_orders.append(order)
        else:
            print(f"Order already exists for {customer.name}")
            created_orders.append(existing_order)
    
    return created_orders

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    # Clear existing data (optional)
    print("\n🗑️  Clearing existing data...")
    Order.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    
    # Seed data
    print("\n👥 Creating customers...")
    customers = seed_customers()
    
    print("\n📦 Creating products...")
    products = seed_products()
    
    print("\n🛒 Creating orders...")
    orders = seed_orders(customers, products)
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Database seeding completed!")
    print(f"📊 Summary:")
    print(f"   - Customers: {Customer.objects.count()}")
    print(f"   - Products: {Product.objects.count()}")
    print(f"   - Orders: {Order.objects.count()}")
    print("\n🚀 You can now test the GraphQL API at: http://localhost:8000/graphql")
    
    # Sample queries
    print("\n📝 Sample GraphQL queries to try:")
    print("""
    # Basic hello query
    {
      hello
    }
    
    # Get all customers
    {
      allCustomers {
        edges {
          node {
            id
            name
            email
            phone
          }
        }
      }
    }
    
    # Get all products with filtering
    {
      allProducts(filter: {priceGte: 100}) {
        edges {
          node {
            id
            name
            price
            stock
          }
        }
      }
    }
    
    # Get orders with customer and product details
    {
      allOrders {
        edges {
          node {
            id
            customer {
              name
              email
            }
            products {
              name
              price
            }
            totalAmount
            orderDate
          }
        }
      }
    }
    """)

if __name__ == "__main__":
    main()
