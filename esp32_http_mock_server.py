from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/update_coords', methods=['POST'])
def update_coords():
    data = request.get_json()
    if not data or 'x' not in data or 'y' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    x = data['x']
    y = data['y']
    width = data.get('width', None)
    height = data.get('height', None)
    timestamp = data.get('timestamp', None)

    print(f"Received coordinates: x={x}, y={y}, width={width}, height={height}, timestamp={timestamp}")
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)