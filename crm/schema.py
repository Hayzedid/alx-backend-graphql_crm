import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")
        filter_fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        filter_fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }
        interfaces = (graphene.relay.Node,)

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        filter_fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
            'customer__name': ['icontains'],
        }
        interfaces = (graphene.relay.Node,)

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Mutation Response Types
class CustomerMutationResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

class BulkCustomerMutationResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    success = graphene.Boolean()

class ProductMutationResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

class OrderMutationResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CustomerMutationResponse

    def mutate(self, info, input):
        try:
            # Validate email uniqueness
            if Customer.objects.filter(email=input.email).exists():
                return CustomerMutationResponse(
                    success=False,
                    errors=["Email already exists"]
                )

            # Validate phone format if provided
            if input.phone:
                phone_pattern = r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$'
                if not re.match(phone_pattern, input.phone):
                    return CustomerMutationResponse(
                        success=False,
                        errors=["Invalid phone format. Use +1234567890 or 123-456-7890"]
                    )

            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )

            return CustomerMutationResponse(
                customer=customer,
                message="Customer created successfully",
                success=True
            )

        except Exception as e:
            return CustomerMutationResponse(
                success=False,
                errors=[str(e)]
            )

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCustomerMutationResponse

    def mutate(self, info, input):
        created_customers = []
        errors = []
        
        try:
            with transaction.atomic():
                for i, customer_data in enumerate(input):
                    try:
                        # Validate email uniqueness
                        if Customer.objects.filter(email=customer_data.email).exists():
                            errors.append(f"Customer {i+1}: Email already exists")
                            continue

                        # Validate phone format if provided
                        if customer_data.phone:
                            phone_pattern = r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$'
                            if not re.match(phone_pattern, customer_data.phone):
                                errors.append(f"Customer {i+1}: Invalid phone format")
                                continue

                        customer = Customer.objects.create(
                            name=customer_data.name,
                            email=customer_data.email,
                            phone=customer_data.phone
                        )
                        created_customers.append(customer)

                    except Exception as e:
                        errors.append(f"Customer {i+1}: {str(e)}")

                return BulkCustomerMutationResponse(
                    customers=created_customers,
                    errors=errors,
                    success=len(created_customers) > 0
                )

        except Exception as e:
            return BulkCustomerMutationResponse(
                customers=[],
                errors=[str(e)],
                success=False
            )

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = ProductMutationResponse

    def mutate(self, info, input):
        try:
            # Validate price is positive
            if input.price <= 0:
                return ProductMutationResponse(
                    success=False,
                    errors=["Price must be positive"]
                )

            # Validate stock is non-negative
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                return ProductMutationResponse(
                    success=False,
                    errors=["Stock cannot be negative"]
                )

            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )

            return ProductMutationResponse(
                product=product,
                message="Product created successfully",
                success=True
            )

        except Exception as e:
            return ProductMutationResponse(
                success=False,
                errors=[str(e)]
            )

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = OrderMutationResponse

    def mutate(self, info, input):
        try:
            # Validate customer exists
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                return OrderMutationResponse(
                    success=False,
                    errors=["Invalid customer ID"]
                )

            # Validate products exist
            if not input.product_ids:
                return OrderMutationResponse(
                    success=False,
                    errors=["At least one product must be selected"]
                )

            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                return OrderMutationResponse(
                    success=False,
                    errors=["One or more invalid product IDs"]
                )

            # Create order
            order = Order.objects.create(
                customer=customer,
                order_date=input.order_date
            )

            # Add products and calculate total
            order.products.set(products)
            total_amount = sum(product.price for product in products)
            order.total_amount = total_amount
            order.save()

            return OrderMutationResponse(
                order=order,
                message="Order created successfully",
                success=True
            )

        except Exception as e:
            return OrderMutationResponse(
                success=False,
                errors=[str(e)]
            )

# Query Class
class Query(graphene.ObjectType):
    hello = graphene.String()
    
    # Basic queries
    all_customers = graphene.List(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())

    def resolve_hello(self, info):
        return "Hello, GraphQL!"

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None

# Mutation Class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Schema
schema = graphene.Schema(query=Query, mutation=Mutation)
