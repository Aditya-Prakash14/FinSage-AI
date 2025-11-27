# Database Module

Complete MongoDB database implementation for FinSage AI.

## Features

- **Connection Management**: Singleton pattern with connection pooling
- **Repository Pattern**: Clean data access layer with type safety
- **Automatic Indexing**: Performance-optimized queries
- **Data Validation**: Schema validation and integrity checks
- **Migration System**: Version-controlled schema changes
- **Seeding Utilities**: Sample data generation for testing

## Structure

```
database/
├── __init__.py           # Module exports
├── mongo_config.py       # MongoDB connection management
├── repositories.py       # Data access layer (repositories)
├── seed.py              # Database seeding utilities
├── validator.py         # Health checks and validation
├── migrations.py        # Schema migration system
└── README.md           # This file
```

## Quick Start

### 1. Configure Environment

Create a `.env` file in the backend directory:

```env
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=finsage_db
```

### 2. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or install locally
# macOS
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongodb
```

### 3. Seed Database (Optional)

```bash
cd backend
python -m database.seed
```

### 4. Validate Database

```bash
python -m database.validator
```

## Usage

### Basic Connection

```python
from database import get_db, RepositoryFactory

# Get database instance
db = get_db()

# Create repositories
repo_factory = RepositoryFactory(db)
user_repo = repo_factory.get_user_repo()
txn_repo = repo_factory.get_transaction_repo()
```

### Repository Operations

#### User Repository

```python
# Create user
user_id = user_repo.create_user({
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+919876543210"
})

# Find user
user = user_repo.find_by_email("user@example.com")
```

#### Transaction Repository

```python
# Add single transaction
txn_id = txn_repo.create({
    "user_id": user_id,
    "date": datetime.utcnow(),
    "amount": -500,
    "type": "debit",
    "category": "Groceries"
})

# Batch create
txn_ids = txn_repo.batch_create([
    {"user_id": user_id, "amount": 5000, "type": "credit", ...},
    {"user_id": user_id, "amount": -200, "type": "debit", ...}
])

# Get recent transactions
transactions = txn_repo.get_recent_transactions(user_id, days=30)

# Get category summary
summary = txn_repo.get_category_summary(
    user_id,
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 12, 31)
)
```

#### Budget Repository

```python
# Create budget
budget_id = budget_repo.create_budget({
    "user_id": user_id,
    "period": "monthly",
    "total_budget": 50000,
    "categories": {
        "Groceries": 10000,
        "Transport": 5000
    }
})

# Get active budget
active_budget = budget_repo.find_active_budget(user_id)
```

#### Goal Repository

```python
# Create goal
goal_id = goal_repo.create({
    "user_id": user_id,
    "goal_name": "Emergency Fund",
    "target_amount": 100000,
    "current_amount": 0,
    "priority": 1
})

# Update progress
goal_repo.update_progress(goal_id, amount=5000)

# Get active goals
goals = goal_repo.get_active_goals(user_id)
```

## Database Schema

### Users Collection

```javascript
{
  _id: ObjectId,
  email: String (unique),
  name: String,
  phone: String,
  primary_income_source: String,
  occupation: String,
  created_at: DateTime,
  is_active: Boolean
}
```

**Indexes**: `email` (unique)

### Transactions Collection

```javascript
{
  _id: ObjectId,
  user_id: String,
  date: DateTime,
  amount: Number,  // Positive for credit, negative for debit
  type: "credit" | "debit",
  category: String,
  description: String,
  source: String,
  created_at: DateTime
}
```

**Indexes**: 
- `user_id` + `date` (compound, descending)
- `type`
- `category`

### Budgets Collection

```javascript
{
  _id: ObjectId,
  user_id: String,
  period: "weekly" | "monthly" | "quarterly",
  total_budget: Number,
  categories: Object,  // {category: amount}
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes**: `user_id` + `is_active` (compound)

### Goals Collection

```javascript
{
  _id: ObjectId,
  user_id: String,
  goal_name: String,
  target_amount: Number,
  current_amount: Number,
  deadline: DateTime,
  priority: Number (1-5),
  is_completed: Boolean,
  completed_at: DateTime,
  created_at: DateTime
}
```

**Indexes**: `user_id` + `deadline` (compound)

### Forecasts Collection

```javascript
{
  _id: ObjectId,
  user_id: String,
  forecast_type: "income" | "expense",
  forecast_data: Object,
  created_at: DateTime
}
```

## Utilities

### Seeding

```bash
# Seed with sample data (clears existing)
python -m database.seed

# Clear database only
python -m database.seed --clear
```

### Validation

```bash
# Run full validation
python -m database.validator
```

Checks:
- Database connectivity
- Collection existence
- Index creation
- Data integrity
- Statistics

### Migrations

```bash
# Run all pending migrations
python -m database.migrations migrate

# Rollback last migration
python -m database.migrations rollback

# Rollback last 3 migrations
python -m database.migrations rollback 3

# Check migration status
python -m database.migrations status
```

## Error Handling

The database layer handles errors gracefully:

```python
try:
    user_id = user_repo.create_user(user_data)
except ValueError as e:
    # User already exists
    print(f"User exists: {e}")
except Exception as e:
    # Database error
    print(f"Database error: {e}")
```

## Performance Tips

1. **Use Batch Operations**: For multiple transactions, use `batch_create()` instead of individual `create()` calls
2. **Leverage Indexes**: Queries on indexed fields are much faster
3. **Limit Results**: Use date ranges and limits to avoid loading too much data
4. **Connection Pooling**: The singleton pattern ensures efficient connection reuse

## Testing

The database module includes sample data generation for testing:

```python
from database.seed import generate_sample_transactions

# Generate 90 days of sample data
transactions = generate_sample_transactions(user_id, days=90)
```

## Monitoring

Use the validator for health checks:

```python
from database.validator import quick_health_check

health = quick_health_check()
if health['healthy']:
    print("Database operational")
    print(health['statistics'])
```

## Production Considerations

1. **Connection String**: Use MongoDB Atlas or managed MongoDB in production
2. **Indexes**: All critical indexes are created automatically on startup
3. **Backups**: Set up regular backups of the database
4. **Monitoring**: Use MongoDB monitoring tools for performance tracking
5. **Security**: 
   - Use strong authentication
   - Enable SSL/TLS
   - Restrict network access
   - Keep connection string in environment variables

## Troubleshooting

### Connection Issues

```python
# Check if MongoDB is running
mongodb_manager.connect()
db = get_db()

if db is None:
    print("Cannot connect to MongoDB")
    # Application will run in demo mode
```

### Missing Indexes

If queries are slow, validate indexes:

```bash
python -m database.validator
```

### Data Corruption

Run integrity checks:

```python
from database.validator import DatabaseValidator

validator = DatabaseValidator()
results = validator.validate_data_integrity()
```

## Contributing

When adding new collections or fields:

1. Update repository classes in `repositories.py`
2. Add schema documentation in this README
3. Create migration in `migrations.py`
4. Update seeding in `seed.py` if needed
5. Add validation checks in `validator.py`

## License

Part of FinSage AI - See main project LICENSE file.
