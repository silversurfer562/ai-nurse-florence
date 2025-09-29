#!/usr/bin/env python3
"""
Railway.app Production Monitoring Script for AI Nurse Florence
Monitors deployment health, API response times, and live data connectivity
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx


class RailwayMonitor:
    """Production monitoring for AI Nurse Florence on Railway"""

    def __init__(self, base_url: str, webhook_url: Optional[str] = None):
        """
        Initialize Railway monitor

        Args:
            base_url: Railway app URL (e.g., https://your-app.railway.app)
            webhook_url: Optional Discord/Slack webhook for alerts
        """
        self.base_url = base_url.rstrip('/')
        self.webhook_url = webhook_url
        self.metrics: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []

    async def check_health(self) -> Dict[str, Any]:
        """Check application health"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                start_time = time.time()
                response = await client.get(f"{self.base_url}/health")
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    health_data = response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": round(response_time, 2),
                        "timestamp": datetime.now().isoformat(),
                        "details": health_data,
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time_ms": round(response_time, 2),
                        "status_code": response.status_code,
                        "timestamp": datetime.now().isoformat(),
                    }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def check_live_apis(self) -> Dict[str, Any]:
        """Test live API endpoints"""
        endpoints = [
            ("/api/v1/disease/lookup?q=diabetes", "Disease API"),
            ("/api/v1/pubmed/search?q=cancer&limit=3", "PubMed API"),
            ("/api/v1/trials/search?condition=diabetes&limit=2", "Clinical Trials API"),
        ]

        results = {}
        total_time = 0
        successful = 0

        for endpoint, name in endpoints:
            try:
                async with httpx.AsyncClient(timeout=20) as client:
                    start_time = time.time()
                    response = await client.get(f"{self.base_url}{endpoint}")
                    response_time = (time.time() - start_time) * 1000
                    total_time += response_time

                    if response.status_code == 200:
                        successful += 1
                        results[name] = {
                            "status": "ok",
                            "response_time_ms": round(response_time, 2),
                            "status_code": response.status_code,
                        }
                    else:
                        results[name] = {
                            "status": "error",
                            "response_time_ms": round(response_time, 2),
                            "status_code": response.status_code,
                        }

            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                }

        avg_response_time = total_time / len(endpoints) if endpoints else 0

        return {
            "timestamp": datetime.now().isoformat(),
            "success_rate": round((successful / len(endpoints)) * 100, 1),
            "average_response_time_ms": round(avg_response_time, 2),
            "endpoints": results,
        }

    async def check_railway_metrics(self) -> Dict[str, Any]:
        """Get Railway-specific metrics"""
        # Railway doesn't expose metrics API, so we'll check environment info
        return {
            "timestamp": datetime.now().isoformat(),
            "environment": "railway",
            "region": os.getenv("RAILWAY_REGION", "unknown"),
            "deployment_id": os.getenv("RAILWAY_DEPLOYMENT_ID", "unknown"),
            "service_id": os.getenv("RAILWAY_SERVICE_ID", "unknown"),
            "project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
        }

    async def send_alert(self, message: str, level: str = "warning"):
        """Send alert to webhook (Discord/Slack)"""
        if not self.webhook_url:
            return

        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "service": "ai-nurse-florence",
            "deployment": "railway",
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Format for Discord webhook
                webhook_payload = {
                    "embeds": [{
                        "title": f"🏥 AI Nurse Florence Alert ({level.upper()})",
                        "description": message,
                        "color": 16711680 if level == "error" else 16776960,  # Red or Yellow
                        "timestamp": alert_data["timestamp"],
                        "fields": [
                            {"name": "Service", "value": "AI Nurse Florence", "inline": True},
                            {"name": "Platform", "value": "Railway.app", "inline": True},
                            {"name": "URL", "value": self.base_url, "inline": False},
                        ]
                    }]
                }

                await client.post(self.webhook_url, json=webhook_payload)
                self.alerts.append(alert_data)

        except Exception as e:
            print(f"Failed to send alert: {e}")

    async def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        print(f"🔍 Running monitoring cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check application health
        health = await self.check_health()
        print(f"   Health: {health['status']}")

        # Check live APIs
        api_status = await self.check_live_apis()
        print(f"   Live APIs: {api_status['success_rate']}% success rate")

        # Get Railway metrics
        railway_metrics = await self.check_railway_metrics()

        # Compile monitoring report
        report = {
            "timestamp": datetime.now().isoformat(),
            "health": health,
            "live_apis": api_status,
            "railway": railway_metrics,
        }

        # Check for alert conditions
        await self.check_alert_conditions(report)

        # Store metrics
        self.metrics.append(report)

        # Keep only last 100 metrics to prevent memory growth
        if len(self.metrics) > 100:
            self.metrics = self.metrics[-100:]

        return report

    async def check_alert_conditions(self, report: Dict[str, Any]):
        """Check if any alert conditions are met"""
        health = report["health"]
        api_status = report["live_apis"]

        # Health check alerts
        if health["status"] != "healthy":
            await self.send_alert(
                f"Health check failed: {health.get('error', 'Status: ' + health['status'])}",
                "error"
            )

        # Response time alerts
        if health.get("response_time_ms", 0) > 5000:  # 5 seconds
            await self.send_alert(
                f"Slow response time: {health['response_time_ms']}ms",
                "warning"
            )

        # API success rate alerts
        if api_status["success_rate"] < 80:
            await self.send_alert(
                f"Low API success rate: {api_status['success_rate']}%",
                "warning"
            )

    def generate_daily_report(self) -> Dict[str, Any]:
        """Generate a daily summary report"""
        if not self.metrics:
            return {"error": "No metrics available"}

        # Filter last 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]

        if not recent_metrics:
            return {"error": "No recent metrics available"}

        # Calculate averages
        health_checks = [m["health"] for m in recent_metrics if m["health"]["status"] == "healthy"]
        avg_response_time = sum(h.get("response_time_ms", 0) for h in health_checks) / len(health_checks) if health_checks else 0

        api_checks = [m["live_apis"] for m in recent_metrics]
        avg_api_success = sum(a["success_rate"] for a in api_checks) / len(api_checks) if api_checks else 0

        return {
            "period": "24 hours",
            "total_checks": len(recent_metrics),
            "uptime_percentage": round((len(health_checks) / len(recent_metrics)) * 100, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "average_api_success_rate": round(avg_api_success, 2),
            "total_alerts": len([a for a in self.alerts if datetime.fromisoformat(a["timestamp"]) > cutoff]),
            "generated_at": datetime.now().isoformat(),
        }

    async def continuous_monitoring(self, interval_minutes: int = 5):
        """Run continuous monitoring"""
        print(f"🚀 Starting continuous monitoring (every {interval_minutes} minutes)")
        print(f"📊 Monitoring: {self.base_url}")
        print(f"🔔 Alerts: {'Enabled' if self.webhook_url else 'Disabled'}")
        print("-" * 60)

        while True:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                print("\n⏹️  Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying


async def main():
    """Main monitoring function"""
    # Get configuration
    base_url = os.getenv("RAILWAY_STATIC_URL") or os.getenv("APP_URL") or "https://your-app.railway.app"
    webhook_url = os.getenv("WEBHOOK_URL")  # Discord/Slack webhook for alerts

    if len(os.sys.argv) > 1:
        base_url = os.sys.argv[1]

    monitor = RailwayMonitor(base_url, webhook_url)

    # Check command line arguments
    if len(os.sys.argv) > 2 and os.sys.argv[2] == "--continuous":
        await monitor.continuous_monitoring()
    else:
        # Run single monitoring cycle
        report = await monitor.run_monitoring_cycle()

        # Print summary
        print("\n" + "="*50)
        print("🏥 AI NURSE FLORENCE - MONITORING REPORT")
        print("="*50)
        print(f"🌐 URL: {base_url}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏥 Health: {report['health']['status']}")
        print(f"⚡ Response Time: {report['health'].get('response_time_ms', 'N/A')}ms")
        print(f"📊 API Success Rate: {report['live_apis']['success_rate']}%")
        print(f"🚀 Platform: Railway.app")

        # Save report
        with open("railway_monitoring_report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Report saved to: railway_monitoring_report.json")


if __name__ == "__main__":
    import sys
    os.sys = sys
    asyncio.run(main())