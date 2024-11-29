cd /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict

source /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/.venv/bin/activate

/home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/.venv/bin/python /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/get_stock_data.py >> /home/tuukka/workspace/github.com/setuukka/Helsinki_stock_predict/cron_output_get_stock_data.log 2>&1
