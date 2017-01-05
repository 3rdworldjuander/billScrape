#! /usr/bin/env python

import os
import ConfigParser
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time


# Survey popup
# //*[@id="fsrOverlay"]/div/div/div/div/div
# No, thanks button
# //*[@id="fsrOverlay"]/div/div/div/div/div/div[2]/div[2]/a

def hover(driver, xpath):
    """
    Function to hover over link
    """
    from selenium.webdriver.common.action_chains import ActionChains
    element = driver.find_element_by_xpath(xpath)
    hov = ActionChains(driver).move_to_element(element)
    hov.perform()

def calc_dollar(s):
    """
    Function to convert dollar WebElement to float.
    Example, "130.00" to 130.0
    """
    from decimal import Decimal
    dec = Decimal(s.text.replace(u'\u2212','-').replace('$',''))
    return dec

def webelements_to_list(elems):
    """
    Function to convert list of web elements to string list
    """
    list = []
    for i in range(len(elems)):
        list.append(str(elems[i].text))
    return list

def getlist(option, sep=',', chars=None):
    """
    Return a list from a ConfigParser option. By default,
    split on a comma and strip whitespaces.
    """
    return [ chunk.strip(chars) for chunk in option.split(sep) ]


def get_bill(after_login):
    import os
    import ConfigParser
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    import time

    config = ConfigParser.ConfigParser()
    config.read(config_file_path)

    # Webdriver Configuration
    # Using chromedriver
#    driver = webdriver.Chrome(executable_path = config.get('webdriver', 'path_to_chromedriver'))
#    driver.maximize_window()
    # Using phantomjs
    driver = webdriver.PhantomJS(executable_path  = config.get('webdriver', 'path_to_phantomjs') , service_log_path = config.get('webdriver', 'phantom_log_path'))
    driver.set_window_size(1120, 550)
    print "webdriver activated"

    # Load website Configuration
    url = config.get('website', 'start_url')
    uname = config.get('secret', 'att_uname')
    passwd = config.get('secret', 'att_passwd')
    print "credentials acquired"

    driver.get(url)
    print "opened login page"
    # Logging in
    driver.find_element_by_id("userName").send_keys(uname)
    driver.find_element_by_id("password").send_keys(passwd)
    driver.find_element_by_id("loginButton").click()
    print "logged in"
    driver.implicitly_wait(20)
    # Check for popups here

    hover(driver, '//*[@id="ge5p_z2_s2002"]')
    print "hovering"
    driver.find_element_by_xpath(after_login).click()
    print "clicked after_login"
    # Check for popups here
    ### delay to click Expand All
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "accordplusAll")))
    element.click()
    print "clicked Expand All"
    # Getting elements of current bill
    subs_labels = webelements_to_list(driver.find_elements_by_xpath(config.get('elements', 'subscriberLabels')))
    subs_values = driver.find_elements_by_xpath(config.get('elements', 'subscriberValues'))
    disc_label = driver.find_elements_by_xpath(config.get('elements', 'discountLabel'))
    disc_value = driver.find_elements_by_xpath(config.get('elements', 'discountValue'))
    promo_label = driver.find_elements_by_xpath(config.get('elements', 'promoLabel'))
    promo_value = driver.find_elements_by_xpath(config.get('elements', 'promoValue'))
    bill_date = str(driver.find_element_by_xpath(config.get('elements', 'billPeriod')).text)
    names = webelements_to_list(driver.find_elements_by_xpath(config.get('elements', 'allNames')))

    # Creating monthly bill for each user
    subs_adj_values = range(len(subs_values))
    doll_monthlybase = (calc_dollar(promo_value[0]) + calc_dollar(disc_value[0])) / len(subs_values)
    temp = calc_dollar(subs_values[0]) - (calc_dollar(promo_value[0]) + calc_dollar(disc_value[0])) + doll_monthlybase
    subs_adj_values[0] = round(temp)

    for subs in range(len(subs_values))[1:]:
        subs_adj_values[subs] = round(calc_dollar(subs_values[subs]) + doll_monthlybase)

    # Add function to make sure that collected amount is > than actual bill

    # Logout
    driver.find_element_by_xpath("//*[contains(text(),'Log out')]").click()
    print "Logging out"
    # Quit
    driver.quit()
    print "closing browser"
    return names, subs_labels, bill_date, subs_adj_values

# Configure sending email
def send_email(user, pwd, recipient, subject, body):
    """
    Function to send email using gmail smtp server
    """
    import smtplib

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
        server.login(user.split("@")[0], pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print 'successfully sent the mail'
    except:
        print "failed to send mail"

# Sending email notifications to email list
def notify(emails, names, bill_date, subs_labels, subs_adj_values):
    import ConfigParser
    from socket import gethostname

    config = ConfigParser.ConfigParser()
    config.read(config_file_path)

    user = config.get('secret', 'gmail_uname')
    pwd = config.get('secret', 'gmail_passwd')
    for c in range(len(emails)):
        recipient = emails[c] #recipient
        subject = "AT&T Bill: %s %s" % (names[c], bill_date) #subject
        body = "%s \n" \
                "%s \n" \
                "$%d \n" \
                    "Auto-generated message from %s on: \n" \
                        "%s" % (bill_date, subs_labels[c], subs_adj_values[c], gethostname(), time.strftime("%c"))
        send_email(user, pwd, recipient, subject, body)

# Read ini config file
config_file_path = "/Users/Maria/Scripts/billScrapeConfig.ini"
config = ConfigParser.ConfigParser()
config.read(config_file_path)
print time.strftime("%c")
# Load email configuration
emails = getlist(config.get('mail-list', 'emails_live'))
print emails
print "phantomjs"
# Load after-login configuration
bill_from = config.get('website', 'xpath_current')

names, subs_labels, bill_date, subs_adj_values = get_bill(bill_from)
print "all emails", emails
print "all names", names
print "all labels", subs_labels
print "billing date", bill_date
print "adjusted bill", subs_adj_values
print "Total bill:", sum(subs_adj_values)

notify(emails, names, bill_date, subs_labels, subs_adj_values)
