set -o errexit
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
mkdir -p logs/buyer_logs
mkdir -p logs/seller_logs
mkdir -p logs/estate_logs
mkdir -p logs/common_logs
