"""
Extraction Scheduler
====================
Run this script to schedule periodic extraction jobs.

Usage:
    # Run once immediately
    python src/scheduler/run_extraction.py --once
    
    # Run on schedule (every day at current time)
    python src/scheduler/run_extraction.py
    
    # Custom interval (e.g., every 6 hours)
    python src/scheduler/run_extraction.py --hours 6
    
    # Or every N minutes
    python src/scheduler/run_extraction.py --minutes 30
"""
import schedule
import time
import argparse
from datetime import datetime
from src.data_ingestion.extract_and_store import extract_and_store

def job():
    """Run extraction job"""
    print(f"\n{'*'*70}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Triggered scheduled extraction job")
    print(f"{'*'*70}\n")
    
    try:
        result = extract_and_store()
        print(f"\n✅ Job completed successfully: {result}")
    except Exception as e:
        print(f"\n❌ Job failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Run extraction scheduler')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--minutes', type=int, help='Interval in minutes')
    parser.add_argument('--hours', type=int, help='Interval in hours')
    parser.add_argument('--days', type=int, default=1, help='Interval in days (default: 1)')
    args = parser.parse_args()
    
    if args.once:
        print("Running extraction once...")
        job()
        return
    
    # Determine scheduling interval
    if args.minutes:
        schedule.every(args.minutes).minutes.do(job)
        interval_str = f"every {args.minutes} minutes"
    elif args.hours:
        schedule.every(args.hours).hours.do(job)
        interval_str = f"every {args.hours} hours"
    else:
        schedule.every(args.days).days.do(job)
        interval_str = f"every {args.days} day(s)"
    
    print(f"🔄 Starting extraction scheduler ({interval_str})")
    print("Press Ctrl+C to stop\n")
    
    # Run immediately on startup
    job()
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user")

if __name__ == "__main__":
    main()

