#!/usr/bin/env python3
"""
Load Testing Script for Enhanced RAG System
Tests system performance under various load conditions
"""

import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

class LoadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.lock = threading.Lock()
        
    def log_result(self, test_name, response_time, status_code, success, error=None):
        """Log test result"""
        with self.lock:
            self.results.append({
                "test": test_name,
                "response_time": response_time,
                "status_code": status_code,
                "success": success,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })

    async def single_request(self, session, question, test_name):
        """Make a single request"""
        payload = {"question": question}
        start_time = time.time()
        
        try:
            async with session.post(f"{self.base_url}/ask", json=payload) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    success = data.get("success", False)
                    self.log_result(test_name, response_time, response.status, success)
                else:
                    self.log_result(test_name, response_time, response.status, False, f"HTTP {response.status}")
                    
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            self.log_result(test_name, response_time, 0, False, str(e))

    async def concurrent_load_test(self, num_requests, concurrent_users, test_name):
        """Run concurrent load test"""
        print(f"🚀 Starting {test_name}: {num_requests} requests with {concurrent_users} concurrent users")
        
        questions = [
            "What is LayerZero?",
            "Explain LayerZero primitives",
            "How does LayerZero work?",
            "What are the benefits of LayerZero?",
            "Tell me about LayerZero architecture"
        ]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(num_requests):
                question = questions[i % len(questions)]
                task = self.single_request(session, question, test_name)
                tasks.append(task)
                
                # Limit concurrent requests
                if len(tasks) >= concurrent_users:
                    await asyncio.gather(*tasks)
                    tasks = []
            
            # Wait for remaining tasks
            if tasks:
                await asyncio.gather(*tasks)

    def stress_test(self, max_requests=100, max_concurrent=20):
        """Run stress test with increasing load"""
        print("🔥 Starting Stress Test")
        print("=" * 50)
        
        test_scenarios = [
            (10, 2, "Light Load"),
            (25, 5, "Medium Load"),
            (50, 10, "Heavy Load"),
            (100, 20, "Stress Load"),
            (200, 30, "Extreme Load")
        ]
        
        for requests, concurrent, name in test_scenarios:
            if requests > max_requests:
                break
            if concurrent > max_concurrent:
                concurrent = max_concurrent
                
            asyncio.run(self.concurrent_load_test(requests, concurrent, name))
            time.sleep(2)  # Brief pause between tests

    def burst_test(self, burst_size=50, num_bursts=3):
        """Test system response to burst traffic"""
        print("💥 Starting Burst Test")
        print("=" * 50)
        
        for i in range(num_bursts):
            print(f"Burst {i+1}/{num_bursts}: {burst_size} simultaneous requests")
            asyncio.run(self.concurrent_load_test(burst_size, burst_size, f"Burst_{i+1}"))
            time.sleep(5)  # Wait between bursts

    def endurance_test(self, duration_minutes=5, requests_per_minute=60):
        """Test system endurance over time"""
        print("⏰ Starting Endurance Test")
        print("=" * 50)
        
        total_requests = (duration_minutes * requests_per_minute)
        interval = 60.0 / requests_per_minute  # seconds between requests
        
        print(f"Running {total_requests} requests over {duration_minutes} minutes")
        print(f"Request interval: {interval:.2f} seconds")
        
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < (duration_minutes * 60):
            asyncio.run(self.concurrent_load_test(1, 1, "Endurance"))
            request_count += 1
            
            if request_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"Completed {request_count} requests in {elapsed:.1f}s")
            
            time.sleep(interval)

    def analyze_results(self):
        """Analyze test results"""
        print("\n📊 LOAD TEST ANALYSIS")
        print("=" * 50)
        
        if not self.results:
            print("No results to analyze")
            return
        
        # Overall statistics
        response_times = [r["response_time"] for r in self.results]
        success_count = sum(1 for r in self.results if r["success"])
        error_count = len(self.results) - success_count
        
        print(f"Total Requests: {len(self.results)}")
        print(f"Successful: {success_count}")
        print(f"Failed: {error_count}")
        print(f"Success Rate: {(success_count/len(self.results))*100:.1f}%")
        
        if response_times:
            print(f"\nResponse Time Statistics:")
            print(f"  Average: {statistics.mean(response_times):.3f}s")
            print(f"  Median: {statistics.median(response_times):.3f}s")
            print(f"  Min: {min(response_times):.3f}s")
            print(f"  Max: {max(response_times):.3f}s")
            print(f"  95th Percentile: {sorted(response_times)[int(len(response_times)*0.95)]:.3f}s")
        
        # Group by test type
        test_groups = {}
        for result in self.results:
            test_name = result["test"]
            if test_name not in test_groups:
                test_groups[test_name] = []
            test_groups[test_name].append(result)
        
        print(f"\nResults by Test Type:")
        for test_name, results in test_groups.items():
            times = [r["response_time"] for r in results]
            success_rate = (sum(1 for r in results if r["success"]) / len(results)) * 100
            print(f"  {test_name}:")
            print(f"    Requests: {len(results)}")
            print(f"    Success Rate: {success_rate:.1f}%")
            print(f"    Avg Response Time: {statistics.mean(times):.3f}s")
        
        # Save detailed results
        report_file = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

    def run_comprehensive_load_test(self):
        """Run comprehensive load testing suite"""
        print("🚀 Starting Comprehensive Load Testing Suite")
        print("=" * 60)
        
        try:
            # 1. Stress Test
            self.stress_test(max_requests=50, max_concurrent=10)
            
            # 2. Burst Test
            self.burst_test(burst_size=20, num_bursts=2)
            
            # 3. Endurance Test (shorter version for demo)
            self.endurance_test(duration_minutes=1, requests_per_minute=30)
            
        except KeyboardInterrupt:
            print("\n⚠️ Load testing interrupted by user")
        except Exception as e:
            print(f"\n❌ Load testing failed: {str(e)}")
        
        # Analyze results
        self.analyze_results()

if __name__ == "__main__":
    tester = LoadTester()
    tester.run_comprehensive_load_test()
