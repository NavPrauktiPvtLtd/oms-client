import schedule
import time

def job():
    print("I'm working...")

def job2():
    print("yo boiss..")

def job3():
    print("Hello")

schedule.every(5).seconds.do(job)
# some other variations 
schedule.every().hour.do(job)
schedule.every().day.at("12:25").do(job)
schedule.every(5).to(10).minutes.do(job)
schedule.every().thursday.at("19:15").do(job)
schedule.every().wednesday.at("13:15").do(job)
schedule.every().minute.at(":17").do(job)
schedule.every(2).seconds.do(job2)

while True:
    schedule.run_pending()
    time.sleep(1)