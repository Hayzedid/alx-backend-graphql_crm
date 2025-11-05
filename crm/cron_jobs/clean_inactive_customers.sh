#!/bin/bash

# Customer cleanup script - removes customers with no orders since a year ago
# Logs the number of deleted customers with timestamp

# Get current directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project directory
cd "$PROJECT_ROOT"

# Log file path
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Execute Django command to delete inactive customers
# Customers are considered inactive if they have no orders in the last year
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer, Order
from django.utils import timezone
from datetime import timedelta
import sys

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since one year ago
inactive_customers = Customer.objects.exclude(
    orders__order_date__gte=one_year_ago
).distinct()

# Count and delete
count = inactive_customers.count()
inactive_customers.delete()

print(count)
" 2>/dev/null)

# Check if command was successful
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Successfully deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] Error: Failed to delete inactive customers" >> "$LOG_FILE"
fi
