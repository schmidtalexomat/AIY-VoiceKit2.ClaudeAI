#!/usr/bin/env python3
"""
AIY VoiceKit 2 Hardware Test Script
Tests LED, button, and audio functionality independently.
"""

import sys
import time
import os
import subprocess

# Add AIY path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "AIY-projects-python", "src"))

try:
    from aiy.leds import Leds, Color
    from aiy.board import Board
    print("✓ AIY libraries loaded successfully")
except ImportError as e:
    print(f"✗ Failed to import AIY libraries: {e}")
    print("Make sure AIY-projects-python is in the correct location")
    sys.exit(1)

def test_leds():
    """Test LED functionality"""
    print("\n=== LED Test ===")
    try:
        leds = Leds()
        
        colors = [
            ("Red", Color.RED),
            ("Green", Color.GREEN),
            ("Blue", Color.BLUE),
            ("Purple", Color.PURPLE),
            ("Yellow", Color.YELLOW),
            ("White", Color.WHITE)
        ]
        
        print("Testing LED colors (2 seconds each)...")
        for name, color in colors:
            print(f"  {name}...")
            leds.update(Leds.rgb_on(color))
            time.sleep(2)
        
        print("  Off...")
        leds.update(Leds.rgb_off())
        
        print("✓ LED test completed")
        return True
        
    except Exception as e:
        print(f"✗ LED test failed: {e}")
        return False

def test_button():
    """Test button functionality"""
    print("\n=== Button Test ===")
    try:
        board = Board()
        leds = Leds()
        
        print("Press and release the button within 10 seconds...")
        
        button_pressed = False
        button_released = False
        
        def on_press():
            nonlocal button_pressed
            button_pressed = True
            print("  Button pressed!")
            leds.update(Leds.rgb_on(Color.GREEN))
        
        def on_release():
            nonlocal button_released
            button_released = True
            print("  Button released!")
            leds.update(Leds.rgb_off())
        
        board.button.when_pressed = on_press
        board.button.when_released = on_release
        
        # Wait for button interaction
        start_time = time.time()
        while time.time() - start_time < 10:
            if button_pressed and button_released:
                break
            time.sleep(0.1)
        
        if button_pressed and button_released:
            print("✓ Button test completed")
            return True
        else:
            print("✗ Button test failed - no interaction detected")
            return False
            
    except Exception as e:
        print(f"✗ Button test failed: {e}")
        return False

def test_audio_devices():
    """Test audio device recognition"""
    print("\n=== Audio Device Test ===")
    try:
        # Check ALSA cards
        result = subprocess.run(['cat', '/proc/asound/cards'], 
                              capture_output=True, text=True)
        
        if 'googlevoicehat' in result.stdout.lower():
            print("✓ Google Voice HAT audio card detected")
            print("Available cards:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
            return True
        else:
            print("✗ Google Voice HAT audio card not found")
            print("Available cards:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"✗ Audio device test failed: {e}")
        return False

def test_audio_recording():
    """Test audio recording capability"""
    print("\n=== Audio Recording Test ===")
    try:
        test_file = "/tmp/test_recording.wav"
        
        print("Recording 3 seconds of audio...")
        result = subprocess.run([
            'arecord', '-f', 'cd', '-d', '3', '-t', 'wav', test_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(test_file):
            size = os.path.getsize(test_file)
            print(f"✓ Recording successful: {size} bytes")
            
            # Test playback
            print("Playing back recording...")
            subprocess.run(['aplay', test_file], capture_output=True)
            
            # Cleanup
            os.unlink(test_file)
            return True
        else:
            print(f"✗ Recording failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Audio recording test failed: {e}")
        return False

def test_services():
    """Test AIY services status"""
    print("\n=== Service Status Test ===")
    try:
        services = [
            'aiy_io_permission.service',
            'aiy_voice_classic.service'
        ]
        
        all_good = True
        for service in services:
            result = subprocess.run([
                'systemctl', 'is-active', service
            ], capture_output=True, text=True)
            
            if result.stdout.strip() == 'active':
                print(f"✓ {service} is active")
            else:
                print(f"✗ {service} is not active")
                all_good = False
        
        return all_good
        
    except Exception as e:
        print(f"✗ Service test failed: {e}")
        return False

def main():
    """Run all hardware tests"""
    print("AIY VoiceKit 2 Hardware Test")
    print("=" * 40)
    
    tests = [
        ("Services", test_services),
        ("Audio Devices", test_audio_devices),
        ("LEDs", test_leds),
        ("Button", test_button),
        ("Audio Recording", test_audio_recording)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print(f"\n✗ {test_name} test interrupted")
            results.append((test_name, False))
            break
        except Exception as e:
            print(f"\n✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<15} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("✓ All tests passed! Hardware is ready.")
        return 0
    else:
        print("✗ Some tests failed. Check hardware setup.")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
