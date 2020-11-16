# crawler
> record for this small functionality using python, ocr(only verify for digit number) and selenium. OS system is ubuntu18.04 and anconda env

## contents
* [Installation](#Installation)
* [Coding](#Coding)
* [Service](#Service)


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

## Server

I want to buld a service fot this api, therefore I am using Gunicorn and Nginx for my Flask app. references link as following
* [link1(chinese)](https://peterli.website/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8nginx-gunicorn%E8%88%87supervisor-%E9%83%A8%E7%BD%B2%E4%B8%80%E5%80%8Bflask-app/)
* [link2(chinese)](https://www.howtoing.com/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)
* [link3](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)

for some reason, using above method will case a issue i have to figure out. When I test the selenium with different urls, some urls are working perfect like running flask default setting. But some are not like `https://www.google.com/`. It will cause 500 Internal error. If I check gunicorn server with the command `sudo systemctl status crawler`, the server wich I name crawler shows error for driver.get with unexcept error. I wonder if it is somthing to do with unix server with .sock file cause the problem.

So I use my second option. So I am using supervisor instruction [link(chinese)](https://codertw.com/%E7%A8%8B%E5%BC%8F%E8%AA%9E%E8%A8%80/710461/) to run specific port instead to create a sock file as a service. Fortunately, it work this time. Setting is in supervisord.conf file. The last step is to map ip and port inside nginx. There are serveral way can handle. I create a file with this path `sudo vim /etc/nginx/sites-available/crawler`

```sh
server {
    listen 8788;
    server_name localhost;
    charset utf-8;

    location / {
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        #proxy_redirect off;
        proxy_pass http://127.0.0.1:9200;
        #proxy_connect_timeout 500s;
        #proxy_read_timeout 500s;
        #proxy_send_timeout 500s;
        #include proxy_params;
        #proxy_pass http://unix:/run/crawler.sock;
    }
}
```
Then just restart the nginx. Everything will be alright!!
