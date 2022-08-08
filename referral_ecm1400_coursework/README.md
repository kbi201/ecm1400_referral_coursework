# Markdown heading Readme file

-------Introduction - Brief summary of the purpose of the project-------

Purpose of the covid19-dashboard-ecm1400 is to display in a concise matter the local 7 day infection rate, the national 7 day infection rate, as well as the national amount of hospital cases, and the national total deaths. It also displays relevant news to covid, as well as giving the user the ability to schedule updates.

-------Prerequisites – Any dependencies not in the installation-------

The python version used for the developement of this dashboard was 3.8.8
To use the dashboard, please install the following:
    Flask
    Cov19 API package provided by the UK gov

-------Installation – Any module dependencies-------

The module dependencies for this project are:
    Flask
    uk-covid19

Please refer to setup.py for more information

-------Getting started tutorial-------

To begin use, please refer to the config file and make any changes desired accordingly to the right-hand side.
Once all the correct packages are installed, run the covid_data_handling.py file to get the dashboard up and running.
To schedule updates, do so on the dashboard.

-------Testing – How to run and test the code-------

To test and run the code, please refer to and use the test versions of both covid_data_handler.py and covid_new_handler.py (the test verions will have 'test' at the end, before the py), and use the pytest testing tool.

-------Developer documentation – Detailed manual on how to use the code-------

To use the code, please check the config.json file and ensure it is correct for what the user wants. Please provide your own API key, as well as directory for the configuration file, so it can work correctly.

Once everything in the configuration file is correct for the the user, please run the the covid_data_handler.py file in the cov19dashboard_pkg folder to get the dashboard up an running, on 'http://127.0.0.1:5000/index'.

To further use the dashboard, one can schedule and remove updates, using the texr box and check boxes, to customize what and when the updates will do. One can also remove articles desired from the dashboard.

-------Details – Authors, license, link to source and acknowledgements-------

Author of covid_data_handler, covid_news_handler: Kelly Blanca Irahola Vallejos
Author of the HTML index file: Matt Collison

Thank you to Matt Collison for providing the html index template for the dasboard.
Thank you to the UK.gov for providing the uk_covid19 package.
