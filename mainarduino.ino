#include "Adafruit_SSD1306.h"
#include "Adafruit_GFX.h"
#include "Wire.h"
#define OLED_RESET -1
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define CHANNELS 3
#define BUTTON 2
#define RESET -12
#define SCROLL_SPEED 3
Adafruit_SSD1306 Display(SCREEN_WIDTH,SCREEN_HEIGHT, &Wire, OLED_RESET);
float truncate(float,byte);
float getInput(int index);
void Button();
float lastdata[CHANNELS];
String track;
String lastTrack;
int xpos,minx;
unsigned long lastTime;
bool isconnected;
void setup()
{
    Serial.begin(9600);
    Display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
    Display.setTextColor(SSD1306_WHITE);
    Display.setTextWrap(false);
    Display.display();
    Display.clearDisplay();
    attachInterrupt(digitalPinToInterrupt(BUTTON),Button,RISING);
    isconnected = true;
    for(int x = 0; x < CHANNELS; x++)
    {
        lastdata[x] = 0;
    }
    track = "No song playing";
    lastTrack = "";
    xpos = SCREEN_WIDTH;
    minx = RESET * track.length();
    lastTime = 0;
}

void loop()
{
   char index = 'A';
   float data[CHANNELS];
   if(((millis() - lastTime) > 5000) || (track == "No song playing"))
   {
       Serial.println('N');
       if(isconnected)
       {
           track = "Not connected to PC";
           isconnected = false;
       }
   }
   else isconnected = true;
   for(int x = 0; x < CHANNELS; x++)
   {
       data[x] = getInput(x);
       String s = index + String((int)data[x]);
       if((data[x] != lastdata[x]) && (data[x] != lastdata[x] + 1) && (data[x] != lastdata[x] - 1))
       {
           Serial.println(s);
           lastdata[x] = data[x];
       }
       index++;
   }
    if(track != lastTrack)
    {
        minx = RESET * track.length();
        lastTrack = track;
    }
    Display.clearDisplay();
    Display.setTextSize(2);
    Display.setCursor(xpos,12);
    Display.print(track);
    Display.display();
    xpos -= SCROLL_SPEED;
    if(xpos < minx) xpos = SCREEN_WIDTH;
    
}

float truncate(float val, byte dec) 
{
    float x = val * pow(10, dec);
    float y = round(x);
    float z = x - y;
    if ((int)z == 5)
    {
        y++;
    } else {}
    x = y / pow(10, dec);
    return x;
}

float getInput(int index)
{
   int pot1r = 0;
   for(int i = 0; i < 32; i++) pot1r += analogRead(index);
   pot1r /= 32;
   float out1 = 0;
   if(pot1r != 0) out1 = (float)pot1r / 1023;
   float data1 = 0;
   data1 = truncate(out1,2);
   if(data1 < 0.01f) data1 = 0;
   if(data1 > 1.0f) data1 = 1.0f;
   data1 *= 100;
   return data1;
}

void Button()
{
    static unsigned long last_time = 0;
    unsigned long new_time = millis();
    if((new_time - last_time) > 10000)
    {
        Serial.println('S');
        last_time = new_time;
    }

}

void serialEvent()
{
    String str = "";
    str = Serial.readStringUntil('\n');
    if(str.length() > 2)
    {
        str.remove(str.length());
        track = str;
        lastTime = millis();
    }
    else if (str == "P" || str == "P\n")
    {
        lastTime = millis();
    }

}


