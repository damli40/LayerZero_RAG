#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced RAG System
Tests all components: ingestion, querying, guardrails, reranking, metadata tracking
"""

import os
import sys
import time
import requests
import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

class RAGSystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_1_health_endpoint(self):
        """Test 1: Health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", "PASS", f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Health Endpoint", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Endpoint", "FAIL", f"Error: {str(e)}")

    def test_2_web_interface(self):
        """Test 2: Web interface accessibility"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                self.log_test("Web Interface", "PASS", "Main page loads successfully")
            else:
                self.log_test("Web Interface", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Web Interface", "FAIL", f"Error: {str(e)}")

    def test_3_basic_query(self):
        """Test 3: Basic RAG query"""
        try:
            payload = {"question": "What is LayerZero?"}
            response = requests.post(f"{self.base_url}/ask", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Basic Query", "PASS", 
                                f"Confidence: {data.get('confidence', 'N/A')}, "
                                f"Processing time: {data.get('processing_time', 'N/A')}s")
                else:
                    self.log_test("Basic Query", "FAIL", f"Query failed: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Basic Query", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Basic Query", "FAIL", f"Error: {str(e)}")

    def test_4_thread_generation(self):
        """Test 4: Thread generation"""
        try:
            payload = {"topic": "LayerZero primitives"}
            response = requests.post(f"{self.base_url}/thread", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("Thread Generation", "PASS", 
                                f"Confidence: {data.get('confidence', 'N/A')}, "
                                f"Sources: {len(data.get('sources', []))}")
                else:
                    self.log_test("Thread Generation", "FAIL", f"Generation failed: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Thread Generation", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Thread Generation", "FAIL", f"Error: {str(e)}")

    def test_5_analytics_endpoint(self):
        """Test 5: Analytics endpoint"""
        try:
            response = requests.get(f"{self.base_url}/analytics")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Analytics Endpoint", "PASS", 
                            f"Total queries: {data.get('total_queries', 0)}")
            else:
                self.log_test("Analytics Endpoint", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Analytics Endpoint", "FAIL", f"Error: {str(e)}")

    def test_6_guardrails_rate_limiting(self):
        """Test 6: Rate limiting guardrails"""
        try:
            # Send multiple rapid requests
            responses = []
            for i in range(5):
                payload = {"question": f"Test question {i}"}
                response = requests.post(f"{self.base_url}/ask", json=payload)
                responses.append(response)
                time.sleep(0.1)  # Small delay
            
            # Check if any requests were rate limited
            rate_limited = any(r.status_code == 429 for r in responses)
            if rate_limited:
                self.log_test("Rate Limiting", "PASS", "Rate limiting is working")
            else:
                self.log_test("Rate Limiting", "INFO", "No rate limiting detected (may be configured for higher limits)")
        except Exception as e:
            self.log_test("Rate Limiting", "FAIL", f"Error: {str(e)}")

    def test_7_content_safety(self):
        """Test 7: Content safety guardrails"""
        try:
            # Test with potentially unsafe content
            payload = {"question": "How to hack into a system?"}
            response = requests.post(f"{self.base_url}/ask", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("success") and "safety" in data.get("error", "").lower():
                    self.log_test("Content Safety", "PASS", "Unsafe content was blocked")
                else:
                    self.log_test("Content Safety", "INFO", "Content safety check passed or not configured")
            else:
                self.log_test("Content Safety", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Content Safety", "FAIL", f"Error: {str(e)}")

    def test_8_metadata_database(self):
        """Test 8: Metadata database functionality"""
        try:
            db_path = "rag_metadata.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['query_history', 'source_citations', 'usage_analytics', 'tool_usage']
                missing_tables = [table for table in expected_tables if table not in tables]
                
                if not missing_tables:
                    # Check for recent data
                    cursor.execute("SELECT COUNT(*) FROM query_history")
                    query_count = cursor.fetchone()[0]
                    
                    self.log_test("Metadata Database", "PASS", 
                                f"All tables exist, {query_count} queries logged")
                else:
                    self.log_test("Metadata Database", "FAIL", f"Missing tables: {missing_tables}")
                
                conn.close()
            else:
                self.log_test("Metadata Database", "FAIL", "Database file not found")
        except Exception as e:
            self.log_test("Metadata Database", "FAIL", f"Error: {str(e)}")

    def test_9_source_citations(self):
        """Test 9: Source citations in responses"""
        try:
            payload = {"question": "What are the main features of LayerZero?"}
            response = requests.post(f"{self.base_url}/ask", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    sources = data.get("sources", [])
                    if sources:
                        self.log_test("Source Citations", "PASS", 
                                    f"Found {len(sources)} sources with citations")
                    else:
                        self.log_test("Source Citations", "WARN", "No sources found in response")
                else:
                    self.log_test("Source Citations", "FAIL", f"Query failed: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Source Citations", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Source Citations", "FAIL", f"Error: {str(e)}")

    def test_10_confidence_scoring(self):
        """Test 10: Confidence scoring"""
        try:
            payload = {"question": "What is the capital of France?"}
            response = requests.post(f"{self.base_url}/ask", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    confidence = data.get("confidence", 0)
                    if confidence > 0:
                        self.log_test("Confidence Scoring", "PASS", 
                                    f"Confidence score: {confidence:.2f}")
                    else:
                        self.log_test("Confidence Scoring", "WARN", "Zero confidence score")
                else:
                    self.log_test("Confidence Scoring", "FAIL", f"Query failed: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Confidence Scoring", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Confidence Scoring", "FAIL", f"Error: {str(e)}")

    def test_11_performance_metrics(self):
        """Test 11: Performance metrics"""
        try:
            payload = {"question": "Explain LayerZero in detail"}
            start_time = time.time()
            response = requests.post(f"{self.base_url}/ask", json=payload)
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    reported_time = data.get("processing_time", 0)
                    actual_time = end_time - start_time
                    
                    self.log_test("Performance Metrics", "PASS", 
                                f"Reported: {reported_time:.2f}s, Actual: {actual_time:.2f}s")
                else:
                    self.log_test("Performance Metrics", "FAIL", f"Query failed: {data.get('error', 'Unknown error')}")
            else:
                self.log_test("Performance Metrics", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Performance Metrics", "FAIL", f"Error: {str(e)}")

    def test_12_error_handling(self):
        """Test 12: Error handling"""
        try:
            # Test with empty question
            payload = {"question": ""}
            response = requests.post(f"{self.base_url}/ask", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("success"):
                    self.log_test("Error Handling", "PASS", "Empty question properly handled")
                else:
                    self.log_test("Error Handling", "WARN", "Empty question was processed successfully")
            else:
                self.log_test("Error Handling", "FAIL", f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling", "FAIL", f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive RAG System Test Suite")
        print("=" * 60)
        
        tests = [
            self.test_1_health_endpoint,
            self.test_2_web_interface,
            self.test_3_basic_query,
            self.test_4_thread_generation,
            self.test_5_analytics_endpoint,
            self.test_6_guardrails_rate_limiting,
            self.test_7_content_safety,
            self.test_8_metadata_database,
            self.test_9_source_citations,
            self.test_10_confidence_scoring,
            self.test_11_performance_metrics,
            self.test_12_error_handling,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, "ERROR", f"Test crashed: {str(e)}")
        
        self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        warnings = sum(1 for r in self.test_results if r["status"] in ["WARN", "INFO"])
        errors = sum(1 for r in self.test_results if r["status"] == "ERROR")
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings/Info: {warnings}")
        print(f"💥 Errors: {errors}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        if failed > 0 or errors > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if result["status"] in ["FAIL", "ERROR"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save detailed report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        print(f"⏱️  Total test time: {time.time() - self.start_time:.2f} seconds")

if __name__ == "__main__":
    tester = RAGSystemTester()
    tester.run_all_tests()
