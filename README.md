# crawler
> record for this small functionality using python, ocr(only verify for digit number) and selenium. OS system is ubuntu18.04 and anconda env

## contents
* [Installation](#Installation)
* [Coding](#Coding)
* [Server Setting](#Server Setting)


## Installation
* step1 - Install [Anaconda](https://www.anaconda.com/) and create a environment. For the futher reference pip install, you can check requirement.yml

* step2 - Install `Tesseract 4.0.0 Beta` (P.S you can install other version of Tesseract). More Instruction check out this [link](https://blog.csdn.net/weixin_26752765/article/details/108132614). After download, you can type command to check.

* step3 - Examine Tesseract is working correctly. When I run python to verify the tesseract function, the error message orrcur as following `Failed loading language 'eng' Tesseract couldn't load any languages! Could not initialize tesseract.`, but I check all the files are download successfully and `eng.traineddata` file is exist. After searching, the error is because env variable [TESSDATA_PREFIX](https://askubuntu.com/questions/1111119/tesseract-tessdata-dir-option-not-working-in-ubuntu-18-04) is not set to the tessdata directory when using `Tesseract 4.0.0 Beta`. you can edit `~/.bashrc` and add a line `export TESSDATA_PREFIX='<absolute path to tessdata>'`. Do run source `~/.bashrc` once. you can put tessdata folder like this path `/usr/local/share/tessdata/` and `eng.traineddata` file is inside this folder. Otherwise error might occur. I did not fully test yet.

* step4 - Install [chromedriver and Chrome](https://www.ultralinux.org/post/how-to-install-selenium-python-in-linux/) 

## Coding
There are only two python file. one for [selenium](https://selenium-python.readthedocs.io/) which to open chrome browser and get capcha img and using ocr to get four digit number then enter the number and submit the form to get final output in this porject. The other one is [flask](https://flask.palletsprojects.com/en/1.1.x/) api which is a service can be called by other services to get the final result. 
Testing selenium can use following code for testing

```sh
from selenium import webdriver
from selenium.webdriver.chrome.options import options

#initializeing
options = Options()
options.binary_location = '/usr/bin/google-chrome'
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox') #for linux avoid chrome not started
options.add_experimental_option("excludeSwitches", ['enable-automation'])
options.add_experimental_option('useAutomationExtension', False)  #avoid Cloudflare to restrict access
driver = webdriver.Chrome(options=options)
driver.get("your url")
time.sleep(1)

driver.close()   #Close the chrome window
driver.quit()    #Close the console app that was used to kick off the chrome window
```
When you run python `hct_information.py`, the  __pycache__ and screenshot.png are created. you can delete them, there is no affect on this project.

During the testing you might meet unkill process the links might helpful.
* [Killing a Zombie-Process](https://vitux.com/how-to-kill-zombie-processes-in-ubuntu-18-04/)
* [stop accumulated Google Chrome background processes](https://askubuntu.com/questions/27604/how-can-i-stop-accumulated-google-chrome-background-processes)
* [netstat -tulpn - find current listing port](https://www.tecmint.com/find-listening-ports-linux/)

## Server Setting

I want to buld a service fot this api, therefore I am using Gunicorn and Nginx for my Flask app. references link as following
* [link1(chinese)](https://peterli.website/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8nginx-gunicorn%E8%88%87supervisor-%E9%83%A8%E7%BD%B2%E4%B8%80%E5%80%8Bflask-app/)
* [link2(chinese)](https://www.howtoing.com/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
* [link3](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)

Basically, I need to create a file call XXX.service(in my case is crawler.service) under /etc/systemd/system/ with associated paths which is the locations for bin directories and home directory. `sudo systemctl start crawler` `sudo systemctl enable crawler` `sudo systemctl status crawler` last comman is check the status for this service. The crawler.sock file should be created in the home directory which you type in the crawler.service

Next I use Nginx as a proxy service. Since I want to use different port as a new service, I would like to create a new file for example crawler under /etc/nginx/sites-available/ 
we need to add proxy_pass from our .sock file like this `proxy_pass http://unix:/home/XXX/XXX/crawler.sock;` to map the request.
To enable the Nginx server block configuration you’ve just created, link the file to the sites-enabled directory:
`sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled`
With the file in that directory, you can test for syntax errors:
`sudo nginx -t`
If this returns without indicating any issues, restart the Nginx process to read the new configuration:
`sudo systemctl restart nginx`



