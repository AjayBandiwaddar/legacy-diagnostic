import boto3
from flask import Flask

app = Flask(__name__)

API_KEY = "sk-live-4242424242424242424242"

# deprecated: boto3 machinelearning client (service retired 2019)
ml_client = boto3.client('machinelearning')


@app.route('/predict')
def predict():
    return ml_client.predict()


@app.route('/health')
def health():
    return {"status": "ok"}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
