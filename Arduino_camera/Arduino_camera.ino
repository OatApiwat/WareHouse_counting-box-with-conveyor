#include <Ethernet.h>
#include <SPI.h>

const int green = 35;
const int orange = 45;
const int red = 48;
const int stop_con = 47;
const int buzzer = 36;
const int status_con = 42;  //42

const int led_red = 46;
const int led_green = 7;
const int led_blue = 2;

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

IPAddress ip(169, 254, 52, 177);

char server[] = "169.254.52.155";
int port = 5001;

EthernetClient client;

volatile bool interruptFlag = false;

void IRAM_ATTR handleInterrupt() {
  interruptFlag = true;
}

void setup() {
  Serial.begin(115200);
  pinMode(green, OUTPUT);
  pinMode(orange, OUTPUT);
  pinMode(red, OUTPUT);
  pinMode(buzzer, OUTPUT);
  pinMode(stop_con, OUTPUT);
  digitalWrite(green, LOW);
  digitalWrite(orange, LOW);
  digitalWrite(red, LOW);
  digitalWrite(buzzer, LOW);
  Ethernet.begin(mac, ip);
  pinMode(status_con, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(status_con), handleInterrupt, CHANGE);
  delay(1000);

  Serial.println("Connecting...");

  // เชื่อมต่อกับเซิร์ฟเวอร์
  if (client.connect(server, port)) {
    Serial.println("Connected");
  } else {
    Serial.println("Connection failed");
  }
}

void loop() {
  String response = "";

  while (client.available()) {
    char c = client.read();
    response += c;
  }

  Serial.print(response);

  // ตรวจสอบว่ามีคำว่า "ok" ในข้อมูลหรือไม่
  if (response.indexOf("ok") >= 0 || response.indexOf("OK") >= 0) {
    Serial.println("OK");
    rgb_off();
    digitalWrite(green, HIGH);
    rgb_green();
    digitalWrite(orange, LOW);
    buz(1);delay(50);buz(0);
    delay(1000);
    digitalWrite(green, LOW);
    rgb_off();
    // delay(500);
  } else if (response.indexOf("ng") >= 0) {
    Serial.println("ng");
    rgb_off();
    digitalWrite(green, LOW);
    digitalWrite(red, HIGH);
    rgb_red();
    digitalWrite(orange, LOW);
    // buz(1);
    digitalWrite(stop_con, HIGH);

    delay(1000);
    digitalWrite(stop_con, LOW);
  } else if (response.indexOf("nm") >= 0) {
    rgb_off();
    digitalWrite(red, LOW);
    digitalWrite(green, LOW);
    digitalWrite(orange, HIGH);
    rgb_orange();
    buz(1);delay(50);buz(0);
    Serial.println("nm");
  }

  if (interruptFlag) {                     
    interruptFlag = false;
    digitalWrite(stop_con, LOW);              
    bool state = digitalRead(status_con);  

    if (state == 1)  //STOP
    {
      delay(500);
      client.print("stop");
      Serial.println("stop");
      digitalWrite(stop_con, LOW);
    } else if (state == 0)  //RUN
    {
      delay(500);
      client.print("run");
      Serial.println("run");
      rgb_off();
      digitalWrite(red, LOW);
      buz(0);
    }
  }

  // ถ้าเซิร์ฟเวอร์ตัดการเชื่อมต่อ ให้หยุดการทำงาน
  if (!client.connected()) {
    Serial.println();
    Serial.println("Disconnecting.");
    rgb_blue();  // แสดงสีที่บ่งบอกว่าการเชื่อมต่อสำเร็จ
    client.stop();
    // delay(1000); // หน่วงเวลา 2 วินาทีก่อนที่จะลองเชื่อมต่อใหม่
    if (client.connect(server, port)) {
      Serial.println("Reconnected");
      rgb_ready();
    } else {
      Serial.println("Reconnection failed");
      
    }
  } else {
    delay(5);
    rgb_ready();
  }

}

void buz(int s)
{
  if(s == 1)
  {
    analogWrite(buzzer, 255);
  }
  if(s == 0)
  {
    analogWrite(buzzer, 0);
  }
}

void rgb_ready() {
  analogWrite(led_red, 150);
  analogWrite(led_green, 150);
  analogWrite(led_blue, 150);
}

void rgb_red() {
  analogWrite(led_red, 255);
  analogWrite(led_green, 0);
  analogWrite(led_blue, 0);
}

void rgb_green() {
  analogWrite(led_red, 0);
  analogWrite(led_green, 255);
  analogWrite(led_blue, 0);
}

void rgb_blue() {
  analogWrite(led_red, 0);
  analogWrite(led_green, 0);
  analogWrite(led_blue, 255);
}

void rgb_orange() {
  analogWrite(led_red, 255);
  analogWrite(led_green, 255);
  analogWrite(led_blue, 0);
}

void rgb_off() {
  analogWrite(led_red, 0);
  analogWrite(led_green, 0);
  analogWrite(led_blue, 0);
}
