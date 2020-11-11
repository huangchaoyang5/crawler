from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import cv2
import pytesseract
import json
import sys


def decryptRepacha(driver):
    img_src = driver.find_element_by_xpath("//img[@name='imgCode']").screenshot_as_png
    #img_src = driver.find_element_by_tag_name("img").screenshot_as_png
    # save Captcha
    file_img = open("./hct/screenshot.png", "bw+")
    file_img.write(img_src)
    file_img.close()

    # get rid of noise
    img = cv2.imread('./hct/screenshot.png')
    img = img[1:30, 1:80]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.medianBlur(img_gray, 5)
    ret, img_binary = cv2.threshold(img_gray, 55, 255, cv2.THRESH_BINARY_INV)
    #cv2.imwrite('img_code.bmp', img_binary) #saved file for check image
    
    # recognize
    #user_tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    code = pytesseract.image_to_string(img_binary, config='--psm 6 --oem 0 -c tessedit_char_whitelist=0123456789')
    print('repacha: ' + code.rstrip())

    return code.rstrip()

def textTag(num):
    switcher={
                0:'time',
                1:'desc',
             }
    return switcher.get(num, 'Invalid num')



def crawler(orderNo):

    result = ''

    #initializeing
    options = Options()
    options.binary_location = '/usr/bin/google-chrome'
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox') #for linux avoid chrome not started
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.hct.com.tw/Search/SearchGoods_n.aspx")
    time.sleep(1)

    #input Data Insert
    orderNoInput = driver.find_element_by_id("ctl00_ContentFrame_txtpKey")
    repechaDiv =  driver.find_element_by_id("ctl00_ContentFrame_Panel1")
    repechaInput = repechaDiv.find_element_by_class_name("chktxt")
    submit = driver.find_element_by_id("ctl00_ContentFrame_Button1")
    orderNoInput.send_keys(orderNo)
    
    decodeCount = 0

    while decodeCount < 5: #try four times
        try:
            decodeCount += 1
            code = decryptRepacha(driver)
            repechaInput.send_keys(code)
            submit.click()
            time.sleep(1)

            try:

                invoiceNo = driver.find_element_by_id('ctl00_ContentFrame_lblInvoiceNo')
                print(invoiceNo.text)

                table = driver.find_element_by_xpath("//table[@class='cargotable']")
                tr = table.find_elements_by_tag_name("tr")
                th = table.find_elements_by_tag_name("th")

                list_of_num = []
                for rC in range(2, len(tr) + 1):
                    row = {}
                    for tC in range(1, len(th) + 1):
                        td = table.find_element_by_xpath("//tbody/tr[" + str(rC) + "]/td[" + str(tC) + "]")
                        row[textTag(tC - 1)] = td.text    

                    list_of_num.append(row)
                    
                
                result = json.dumps(list_of_num)
                decodeCount = 5

            except NoSuchElementException as e: #only happen when input values are incorrect
                print(e)
                driver.switch_to.alert.accept()

        except Exception as e:
            print(e)
            pass

    #result = driver.title
    driver.close()   #Close the chrome window
    driver.quit()    #Close the console app that was used to kick off the chrome window
    #driver.dispose() #Close the chromedriver.exe
    return result

if __name__ == '__main__':
    arg1 = sys.argv[1:]
    result = crawler(arg1)
    #print(result)
