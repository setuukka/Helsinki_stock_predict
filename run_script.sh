
#!/bin/bash
cd /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict

source /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/.venv/bin/activate 

/home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/.venv/bin/python /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/get_todays_stock_data.py >> /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/cron_output.log 2>&1
