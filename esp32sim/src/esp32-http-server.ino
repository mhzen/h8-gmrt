#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h> // Required to parse the incoming JSON from comvis.py

// --- WiFi Settings ---
#define WIFI_SSID "Test"
#define WIFI_PASSWORD ""
#define WIFI_CHANNEL 6

// --- Server ---
WebServer server(80); // The server runs on port 80

/**
 * @brief Handles the incoming POST request from comvis.py
 * This function is triggered when the server receives a POST request
 * at the /update_coords endpoint.
 */
void handlePost()
{
    // Check if the client sent a body
    if (server.hasArg("plain") == false)
    {
        server.send(400, "text/plain", "Body required");
        return;
    }

    String body = server.arg("plain");

    // Parse the JSON data
    StaticJsonDocument<256> doc; // Create a JSON document
    DeserializationError error = deserializeJson(doc, body);

    // Check if JSON parsing failed
    if (error)
    {
        Serial.print("deserializeJson() failed: ");
        Serial.println(error.c_str());
        server.send(400, "text/plain", "Invalid JSON");
        return;
    }

    // --- Success! ---
    // Extract the data from the JSON
    int x = doc["x"];
    int y = doc["y"];

    // **Action: Print the received coordinates to the Serial Monitor**
    Serial.printf("Coordinates received: x = %d, y = %d\n", x, y);

    // Send a 200 OK response back to the Python script
    server.send(200, "application/json", "{\"status\":\"ok\", \"message\":\"Data received\"}");
}

void setup(void)
{
    Serial.begin(115200);

    // --- Connect to WiFi ---
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD, WIFI_CHANNEL);
    Serial.print("Connecting to WiFi ");
    Serial.print(WIFI_SSID);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(100);
        Serial.print(".");
    }
    Serial.println(" Connected!");

    Serial.print("IP address: ");
    Serial.println(WiFi.localIP()); // <-- IMPORTANT! Note this IP.

    // --- Setup Server Routes ---
    // This route listens for HTTP_POST at /update_coords
    server.on("/update_coords", HTTP_POST, handlePost);

    // Start the server
    server.begin();
    Serial.println("HTTP server started.");
    Serial.println("Waiting for POST requests at /update_coords");
}

void loop(void)
{
    // This is required to handle incoming client requests
    server.handleClient();
    delay(2);
}