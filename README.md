# ALX Backend GraphQL CRM

A comprehensive Customer Relationship Management (CRM) system built with Django and GraphQL, featuring advanced mutations, filtering, and bulk operations.

## 🚀 Features

### Task 0: GraphQL Endpoint Setup
- ✅ Django project with GraphQL integration
- ✅ Basic "Hello, GraphQL!" query
- ✅ GraphiQL interface for testing

### Task 1 & 2: CRM Database with GraphQL Mutations
- ✅ **Customer Management**
  - Create single customers with validation
  - Bulk customer creation with partial success support
  - Email uniqueness validation
  - Phone number format validation
- ✅ **Product Management**
  - Create products with price and stock validation
  - Positive price enforcement
  - Non-negative stock validation
- ✅ **Order Management**
  - Create orders with customer and product associations
  - Automatic total amount calculation
  - Nested customer and product data in responses
- ✅ **Advanced Error Handling**
  - User-friendly error messages
  - Validation for all inputs
  - Transaction support for bulk operations

### Task 3: Advanced Filtering
- ✅ **Customer Filters**
  - Name and email partial matching (case-insensitive)
  - Creation date range filtering
  - Custom phone pattern filtering
- ✅ **Product Filters**
  - Name partial matching
  - Price range filtering
  - Stock level filtering
  - Low stock filter (< 10 items)
- ✅ **Order Filters**
  - Total amount range filtering
  - Order date range filtering
  - Customer name filtering
  - Product name filtering
  - Specific product ID filtering

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- graphene-django 3.0+
- django-filter 23.0+

## 🛠️ Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   cd alx-backend-graphql_crm
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Seed the database (optional):**
   ```bash
   python seed_db.py
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access GraphQL interface:**
   - Open: http://localhost:8000/graphql
   - Use GraphiQL interface for testing queries and mutations

## 🧪 Testing GraphQL Operations

### Basic Query
```graphql
{
  hello
}
```

### Create Customer
```graphql
mutation {
  createCustomer(input: {
    name: "Alice Johnson"
    email: "alice@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
    success
  }
}
```

### Bulk Create Customers
```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob Smith", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol Davis", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
    success
  }
}
```

### Create Product
```graphql
mutation {
  createProduct(input: {
    name: "Laptop"
    price: 999.99
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
    success
  }
}
```

### Create Order
```graphql
mutation {
  createOrder(input: {
    customerId: "1"
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
    success
  }
}
```

### Advanced Filtering Examples

#### Filter Customers
```graphql
{
  allCustomers(filter: { 
    nameIcontains: "Ali", 
    createdAtGte: "2025-01-01" 
  }) {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

#### Filter Products by Price Range
```graphql
{
  allProducts(filter: { 
    priceGte: 100, 
    priceLte: 1000 
  }) {
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
```

#### Filter Orders by Customer and Product
```graphql
{
  allOrders(filter: { 
    customerName: "Alice", 
    productName: "Laptop",
    totalAmountGte: 500 
  }) {
    edges {
      node {
        id
        customer {
          name
        }
        products {
          name
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

## 📁 Project Structure

```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/
│   ├── __init__.py
│   ├── settings.py          # Django settings with GraphQL config
│   ├── urls.py              # URL configuration with GraphQL endpoint
│   ├── wsgi.py
│   └── schema.py            # Main GraphQL schema
├── crm/
│   ├── __init__.py
│   ├── models.py            # Customer, Product, Order models
│   ├── schema.py            # GraphQL types, queries, mutations
│   ├── filters.py           # Django-filter classes
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── tests.py
│   └── views.py
├── manage.py
├── requirements.txt         # Project dependencies
├── seed_db.py              # Database seeding script
└── README.md               # This file
```

## 🔧 Key Features Implementation

### Validation & Error Handling
- **Email Uniqueness**: Prevents duplicate customer emails
- **Phone Format**: Validates phone numbers (+1234567890 or 123-456-7890)
- **Price Validation**: Ensures positive product prices
- **Stock Validation**: Prevents negative stock values
- **Order Validation**: Validates customer and product existence

### Advanced GraphQL Features
- **Relay-style Connections**: Pagination support for all queries
- **Custom Filters**: Complex filtering with django-filter integration
- **Nested Queries**: Access related data in single queries
- **Bulk Operations**: Efficient bulk customer creation
- **Transaction Support**: Atomic operations for data consistency

### Database Design
- **Customer Model**: Name, email (unique), phone with validation
- **Product Model**: Name, price, stock with constraints
- **Order Model**: Many-to-many relationship with products, auto-calculated totals
- **Timestamps**: Created/updated timestamps on all models

## 🎯 API Endpoints

- **GraphQL Endpoint**: `/graphql`
- **GraphiQL Interface**: `/graphql` (with graphiql=True)
- **Admin Interface**: `/admin/`

## 🧪 Sample Data

The `seed_db.py` script creates:
- 5 sample customers
- 8 sample products
- 5 sample orders with various product combinations

## 🔍 Testing & Validation

All mutations include comprehensive validation:
- Input validation with user-friendly error messages
- Database constraint enforcement
- Transaction rollback on errors
- Partial success support for bulk operations

## 📚 GraphQL Schema Features

- **Queries**: Get single items or filtered lists
- **Mutations**: Create customers, products, and orders
- **Filtering**: Advanced filtering on all models
- **Sorting**: Order results by various fields
- **Pagination**: Relay-style pagination for large datasets

## 🚀 Ready for Production

The CRM system includes:
- Proper error handling and validation
- Scalable database design
- Efficient querying with select_related/prefetch_related
- Transaction support for data integrity
- Comprehensive filtering and search capabilities
