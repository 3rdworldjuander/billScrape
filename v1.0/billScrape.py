#! /usr/bin/env python

def calc_dollar(s):
    """
    Function to convert dollar WebElement to float.
    Example, "130.00" to 130.0
    """
    from decimal import Decimal
    dec = Decimal(s.text.replace(u'\u2212','-').replace('$',''))
    return dec


from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

# Using chromedriver
#path_to_chromedriver = '/Users/Maria/Scripts/chromedriver'
#driver = webdriver.Chrome(executable_path = path_to_chromedriver)
# Using phantomjs
path_to_phantomjs = '/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs'
log_path = '/Users/Maria/Scripts/ghostdriver.log'
driver = webdriver.PhantomJS(executable_path  = path_to_phantomjs, service_log_path = log_path)
driver.set_window_size(1120, 550)

url = "https://www.att.com/olam/"
driver.get(url)
driver.maximize_window()
# Logging in
username = driver.find_element_by_id("userName")
password = driver.find_element_by_id("password")
#### HIDE THIS ####
username.send_keys("")
password.send_keys("")
#### HIDE THIS ####
driver.find_element_by_id("loginButton").click()

# Inspecting current bill
"""
bill details: https://www.att.com/olam/passthroughAction.myworld?actionType=ViewBillDetails
    includes charges per phone number. Expand all will show itemized charges for each phone number
billing history: https://www.att.com/olam/passthroughAction.myworld?actionType=ViewBillHistory
    shows all bills from 12 months back
"""
after_login = "https://www.att.com/olam/passthroughAction.myworld?actionType=ViewBillDetails"
driver.get(after_login)

### delay to click Expand All
element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "accordplusAll")))
element.click()

# Getting elements of current bill
#####################
# Getting each phone number's label and monthly charges on current and historical billing
# LABEL
# .//*[contains(text(),'Total for')]
subs_labels = driver.find_elements_by_xpath('//*[contains(text(), "Total for")]')
# VALUE
# .//*[contains(text(),'Total for')]/following-sibling::div[1]
subs_values = driver.find_elements_by_xpath('.//*[contains(text(),"Total for")]/following-sibling::div[1]')
# Getting National Account discount on current historical billing
# LABEL
# .//*[contains(text(),"National Account Discount")]
disc_label = driver.find_elements_by_xpath('//*[contains(text(),"National Account Discount")]')
# VALUE
# .//*[contains(text(),"National Account Discount")]/ancestor::div[2]/following-sibling::div[1]
disc_value = driver.find_elements_by_xpath('//*[contains(text(),"National Account Discount")]/ancestor::div[2]/following-sibling::div[1]')
# Getting 'Promo for Mobile Share' on current historical billing
# LABEL
# .//*[contains(text(),"Promo for Mobile Share") and contains(@class,"float-left accRow w300")]
promo_label = driver.find_elements_by_xpath('//*[contains(text(),"Promo for Mobile Share") and contains(@class,"float-left accRow w300")]')
# VALUE
# .//*[contains(text(),"Promo for Mobile Share") and contains(@class,"float-left accRow w300")]/following-sibling::div[1]
promo_value = driver.find_elements_by_xpath('//*[contains(text(),"Promo for Mobile Share") and contains(@class,"float-left accRow w300")]/following-sibling::div[1]')
####################

# Creating monthly bill for each user
subs_adj_values = range(len(subs_values))
doll_monthlybase = (calc_dollar(promo_value[0]) + calc_dollar(disc_value[0])) / len(subs_labels)
temp = calc_dollar(subs_values[0]) - (calc_dollar(promo_value[0]) + calc_dollar(disc_value[0])) + doll_monthlybase
subs_adj_values[0] = round(temp)

for subs in range(len(subs_values))[1:]:
    subs_adj_values[subs] = round(calc_dollar(subs_values[subs]) + doll_monthlybase)

# Add function to make sure that collected amount is > than actual bill
# sum(subs_adj_values)

bill_date = str(driver.find_element_by_xpath('//*[contains(text(),"New charges")]').text)

# Get all names of subscribers
names = driver.find_elements_by_xpath('//*[@class="toggle  spl font14 linkColor collapseImg"]')

for c in range(len(subs_labels)):
    body = "%s " \
            "%s " \
            "%s " \
            "$%d" % (str(names[c].text), str(subs_labels[c].text), bill_date, subs_adj_values[c])
    print body

print "Total bill:", sum(subs_adj_values)
print time.strftime("%c")

# Configure all email addresses
# emails = ['maogianan@gmail.com', 'luisa0131@yahoo.com', 'cpluzentales@gmail.com', \
#              'luisa0131@yahoo.com', 'ggold8888@yahoo.com', 'leigh.penafiel@gmail.com', \
#             'ggold8888@yahoo.com', 'campo99@gmail.com', 'ggold8888@yahoo.com']
#
emails = ['maogianan@gmail.com', 'maogianan@gmail.com', 'maogianan@gmail.com', \
              'maogianan@gmail.com', 'maogianan@gmail.com', 'maogianan@gmail.com', \
             'maogianan@gmail.com', 'maogianan@gmail.com', 'maogianan@gmail.com']


# Configure sending email
def send_email(user, pwd, recipient, subject, body):
    """
    Function to send email using gmail smtp server
    """
    import smtplib

#### HIDE THIS ####
    gmail_user = ""
    gmail_pwd = ""
#### HIDE THIS ####

    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

#### HIDE THIS ####
user = ""
pwd = ""
#### HIDE THIS ####

# Sending individual email
for c in range(len(subs_values)):
    recipient = emails[c] #recipient
    subject = "AT&T Bill: %s %s" % (str(names[c].text), bill_date) #subject
    body = "%s \n" \
            "%s \n" \
            "$%d \n" \
                "Auto-generated message from sys-may on: \n" \
                    "%s" % (bill_date, str(subs_labels[c].text), subs_adj_values[c], time.strftime("%c"))
    send_email(user, pwd, recipient, subject, body)

# Logout
driver.find_element_by_xpath("//*[contains(text(),'Log out')]").click()
# Quit
driver.quit()
