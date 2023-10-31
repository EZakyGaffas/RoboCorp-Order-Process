from robocorp.tasks import task
from robocorp import browser

from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.HTTP import HTTP
from RPA.Archive import Archive
from RPA.FileSystem import FileSystem


import time


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    open_robot_order_website()
    download_orders_csv()
   
    orders=get_orders()
    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        receipt_pdf_path=store_receipt_as_pdf(row["Order number"])
        screenshot_path=screenshot_robot(row["Order number"])
        embed_screenshot_to_receipt(screenshot_path,receipt_pdf_path)
        go_to_another_robot()

    archive_receipts()

    


def open_robot_order_website():
    "go to browswer and open url"
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def download_orders_csv():
    "download csv"
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv","./output/orders.csv",overwrite=True)
    file_system=FileSystem()
    retry_count=0
    file_exists=False
    while retry_count< 3 and file_exists is False:
        file_exists=file_system.does_file_exist("./output/orders.csv")
        retry_count=retry_count+1
        time.sleep(2)

    

def get_orders():
    "retrive csv data as table format"
    tables=Tables()
    orders=tables.read_table_from_csv(path="./output/orders.csv",header=True)
    return orders

def close_annoying_modal():
    page = browser.page()
    page.click('//div[@class="alert-buttons"]//button[text()="OK"]')



def fill_the_form(order):
    page= browser.page()
    page.select_option("#head",order["Head"])
    page.click('//input[@value='+order["Body"]+']')
    page.fill('//label[text()="3. Legs:"]/ancestor::div/input',order["Legs"])
    page.fill("#address",order["Address"])
    page.click("#preview")

    page.click("#order")
    retry_count=0
    while page.is_visible(selector='//div[@class="alert alert-danger"]',timeout=60) and retry_count <3:
        page.click("#order")
        retry_count=retry_count + 1
        time.sleep(2)
        
    

    

    
def store_receipt_as_pdf(order_number):
    "Stores the receipt as a PDF file"
    page=browser.page()
    receipt_html=page.locator("#receipt").inner_html()
    pdf=PDF()
    pdf.html_to_pdf(receipt_html,"./output/receipts/"+order_number+" receipt.pdf")
    return "./output/receipts/"+order_number+" receipt.pdf"
    

def screenshot_robot(order_number):
    "Takes a screenshot"
    page = browser.page()
    page.locator("#robot-preview-image").screenshot(path="./output/roboimage/robo_"+order_number+".png")
    return "./output/roboimage/robo_"+order_number+".png"

def embed_screenshot_to_receipt(screenshot, pdf_file):
    "Embeds the screenshot to a PDF"
    pdf=PDF()
    # list_of_files=[pdf_file,screenshot]
    pdf.add_files_to_pdf(files=[pdf_file,screenshot],target_document=pdf_file)

def go_to_another_robot():
    browser.page().click("#order-another")

def archive_receipts():
    "Create zip file of receipt PDF files"
    archive = Archive()
    archive.archive_folder_with_zip(folder="./output/receipts",archive_name="./output/receipts.zip")