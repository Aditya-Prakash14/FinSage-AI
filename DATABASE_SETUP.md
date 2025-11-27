# Database Setup Guide

Complete guide for setting up and managing the FinSage AI database.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Initial Setup](#initial-setup)
5. [Management Commands](#management-commands)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.9+ installed
- MongoDB 4.4+ installed (or MongoDB Atlas account)
- Required Python packages (see requirements.txt)

## Installation

### Option 1: Local MongoDB (Development)

#### macOS

```bash
# Install MongoDB
brew tap mongodb/brew
brew install mongodb-community@7.0

# Start MongoDB service
brew services start mongodb-community@7.0

# Verify installation
mongosh --eval "db.version()"
```

#### Ubuntu/Debian

```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify installation
mongosh --eval "db.version()"
```

#### Windows

Download and install from: https://www.mongodb.com/try/download/community

### Option 2: Docker (Quick Start)

```bash
# Run MongoDB in Docker
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0

# Verify container is running
docker ps | grep mongodb
```

### Option 3: MongoDB Atlas (Cloud - Production)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Create database user
4. Whitelist your IP address
5. Get connection string

## Configuration

Create a `.env` file in the `backend/` directory:

```env
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=finsage_db

# OR MongoDB Atlas (Cloud)
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
# MONGODB_DB_NAME=finsage_db

# Optional: OpenAI API Key for AI features
OPENAI_API_KEY=your_openai_api_key_here
```

## Initial Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Test Database Connection

```bash
python -m database.cli health
```

Expected output:
```
🏥 Running health check...

✅ Database is healthy!

📊 Statistics:
   users: 0 documents (0 bytes)
   transactions: 0 documents (0 bytes)
   budgets: 0 documents (0 bytes)
   goals: 0 documents (0 bytes)
```

### 3. Run Migrations (Create Indexes)

```bash
python -m database.cli migrate
```

Expected output:
```
🔄 Running database migrations...
   ⏩ Applying 001: Add unique index on user email
   ✅ Applied 001
   ⏩ Applying 002: Add transaction indexes
   ✅ Applied 002
   ⏩ Applying 003: Add created_at field to existing documents
   ✅ Applied 003
✅ Applied 3 migration(s)
```

### 4. Seed with Sample Data (Optional)

```bash
python -m database.cli seed
```

This creates:
- 2 sample users
- ~270 transactions per user (90 days)
- Sample budgets
- Sample financial goals

### 5. Validate Setup

```bash
python -m database.cli validate
```

Expected output:
```
🔍 Running database validation...

1️⃣  Checking database connection...
   ✅ Connection successful

2️⃣  Checking collections...
   ✅ Collections: {...}

3️⃣  Checking indexes...
   ✅ Indexes checked

4️⃣  Gathering statistics...
   📊 users: 2 documents
   📊 transactions: 540 documents
   📊 budgets: 2 documents
   📊 goals: 4 documents

5️⃣  Checking data integrity...
   ✅ Integrity checked

✅ All validation checks passed!
```

## Management Commands

The database CLI provides several management commands:

### Health Check

Quick health status:

```bash
python -m database.cli health
```

### Full Validation

Complete database validation:

```bash
python -m database.cli validate
```

### Statistics

View database statistics:

```bash
python -m database.cli stats
```

### Seed Data

Populate with sample data:

```bash
# With confirmation prompt
python -m database.cli seed

# Skip confirmation
python -m database.cli seed --force
```

### Clear Database

Remove all data:

```bash
# With safety confirmation
python -m database.cli clear

# Skip confirmation (dangerous!)
python -m database.cli clear --force
```

### Migrations

Run pending migrations:

```bash
python -m database.cli migrate
```

Rollback migrations:

```bash
# Rollback last migration
python -m database.cli rollback

# Rollback last 3 migrations
python -m database.cli rollback --steps 3
```

## Production Deployment

### MongoDB Atlas Setup

1. **Create Production Cluster**
   - Log in to MongoDB Atlas
   - Create a dedicated cluster (M10+ recommended for production)
   - Choose region closest to your application servers

2. **Security Configuration**
   - Create database user with strong password
   - Whitelist application server IPs
   - Enable network encryption
   - Enable authentication

3. **Get Connection String**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

4. **Update Production Environment Variables**
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DB_NAME=finsage_production
   ```

### Best Practices

1. **Backups**
   - Enable automated backups in MongoDB Atlas
   - Or set up mongodump cron jobs for self-hosted

   ```bash
   # Backup script
   mongodump --uri="mongodb://localhost:27017/finsage_db" --out=/backups/$(date +%Y%m%d)
   ```

2. **Monitoring**
   - Set up MongoDB Atlas monitoring alerts
   - Monitor connection pool usage
   - Track slow queries

3. **Indexing**
   - All critical indexes are created automatically
   - Monitor index usage with `db.collection.getIndexes()`
   - Add custom indexes as needed for new queries

4. **Connection Pooling**
   - Default pool: 10-50 connections
   - Adjust in `mongo_config.py` if needed:
   ```python
   self._client = MongoClient(
       conn_str,
       maxPoolSize=100,  # Increase for high traffic
       minPoolSize=20
   )
   ```

5. **Data Retention**
   - Set up TTL indexes for old data if needed:
   ```javascript
   db.forecasts.createIndex(
     { "created_at": 1 },
     { expireAfterSeconds: 7776000 }  // 90 days
   )
   ```

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to MongoDB

**Solutions**:

1. Check if MongoDB is running:
   ```bash
   # macOS/Linux
   mongosh
   
   # Or check service status
   brew services list  # macOS
   sudo systemctl status mongod  # Linux
   ```

2. Verify connection string in `.env`

3. Check firewall settings (port 27017)

4. For Docker:
   ```bash
   docker logs mongodb
   ```

### Permission Errors

**Problem**: Authentication failed

**Solutions**:

1. Verify username/password in connection string

2. Check user permissions:
   ```javascript
   use admin
   db.getUsers()
   ```

3. Create user if needed:
   ```javascript
   use finsage_db
   db.createUser({
     user: "finsage_user",
     pwd: "secure_password",
     roles: [{ role: "readWrite", db: "finsage_db" }]
   })
   ```

### Slow Queries

**Problem**: Database operations are slow

**Solutions**:

1. Check if indexes exist:
   ```bash
   python -m database.cli validate
   ```

2. Recreate indexes:
   ```bash
   python -m database.cli migrate
   ```

3. Analyze query performance:
   ```javascript
   db.transactions.find({user_id: "123"}).explain("executionStats")
   ```

### Data Inconsistencies

**Problem**: Data integrity issues

**Solutions**:

1. Run validation:
   ```bash
   python -m database.cli validate
   ```

2. Check for orphaned documents:
   ```python
   from database.validator import DatabaseValidator
   validator = DatabaseValidator()
   results = validator.validate_data_integrity()
   ```

3. Re-seed if in development:
   ```bash
   python -m database.cli clear --force
   python -m database.cli seed --force
   ```

### Migration Failures

**Problem**: Migration failed to apply

**Solutions**:

1. Check error logs

2. Rollback and retry:
   ```bash
   python -m database.cli rollback
   python -m database.cli migrate
   ```

3. Manual intervention may be needed - check `migrations.py`

## Database Schema Reference

### Collections

- **users**: User accounts and profiles
- **transactions**: Financial transactions (income/expenses)
- **budgets**: Monthly budget allocations
- **goals**: Financial goals and savings targets
- **forecasts**: Historical forecast data
- **migrations**: Migration version tracking

### Key Indexes

- `users.email`: Unique index for user lookup
- `transactions.user_id + date`: Compound index for time-range queries
- `transactions.category`: Index for category aggregations
- `budgets.user_id + is_active`: Active budget lookup
- `goals.user_id + deadline`: Goal deadline queries

## Support

For issues or questions:
1. Check this guide first
2. Review main README.md
3. Check database/README.md for API documentation
4. Open an issue on GitHub

## Next Steps

After completing database setup:

1. ✅ Start the FastAPI backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. ✅ Access API documentation:
   - http://localhost:8000/docs (Swagger UI)
   - http://localhost:8000/redoc (ReDoc)

3. ✅ Test API endpoints:
   ```bash
   curl http://localhost:8000/api/status
   ```

4. ✅ Start the frontend (in separate terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Congratulations! Your database is now set up and ready to use. 🎉
