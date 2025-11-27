# Database Quick Reference

Quick reference for common database operations in FinSage AI.

## CLI Commands

| Command | Description |
|---------|-------------|
| `python -m database.cli health` | Quick health check |
| `python -m database.cli validate` | Full validation |
| `python -m database.cli stats` | Show statistics |
| `python -m database.cli seed` | Seed sample data |
| `python -m database.cli clear` | Clear all data |
| `python -m database.cli migrate` | Run migrations |
| `python -m database.cli rollback` | Rollback migration |

## Python API

### Get Database Connection

```python
from database import get_db, RepositoryFactory

db = get_db()
repo_factory = RepositoryFactory(db)
```

### User Operations

```python
user_repo = repo_factory.get_user_repo()

# Create user
user_id = user_repo.create_user({
    "email": "user@example.com",
    "name": "John Doe"
})

# Find by email
user = user_repo.find_by_email("user@example.com")

# Find by ID
user = user_repo.find_by_id(user_id)
```

### Transaction Operations

```python
txn_repo = repo_factory.get_transaction_repo()

# Add transaction
txn_id = txn_repo.create({
    "user_id": user_id,
    "date": datetime.utcnow(),
    "amount": -500,
    "type": "debit",
    "category": "Groceries"
})

# Batch create
txn_ids = txn_repo.batch_create([txn1, txn2, txn3])

# Get recent
transactions = txn_repo.get_recent_transactions(user_id, days=30)

# Get by date range
transactions = txn_repo.find_by_user(
    user_id,
    start_date=start,
    end_date=end
)

# Category summary
summary = txn_repo.get_category_summary(user_id, start, end)

# Monthly summary
monthly = txn_repo.get_monthly_summary(user_id, 2025, 11)

# Spending trend
trend = txn_repo.get_spending_trend(user_id, days=30)
```

### Budget Operations

```python
budget_repo = repo_factory.get_budget_repo()

# Create budget
budget_id = budget_repo.create_budget({
    "user_id": user_id,
    "period": "monthly",
    "total_budget": 50000,
    "categories": {"Groceries": 10000}
})

# Get active budget
budget = budget_repo.find_active_budget(user_id)

# Deactivate all
budget_repo.deactivate_all(user_id)
```

### Goal Operations

```python
goal_repo = repo_factory.get_goal_repo()

# Create goal
goal_id = goal_repo.create({
    "user_id": user_id,
    "goal_name": "Emergency Fund",
    "target_amount": 100000,
    "priority": 1
})

# Get user goals
goals = goal_repo.find_by_user(user_id)

# Get active goals
active = goal_repo.get_active_goals(user_id)

# Update progress
goal_repo.update_progress(goal_id, amount=5000)

# Mark complete
goal_repo.mark_completed(goal_id)
```

### Forecast Operations

```python
forecast_repo = repo_factory.get_forecast_repo()

# Save forecast
forecast_id = forecast_repo.save_forecast(
    user_id,
    "income",
    forecast_data
)

# Get recent forecasts
forecasts = forecast_repo.get_recent_forecasts(
    user_id,
    "income",
    limit=10
)

# Get accuracy
accuracy = forecast_repo.get_forecast_accuracy(user_id, "income")
```

## MongoDB Shell Commands

### Connect

```bash
# Local
mongosh

# Remote
mongosh "mongodb+srv://cluster.mongodb.net/" --username user
```

### Basic Operations

```javascript
// Show databases
show dbs

// Use database
use finsage_db

// Show collections
show collections

// Count documents
db.users.countDocuments()
db.transactions.countDocuments()

// Find documents
db.users.find().pretty()
db.transactions.find({user_id: "123"}).limit(10)

// Find one
db.users.findOne({email: "user@example.com"})

// Update document
db.users.updateOne(
  {email: "user@example.com"},
  {$set: {name: "New Name"}}
)

// Delete document
db.transactions.deleteOne({_id: ObjectId("...")})

// Aggregate
db.transactions.aggregate([
  {$match: {type: "debit"}},
  {$group: {_id: "$category", total: {$sum: "$amount"}}}
])
```

### Index Management

```javascript
// List indexes
db.transactions.getIndexes()

// Create index
db.transactions.createIndex({user_id: 1, date: -1})

// Drop index
db.transactions.dropIndex("index_name")

// Index stats
db.transactions.stats()
```

### Backup & Restore

```bash
# Backup
mongodump --db finsage_db --out /backup/

# Restore
mongorestore --db finsage_db /backup/finsage_db/

# Export collection to JSON
mongoexport --db finsage_db --collection transactions --out transactions.json

# Import from JSON
mongoimport --db finsage_db --collection transactions --file transactions.json
```

## Common Queries

### Analytics

```javascript
// Total income vs expenses
db.transactions.aggregate([
  {$group: {
    _id: "$type",
    total: {$sum: {$abs: "$amount"}},
    count: {$sum: 1}
  }}
])

// Top categories
db.transactions.aggregate([
  {$match: {type: "debit"}},
  {$group: {
    _id: "$category",
    total: {$sum: {$abs: "$amount"}}
  }},
  {$sort: {total: -1}},
  {$limit: 5}
])

// Daily spending
db.transactions.aggregate([
  {$match: {type: "debit"}},
  {$group: {
    _id: {$dateToString: {format: "%Y-%m-%d", date: "$date"}},
    total: {$sum: {$abs: "$amount"}}
  }},
  {$sort: {_id: 1}}
])

// Monthly summary
db.transactions.aggregate([
  {$group: {
    _id: {
      year: {$year: "$date"},
      month: {$month: "$date"},
      type: "$type"
    },
    total: {$sum: {$abs: "$amount"}}
  }},
  {$sort: {"_id.year": 1, "_id.month": 1}}
])
```

### Data Cleanup

```javascript
// Remove old forecasts (>90 days)
db.forecasts.deleteMany({
  created_at: {
    $lt: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000)
  }
})

// Remove inactive users
db.users.deleteMany({
  is_active: false,
  created_at: {$lt: new Date("2024-01-01")}
})

// Remove zero amount transactions
db.transactions.deleteMany({amount: 0})
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | Connection string | `mongodb://localhost:27017/` |
| `MONGODB_DB_NAME` | Database name | `finsage_db` |

## Connection String Formats

### Local

```
mongodb://localhost:27017/
```

### With Authentication

```
mongodb://username:password@localhost:27017/
```

### MongoDB Atlas

```
mongodb+srv://username:password@cluster.mongodb.net/
```

### With Options

```
mongodb://host:27017/?maxPoolSize=50&retryWrites=true
```

## Performance Tips

1. **Use indexes** - All critical fields are indexed automatically
2. **Batch operations** - Use `batch_create()` for multiple inserts
3. **Limit results** - Use date ranges and `.limit()` in queries
4. **Project fields** - Only fetch needed fields: `find({}, {name: 1})`
5. **Use aggregation** - Better for complex analytics
6. **Connection pooling** - Reuse connections (automatic)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't connect | Check MongoDB is running: `mongosh` |
| Authentication error | Verify credentials in `.env` |
| Slow queries | Run validation to check indexes |
| Out of memory | Limit query results and use pagination |
| Connection timeout | Increase timeout in mongo_config.py |

## File Locations

```
backend/database/
├── __init__.py          # Module exports
├── mongo_config.py      # Connection management
├── repositories.py      # Data access layer
├── seed.py             # Sample data generation
├── validator.py        # Health checks
├── migrations.py       # Schema migrations
├── cli.py              # CLI tool
└── README.md           # Full documentation
```

## Sample Data

After seeding:
- 2 users (demo@finsage.ai, test@finsage.ai)
- ~270 transactions per user
- Budget allocations
- Financial goals

## Further Reading

- Full documentation: `backend/database/README.md`
- Setup guide: `DATABASE_SETUP.md`
- API docs: http://localhost:8000/docs
- MongoDB docs: https://docs.mongodb.com/
