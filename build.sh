set -o errexit
pip install -r requirements.txt
mkdir -p logs/buyer_logs
mkdir -p logs/seller_logs
mkdir -p logs/estate_logs
mkdir -p logs/common_logs
chmod 755 logs
chmod 755 logs/*_logs
python manage.py migrate --noinput
python manage.py collectstatic --noinput
echo "Build completed successfully!"
