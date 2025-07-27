#!/usr/bin/env python3
"""
Meter CLI - A comprehensive metering engineer tool suite
Compatible with Windows, macOS, and Linux
"""

import argparse
import sys
import os
from pathlib import Path

# Ensure cross-platform compatibility
if sys.platform.startswith('win'):
    import msvcrt
else:
    import termios
    import tty

class MeterCLI:
    def __init__(self):
        self.version = "1.0.0"
        self.name = "Meter CLI"
    
    def display_banner(self):
        """Display the CLI banner"""
        banner = f"""
╔══════════════════════════════════════════════════════════════╗
║                        {self.name} v{self.version}                        ║
║              Metering Engineer Tool Suite                    ║
║                Cross-Platform Compatible                     ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def unit_converter(self, value, from_unit, to_unit, unit_type):
        """Convert between different units"""
        conversions = {
            'flow': {
                'gpm': 1.0,  # gallons per minute (base)
                'lpm': 3.78541,  # liters per minute
                'cfm': 0.133681,  # cubic feet per minute
                'm3h': 0.227125,  # cubic meters per hour
                'bpd': 34.2857,  # barrels per day
            },
            'pressure': {
                'psi': 1.0,  # pounds per square inch (base)
                'bar': 0.0689476,  # bar
                'kpa': 6.89476,  # kilopascals
                'mpa': 0.00689476,  # megapascals
                'mmhg': 51.7149,  # millimeters of mercury
            },
            'temperature': {
                'f': lambda c: c * 9/5 + 32,  # Fahrenheit
                'c': lambda f: (f - 32) * 5/9,  # Celsius
                'k': lambda c: c + 273.15,  # Kelvin
                'r': lambda f: f + 459.67,  # Rankine
            },
            'length': {
                'ft': 1.0,  # feet (base)
                'm': 0.3048,  # meters
                'in': 12.0,  # inches
                'cm': 30.48,  # centimeters
                'mm': 304.8,  # millimeters
            }
        }
        
        if unit_type not in conversions:
            return None, f"Unit type '{unit_type}' not supported"
        
        unit_dict = conversions[unit_type]
        
        if unit_type == 'temperature':
            # Special handling for temperature conversions
            if from_unit == 'c' and to_unit == 'f':
                result = unit_dict['f'](value)
            elif from_unit == 'f' and to_unit == 'c':
                result = unit_dict['c'](value)
            elif from_unit == 'c' and to_unit == 'k':
                result = unit_dict['k'](value)
            elif from_unit == 'k' and to_unit == 'c':
                result = value - 273.15
            else:
                return None, f"Temperature conversion from {from_unit} to {to_unit} not implemented"
        else:
            if from_unit not in unit_dict or to_unit not in unit_dict:
                return None, f"Units '{from_unit}' or '{to_unit}' not found in {unit_type} conversions"
            
            # Convert to base unit, then to target unit
            base_value = value / unit_dict[from_unit]
            result = base_value * unit_dict[to_unit]
        
        return result, None
    
    def flow_calculator(self, diameter, velocity=None, flow_rate=None):
        """Calculate flow rate or velocity given pipe diameter"""
        import math
        
        # Convert diameter to meters if needed
        if diameter > 10:  # Assume it's in mm
            diameter = diameter / 1000
        elif diameter > 1:  # Assume it's in inches
            diameter = diameter * 0.0254
        
        area = math.pi * (diameter / 2) ** 2  # m²
        
        if velocity is not None:
            # Calculate flow rate from velocity
            flow_rate = area * velocity * 3600  # m³/h
            return {
                'flow_rate_m3h': flow_rate,
                'flow_rate_gpm': flow_rate * 4.40287,
                'velocity_ms': velocity,
                'pipe_area_m2': area,
                'diameter_m': diameter
            }
        elif flow_rate is not None:
            # Calculate velocity from flow rate
            if flow_rate > 100:  # Assume GPM
                flow_rate = flow_rate / 4.40287  # Convert to m³/h
            
            velocity = flow_rate / (area * 3600)  # m/s
            return {
                'flow_rate_m3h': flow_rate,
                'flow_rate_gpm': flow_rate * 4.40287,
                'velocity_ms': velocity,
                'pipe_area_m2': area,
                'diameter_m': diameter
            }
        else:
            return None
    
    def pressure_drop_calculator(self, flow_rate, diameter, length, roughness=0.045):
        """Calculate pressure drop using Darcy-Weisbach equation"""
        import math
        
        # Convert units if needed
        if diameter > 10:  # mm to m
            diameter = diameter / 1000
        elif diameter > 1:  # inches to m
            diameter = diameter * 0.0254
        
        if flow_rate > 100:  # Assume GPM, convert to m³/s
            flow_rate = flow_rate * 0.00006309
        else:  # Assume m³/h, convert to m³/s
            flow_rate = flow_rate / 3600
        
        # Calculate velocity
        area = math.pi * (diameter / 2) ** 2
        velocity = flow_rate / area
        
        # Reynolds number (assuming water at 20°C)
        kinematic_viscosity = 1.004e-6  # m²/s
        reynolds = velocity * diameter / kinematic_viscosity
        
        # Friction factor (Colebrook-White approximation)
        if reynolds < 2300:
            friction_factor = 64 / reynolds
        else:
            # Swamee-Jain approximation
            friction_factor = 0.25 / (math.log10(roughness / (3.7 * diameter) + 5.74 / (reynolds ** 0.9))) ** 2
        
        # Pressure drop (Pa)
        density = 1000  # kg/m³ (water)
        pressure_drop = friction_factor * (length / diameter) * (density * velocity ** 2) / 2
        
        return {
            'pressure_drop_pa': pressure_drop,
            'pressure_drop_psi': pressure_drop * 0.000145038,
            'pressure_drop_bar': pressure_drop / 100000,
            'velocity_ms': velocity,
            'reynolds_number': reynolds,
            'friction_factor': friction_factor
        }

def interactive_menu():
    """Interactive menu for user-friendly operation"""
    cli = MeterCLI()
    cli.display_banner()
    
    while True:
        print("\n" + "="*60)
        print("Select a function:")
        print("1. Unit Converter")
        print("2. Flow Calculator")
        print("3. Pressure Drop Calculator")
        print("4. Exit")
        print("="*60)
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                interactive_unit_converter(cli)
            elif choice == '2':
                interactive_flow_calculator(cli)
            elif choice == '3':
                interactive_pressure_calculator(cli)
            elif choice == '4':
                print("\nThank you for using Meter CLI!")
                break
            else:
                print("\nInvalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\n\nExiting Meter CLI. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

def interactive_unit_converter(cli):
    """Interactive unit converter"""
    print("\n--- Unit Converter ---")
    print("Available unit types: flow, pressure, temperature, length")
    
    try:
        unit_type = input("Enter unit type: ").strip().lower()
        if unit_type not in ['flow', 'pressure', 'temperature', 'length']:
            print("Invalid unit type. Please use: flow, pressure, temperature, or length")
            return
        
        value = float(input("Enter value to convert: "))
        from_unit = input("From unit: ").strip().lower()
        to_unit = input("To unit: ").strip().lower()
        
        result, error = cli.unit_converter(value, from_unit, to_unit, unit_type)
        if error:
            print(f"Error: {error}")
        else:
            print(f"\nResult: {value} {from_unit} = {result:.4f} {to_unit}")
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")

def interactive_flow_calculator(cli):
    """Interactive flow calculator"""
    print("\n--- Flow Calculator ---")
    
    try:
        diameter = float(input("Enter pipe diameter (m, in, or mm): "))
        
        print("\nChoose calculation type:")
        print("1. Calculate flow rate from velocity")
        print("2. Calculate velocity from flow rate")
        
        calc_type = input("Enter choice (1 or 2): ").strip()
        
        if calc_type == '1':
            velocity = float(input("Enter velocity (m/s): "))
            result = cli.flow_calculator(diameter, velocity=velocity)
        elif calc_type == '2':
            flow_rate = float(input("Enter flow rate (m³/h or GPM): "))
            result = cli.flow_calculator(diameter, flow_rate=flow_rate)
        else:
            print("Invalid choice.")
            return
        
        if result:
            print("\nFlow Calculation Results:")
            print(f"  Diameter: {result['diameter_m']:.4f} m")
            print(f"  Pipe Area: {result['pipe_area_m2']:.6f} m²")
            print(f"  Flow Rate: {result['flow_rate_m3h']:.2f} m³/h ({result['flow_rate_gpm']:.2f} GPM)")
            print(f"  Velocity: {result['velocity_ms']:.2f} m/s")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"Error: {e}")

def interactive_pressure_calculator(cli):
    """Interactive pressure drop calculator"""
    print("\n--- Pressure Drop Calculator ---")
    
    try:
        flow_rate = float(input("Enter flow rate (m³/h or GPM): "))
        diameter = float(input("Enter pipe diameter (m, in, or mm): "))
        length = float(input("Enter pipe length (m): "))
        
        roughness_input = input("Enter pipe roughness in mm (press Enter for default 0.045): ").strip()
        roughness = float(roughness_input) if roughness_input else 0.045
        
        result = cli.pressure_drop_calculator(flow_rate, diameter, length, roughness)
        
        print("\nPressure Drop Calculation Results:")
        print(f"  Pressure Drop: {result['pressure_drop_pa']:.0f} Pa ({result['pressure_drop_psi']:.2f} psi, {result['pressure_drop_bar']:.4f} bar)")
        print(f"  Velocity: {result['velocity_ms']:.2f} m/s")
        print(f"  Reynolds Number: {result['reynolds_number']:.0f}")
        print(f"  Friction Factor: {result['friction_factor']:.6f}")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Meter CLI - Metering Engineer Tool Suite')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Unit converter
    convert_parser = subparsers.add_parser('convert', help='Convert between units')
    convert_parser.add_argument('value', type=float, help='Value to convert')
    convert_parser.add_argument('from_unit', help='Source unit')
    convert_parser.add_argument('to_unit', help='Target unit')
    convert_parser.add_argument('unit_type', choices=['flow', 'pressure', 'temperature', 'length'], help='Type of unit')
    
    # Flow calculator
    flow_parser = subparsers.add_parser('flow', help='Calculate flow rate or velocity')
    flow_parser.add_argument('diameter', type=float, help='Pipe diameter (m, in, or mm)')
    flow_parser.add_argument('--velocity', type=float, help='Velocity (m/s)')
    flow_parser.add_argument('--flow-rate', type=float, help='Flow rate (m³/h or GPM)')
    
    # Pressure drop calculator
    pressure_parser = subparsers.add_parser('pressure', help='Calculate pressure drop')
    pressure_parser.add_argument('flow_rate', type=float, help='Flow rate (m³/h or GPM)')
    pressure_parser.add_argument('diameter', type=float, help='Pipe diameter (m, in, or mm)')
    pressure_parser.add_argument('length', type=float, help='Pipe length (m)')
    pressure_parser.add_argument('--roughness', type=float, default=0.045, help='Pipe roughness (mm)')
    
    # Check if any arguments were provided
    if len(sys.argv) == 1:
        # No arguments provided, start interactive mode
        interactive_menu()
        return
    
    args = parser.parse_args()
    cli = MeterCLI()
    
    if not args.command:
        cli.display_banner()
        parser.print_help()
        return
    
    if args.command == 'convert':
        result, error = cli.unit_converter(args.value, args.from_unit, args.to_unit, args.unit_type)
        if error:
            print(f"Error: {error}")
        else:
            print(f"{args.value} {args.from_unit} = {result:.4f} {args.to_unit}")
    
    elif args.command == 'flow':
        if not args.velocity and not args.flow_rate:
            print("Error: Either --velocity or --flow-rate must be specified")
            return
        
        result = cli.flow_calculator(args.diameter, args.velocity, args.flow_rate)
        if result:
            print("Flow Calculation Results:")
            print(f"  Diameter: {result['diameter_m']:.4f} m")
            print(f"  Pipe Area: {result['pipe_area_m2']:.6f} m²")
            print(f"  Flow Rate: {result['flow_rate_m3h']:.2f} m³/h ({result['flow_rate_gpm']:.2f} GPM)")
            print(f"  Velocity: {result['velocity_ms']:.2f} m/s")
    
    elif args.command == 'pressure':
        result = cli.pressure_drop_calculator(args.flow_rate, args.diameter, args.length, args.roughness)
        print("Pressure Drop Calculation Results:")
        print(f"  Pressure Drop: {result['pressure_drop_pa']:.0f} Pa ({result['pressure_drop_psi']:.2f} psi, {result['pressure_drop_bar']:.4f} bar)")
        print(f"  Velocity: {result['velocity_ms']:.2f} m/s")
        print(f"  Reynolds Number: {result['reynolds_number']:.0f}")
        print(f"  Friction Factor: {result['friction_factor']:.6f}")

if __name__ == '__main__':
    main()