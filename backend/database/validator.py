# backend/database/validator.py
"""Database validation and health check utilities"""

from datetime import datetime
from typing import Dict, List, Tuple
from .mongo_config import get_db, mongodb_manager
from pymongo.errors import ConnectionFailure, OperationFailure


class DatabaseValidator:
    """Validate database connection, schema, and data integrity"""
    
    def __init__(self):
        self.db = None
        self.issues = []
        self.warnings = []
    
    def check_connection(self) -> Tuple[bool, str]:
        """Check if database connection is working"""
        try:
            mongodb_manager.connect()
            self.db = get_db()
            
            if self.db is None:
                return False, "Database connection is None"
            
            # Ping database
            self.db.client.admin.command('ping')
            return True, "Connection successful"
            
        except ConnectionFailure as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def check_indexes(self) -> Dict[str, List[str]]:
        """Check if required indexes exist"""
        if self.db is None:
            return {"error": "Database not connected"}
        
        expected_indexes = {
            "users": ["email"],
            "transactions": ["user_id", "date", "type", "category"],
            "budgets": ["user_id", "is_active"],
            "goals": ["user_id", "deadline"]
        }
        
        results = {}
        
        for collection_name, expected in expected_indexes.items():
            collection = self.db[collection_name]
            existing_indexes = collection.index_information()
            
            missing = []
            for field in expected:
                # Check if any index contains this field
                found = any(field in str(idx.get('key', [])) for idx in existing_indexes.values())
                if not found:
                    missing.append(field)
            
            if missing:
                self.warnings.append(f"Missing indexes on {collection_name}: {missing}")
                results[collection_name] = {"status": "warning", "missing": missing}
            else:
                results[collection_name] = {"status": "ok", "missing": []}
        
        return results
    
    def check_collections(self) -> Dict[str, bool]:
        """Check if required collections exist"""
        if self.db is None:
            return {"error": True}
        
        required_collections = ["users", "transactions", "budgets", "goals"]
        existing_collections = self.db.list_collection_names()
        
        results = {}
        for collection in required_collections:
            exists = collection in existing_collections
            results[collection] = exists
            
            if not exists:
                self.warnings.append(f"Collection '{collection}' does not exist")
        
        return results
    
    def get_statistics(self) -> Dict[str, any]:
        """Get database statistics"""
        if self.db is None:
            return {"error": "Database not connected"}
        
        stats = {}
        
        for collection_name in ["users", "transactions", "budgets", "goals"]:
            try:
                collection = self.db[collection_name]
                count = collection.count_documents({})
                stats[collection_name] = {
                    "count": count,
                    "size": self.db.command("collStats", collection_name).get("size", 0)
                }
            except Exception as e:
                stats[collection_name] = {"error": str(e)}
        
        return stats
    
    def validate_data_integrity(self) -> Dict[str, any]:
        """Check for data integrity issues"""
        if self.db is None:
            return {"error": "Database not connected"}
        
        integrity_results = {}
        
        # Check for orphaned transactions (transactions without users)
        try:
            user_ids = set(str(u["_id"]) for u in self.db.users.find({}, {"_id": 1}))
            orphaned_txns = self.db.transactions.count_documents({"user_id": {"$nin": list(user_ids)}})
            
            integrity_results["orphaned_transactions"] = orphaned_txns
            if orphaned_txns > 0:
                self.issues.append(f"Found {orphaned_txns} orphaned transactions")
        except Exception as e:
            integrity_results["orphaned_transactions"] = {"error": str(e)}
        
        # Check for transactions with zero amount
        try:
            zero_amount_txns = self.db.transactions.count_documents({"amount": 0})
            integrity_results["zero_amount_transactions"] = zero_amount_txns
            if zero_amount_txns > 0:
                self.warnings.append(f"Found {zero_amount_txns} transactions with zero amount")
        except Exception as e:
            integrity_results["zero_amount_transactions"] = {"error": str(e)}
        
        # Check for users without transactions
        try:
            users_without_txns = 0
            for user in self.db.users.find({}, {"_id": 1}):
                user_id = str(user["_id"])
                txn_count = self.db.transactions.count_documents({"user_id": user_id})
                if txn_count == 0:
                    users_without_txns += 1
            
            integrity_results["users_without_transactions"] = users_without_txns
            if users_without_txns > 0:
                self.warnings.append(f"Found {users_without_txns} users without transactions")
        except Exception as e:
            integrity_results["users_without_transactions"] = {"error": str(e)}
        
        return integrity_results
    
    def run_full_validation(self) -> Dict[str, any]:
        """Run complete validation suite"""
        print("🔍 Running database validation...\n")
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # 1. Connection check
        print("1️⃣  Checking database connection...")
        connection_ok, connection_msg = self.check_connection()
        results["checks"]["connection"] = {
            "status": "ok" if connection_ok else "error",
            "message": connection_msg
        }
        print(f"   {'✅' if connection_ok else '❌'} {connection_msg}\n")
        
        if not connection_ok:
            results["overall_status"] = "error"
            return results
        
        # 2. Collections check
        print("2️⃣  Checking collections...")
        collections = self.check_collections()
        results["checks"]["collections"] = collections
        all_exist = all(collections.values())
        print(f"   {'✅' if all_exist else '⚠️'} Collections: {collections}\n")
        
        # 3. Indexes check
        print("3️⃣  Checking indexes...")
        indexes = self.check_indexes()
        results["checks"]["indexes"] = indexes
        print(f"   {'✅' if not self.warnings else '⚠️'} Indexes checked\n")
        
        # 4. Statistics
        print("4️⃣  Gathering statistics...")
        stats = self.get_statistics()
        results["statistics"] = stats
        for collection, data in stats.items():
            if "error" not in data:
                print(f"   📊 {collection}: {data['count']} documents")
        print()
        
        # 5. Data integrity
        print("5️⃣  Checking data integrity...")
        integrity = self.validate_data_integrity()
        results["checks"]["integrity"] = integrity
        print(f"   {'✅' if not self.issues else '⚠️'} Integrity checked\n")
        
        # Summary
        results["issues"] = self.issues
        results["warnings"] = self.warnings
        
        if self.issues:
            results["overall_status"] = "error"
            print("❌ Validation completed with ERRORS:")
            for issue in self.issues:
                print(f"   - {issue}")
        elif self.warnings:
            results["overall_status"] = "warning"
            print("⚠️  Validation completed with WARNINGS:")
            for warning in self.warnings:
                print(f"   - {warning}")
        else:
            results["overall_status"] = "ok"
            print("✅ All validation checks passed!")
        
        return results


def quick_health_check() -> Dict[str, any]:
    """Quick database health check"""
    validator = DatabaseValidator()
    connection_ok, message = validator.check_connection()
    
    if not connection_ok:
        return {
            "healthy": False,
            "message": message
        }
    
    stats = validator.get_statistics()
    
    return {
        "healthy": True,
        "message": "Database is operational",
        "statistics": stats
    }


if __name__ == "__main__":
    validator = DatabaseValidator()
    results = validator.run_full_validation()
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Overall Status: {results['overall_status'].upper()}")
    print(f"{'='*50}")
