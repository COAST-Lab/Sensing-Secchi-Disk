#!/usr/bin/env python3
"""
Extract temperature data from SD card via serial connection
Sends 'READ' command to MKR WiFi 1010 and captures the streamed data
"""

import os
import serial
import time
from datetime import datetime
from pathlib import Path


def find_serial_port():
    """Find the MKR WiFi 1010 serial port"""
    import glob
    
    ports = glob.glob('/dev/tty.usbmodem*') + glob.glob('/dev/ttyACM*') + glob.glob('COM*')
    
    if not ports:
        print("ERROR: No serial ports found")
        print("\nTroubleshooting:")
        print("1. Connect the MKR WiFi 1010 via USB")
        print("2. Wait a few seconds for the port to appear")
        print("3. Run this script again")
        return None
    
    if len(ports) > 1:
        print("Multiple serial ports found:")
        for i, port in enumerate(ports):
            print(f"  {i}: {port}")
        choice = input("Select port (0-{}): ".format(len(ports)-1))
        return ports[int(choice)]
    
    return ports[0]


def read_data_from_board(port):
    """Send READ command and capture data from serial"""
    try:
        ser = serial.Serial(port, 115200, timeout=5)
        time.sleep(1)  # Wait for connection to establish
        
        print(f"Connected to {port}")
        print("Sending READ command...")
        
        # Send READ command
        ser.write(b"READ\n")
        
        # Read data until END marker
        data = ""
        start_found = False
        
        while True:
            line = ser.readline().decode('utf-8', errors='ignore')
            
            if "===START_DATA===" in line:
                start_found = True
                print("Data stream started...")
                continue
            
            if "===END_DATA===" in line:
                print("Data stream ended")
                break
            
            if start_found:
                data += line
        
        ser.close()
        
        if not data.strip():
            print("ERROR: No data received")
            return None
        
        print(f"Received {len(data)} bytes")
        return data
        
    except serial.SerialException as e:
        print(f"ERROR: Serial connection failed: {e}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def save_to_downloads(data):
    """Save data to Downloads folder with timestamp"""
    downloads_path = Path.home() / "Downloads"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = downloads_path / f"templog_{timestamp}.csv"
    
    try:
        with open(output_file, 'w') as f:
            f.write(data)
        print(f"\n✓ Data saved to: {output_file}")
        return str(output_file)
    except Exception as e:
        print(f"ERROR saving file: {e}")
        return None


def display_data_preview(data):
    """Show first few lines of the data"""
    lines = data.split('\n')
    print(f"\nData preview ({len(lines)} lines total):")
    print("-" * 50)
    for i, line in enumerate(lines[:10]):
        if line.strip():
            print(line)
        if i == 9 and len(lines) > 10:
            print(f"... ({len(lines) - 10} more lines)")
            break
    print("-" * 50)


def main():
    print("=" * 60)
    print("SD Card Temperature Data Extractor (via Serial)")
    print("=" * 60)
    
    # Find serial port
    port = find_serial_port()
    if port is None:
        return
    
    # Read data from board
    data = read_data_from_board(port)
    if data is None:
        return
    
    # Display preview
    display_data_preview(data)
    
    # Save to downloads
    output_path = save_to_downloads(data)
    
    if output_path:
        print(f"\nFile ready for analysis!")
        print(f"Location: {output_path}")
        
        # Parse statistics
        lines = data.split('\n')
        data_lines = [l for l in lines if l.strip() and ',' in l]
        
        if data_lines:
            temps = []
            for line in data_lines:
                try:
                    parts = line.split(',')
                    if len(parts) >= 2:
                        temps.append(float(parts[1]))
                except:
                    pass
            
            if temps:
                print(f"\nTemperature Statistics:")
                print(f"  Readings: {len(temps)}")
                print(f"  Min: {min(temps):.2f}°C")
                print(f"  Max: {max(temps):.2f}°C")
                print(f"  Avg: {sum(temps)/len(temps):.2f}°C")


if __name__ == "__main__":
    main()

