from flask import Flask, request, jsonify
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
app = Flask(__name__)

SERVICE_A = "http://127.0.0.1:8080"

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/call-echo")
def call_echo():
    start = time.time()
    msg = request.args.get("msg", "")
    try:
        r = requests.get(f"{SERVICE_A}/echo", params={"msg": msg}, timeout=1.0)
        r.raise_for_status()
        data = r.json()
        logging.info(f'service=B endpoint=/call-echo status=ok latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", service_a=data)
    except Exception as e:
        logging.info(f'service=B endpoint=/call-echo status=error error="{str(e)}" latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", service_a="unavailable", error=str(e)), 503

@app.get("/transform")
def transform():
    start = time.time()
    msg = request.args.get("msg", "")
    try:
        # Call both endpoints on Service A and combine results
        echo_resp = requests.get(f"{SERVICE_A}/echo", params={"msg": msg}, timeout=1.0)
        echo_resp.raise_for_status()
        reverse_resp = requests.get(f"{SERVICE_A}/reverse", params={"msg": msg}, timeout=1.0)
        reverse_resp.raise_for_status()
        
        echo_data = echo_resp.json()
        reverse_data = reverse_resp.json()
        
        logging.info(f'service=B endpoint=/transform status=ok latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", echo=echo_data, reversed=reverse_data)
    except Exception as e:
        logging.info(f'service=B endpoint=/transform status=error error="{str(e)}" latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", service_a="unavailable", error=str(e)), 503

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081)
