from apscheduler.schedulers.background import BackgroundScheduler
from scheduler.jobs import apply_dynamic_discounts, update_product_status_based_on_inventory

scheduler = BackgroundScheduler()

def start_scheduler():
    scheduler.add_job(apply_dynamic_discounts, "cron", hour="6,11,17", minute=0)
    print("Scheduler dynamic discount started and will run every hour at 6, 11, and 17.")
    scheduler.add_job(update_product_status_based_on_inventory, "cron", minute="*/1") 
    print("Scheduler product avail started and will run 1 minute apart.")
    scheduler.start()
    