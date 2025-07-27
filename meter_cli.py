#!/usr/bin/env python3
"""
Meter CLI - A comprehensive metering engineer tool suite
Compatible with Windows, macOS, and Linux
"""

import argparse
import sys
import os
from pathlib import Path
from aga8_calculator import AGA8DetailCalculator, format_gas_report

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
        print("4. AGA8 Gas Report Calculator")
        print("5. Exit")
        print("="*60)
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == '1':
                interactive_unit_converter(cli)
            elif choice == '2':
                interactive_flow_calculator(cli)
            elif choice == '3':
                interactive_pressure_calculator(cli)
            elif choice == '4':
                interactive_aga8_calculator()
            elif choice == '5':
                print("\nThank you for using Meter CLI!")
                break
            else:
                print("\nInvalid choice. Please enter 1, 2, 3, 4, or 5.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Meter CLI. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

def interactive_unit_converter(cli):
    """Interactive unit converter with numbered menus"""
    print("\n--- Unit Converter ---")
    
    # Unit type selection
    unit_types = {
        '1': ('flow', 'Flow Rate'),
        '2': ('pressure', 'Pressure'),
        '3': ('temperature', 'Temperature'),
        '4': ('length', 'Length')
    }
    
    print("\nSelect unit type:")
    for key, (_, display_name) in unit_types.items():
        print(f"{key}. {display_name}")
    
    try:
        type_choice = input("Enter choice (1-4): ").strip()
        if type_choice not in unit_types:
            print("Invalid choice. Please select 1-4.")
            return
        
        unit_type, type_name = unit_types[type_choice]
        
        # Available units for each type
        available_units = {
            'flow': {
                '1': ('gpm', 'Gallons per minute (GPM)'),
                '2': ('lpm', 'Liters per minute (LPM)'),
                '3': ('m3h', 'Cubic meters per hour (m³/h)'),
                '4': ('cfs', 'Cubic feet per second (CFS)'),
                '5': ('lps', 'Liters per second (LPS)')
            },
            'pressure': {
                '1': ('psi', 'Pounds per square inch (PSI)'),
                '2': ('bar', 'Bar'),
                '3': ('pa', 'Pascal (Pa)'),
                '4': ('kpa', 'Kilopascal (kPa)'),
                '5': ('mpa', 'Megapascal (MPa)'),
                '6': ('atm', 'Atmosphere (atm)')
            },
            'temperature': {
                '1': ('c', 'Celsius (°C)'),
                '2': ('f', 'Fahrenheit (°F)'),
                '3': ('k', 'Kelvin (K)')
            },
            'length': {
                '1': ('m', 'Meters (m)'),
                '2': ('mm', 'Millimeters (mm)'),
                '3': ('cm', 'Centimeters (cm)'),
                '4': ('in', 'Inches (in)'),
                '5': ('ft', 'Feet (ft)')
            }
        }
        
        units = available_units[unit_type]
        
        # Get value to convert
        value = float(input(f"\nEnter {type_name.lower()} value to convert: "))
        
        # From unit selection
        print(f"\nSelect FROM unit for {type_name}:")
        for key, (unit, description) in units.items():
            print(f"{key}. {description}")
        
        from_choice = input("Enter choice: ").strip()
        if from_choice not in units:
            print("Invalid choice.")
            return
        
        from_unit = units[from_choice][0]
        
        # To unit selection
        print(f"\nSelect TO unit for {type_name}:")
        for key, (unit, description) in units.items():
            print(f"{key}. {description}")
        
        to_choice = input("Enter choice: ").strip()
        if to_choice not in units:
            print("Invalid choice.")
            return
        
        to_unit = units[to_choice][0]
        
        # Perform conversion
        result, error = cli.unit_converter(value, from_unit, to_unit, unit_type)
        if error:
            print(f"\nError: {error}")
        else:
            from_desc = units[from_choice][1].split('(')[0].strip()
            to_desc = units[to_choice][1].split('(')[0].strip()
            print(f"\nConversion Result:")
            print(f"  {value} {from_unit.upper()} = {result:.4f} {to_unit.upper()}")
            print(f"  ({from_desc} to {to_desc})")
            
    except ValueError:
        print("Invalid input. Please enter a valid number.")
    except Exception as e:
        print(f"Error: {e}")

def interactive_flow_calculator(cli):
    """Interactive flow calculator with numbered menus"""
    print("\n--- Flow Calculator ---")
    
    try:
        # Diameter input with unit selection
        diameter_units = {
            '1': ('m', 'Meters (m)', 1.0),
            '2': ('in', 'Inches (in)', 0.0254),
            '3': ('mm', 'Millimeters (mm)', 0.001),
            '4': ('cm', 'Centimeters (cm)', 0.01),
            '5': ('ft', 'Feet (ft)', 0.3048)
        }
        
        print("\nSelect diameter unit:")
        for key, (unit, description, _) in diameter_units.items():
            print(f"{key}. {description}")
        
        diameter_choice = input("Enter choice (1-5): ").strip()
        if diameter_choice not in diameter_units:
            print("Invalid choice.")
            return
        
        diameter_value = float(input(f"Enter pipe diameter value: "))
        diameter_unit, diameter_desc, conversion_factor = diameter_units[diameter_choice]
        diameter_m = diameter_value * conversion_factor  # Convert to meters
        
        # Calculation type selection
        print("\nChoose calculation type:")
        print("1. Calculate flow rate from velocity")
        print("2. Calculate velocity from flow rate")
        
        calc_type = input("Enter choice (1 or 2): ").strip()
        
        if calc_type == '1':
            velocity = float(input("Enter velocity (m/s): "))
            result = cli.flow_calculator(diameter_m, velocity=velocity)
        elif calc_type == '2':
            # Flow rate unit selection
            flow_units = {
                '1': ('m3h', 'Cubic meters per hour (m³/h)'),
                '2': ('gpm', 'Gallons per minute (GPM)'),
                '3': ('lpm', 'Liters per minute (LPM)'),
                '4': ('cfs', 'Cubic feet per second (CFS)')
            }
            
            print("\nSelect flow rate unit:")
            for key, (unit, description) in flow_units.items():
                print(f"{key}. {description}")
            
            flow_choice = input("Enter choice (1-4): ").strip()
            if flow_choice not in flow_units:
                print("Invalid choice.")
                return
            
            flow_value = float(input("Enter flow rate value: "))
            flow_unit, flow_desc = flow_units[flow_choice]
            
            # Convert flow rate to m³/h for calculation
            if flow_unit == 'gpm':
                flow_m3h = flow_value * 0.227124
            elif flow_unit == 'lpm':
                flow_m3h = flow_value * 0.06
            elif flow_unit == 'cfs':
                flow_m3h = flow_value * 101.94
            else:  # m3h
                flow_m3h = flow_value
            
            result = cli.flow_calculator(diameter_m, flow_rate=flow_m3h)
        else:
            print("Invalid choice.")
            return
        
        if result:
            print("\nFlow Calculation Results:")
            print(f"  Input Diameter: {diameter_value} {diameter_unit} ({result['diameter_m']:.4f} m)")
            print(f"  Pipe Area: {result['pipe_area_m2']:.6f} m²")
            print(f"  Flow Rate: {result['flow_rate_m3h']:.2f} m³/h ({result['flow_rate_gpm']:.2f} GPM)")
            print(f"  Velocity: {result['velocity_ms']:.2f} m/s")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"Error: {e}")

def interactive_pressure_calculator(cli):
    """Interactive pressure drop calculator with numbered menus"""
    print("\n--- Pressure Drop Calculator ---")
    
    try:
        # Flow rate input with unit selection
        flow_units = {
            '1': ('m3h', 'Cubic meters per hour (m³/h)', 1.0),
            '2': ('gpm', 'Gallons per minute (GPM)', 0.227124),
            '3': ('lpm', 'Liters per minute (LPM)', 0.06),
            '4': ('cfs', 'Cubic feet per second (CFS)', 101.94)
        }
        
        print("\nSelect flow rate unit:")
        for key, (unit, description, _) in flow_units.items():
            print(f"{key}. {description}")
        
        flow_choice = input("Enter choice (1-4): ").strip()
        if flow_choice not in flow_units:
            print("Invalid choice.")
            return
        
        flow_value = float(input("Enter flow rate value: "))
        flow_unit, flow_desc, conversion_factor = flow_units[flow_choice]
        flow_rate_m3h = flow_value * conversion_factor  # Convert to m³/h
        
        # Diameter input with unit selection
        diameter_units = {
            '1': ('m', 'Meters (m)', 1.0),
            '2': ('in', 'Inches (in)', 0.0254),
            '3': ('mm', 'Millimeters (mm)', 0.001),
            '4': ('cm', 'Centimeters (cm)', 0.01),
            '5': ('ft', 'Feet (ft)', 0.3048)
        }
        
        print("\nSelect diameter unit:")
        for key, (unit, description, _) in diameter_units.items():
            print(f"{key}. {description}")
        
        diameter_choice = input("Enter choice (1-5): ").strip()
        if diameter_choice not in diameter_units:
            print("Invalid choice.")
            return
        
        diameter_value = float(input("Enter pipe diameter value: "))
        diameter_unit, diameter_desc, diameter_conversion = diameter_units[diameter_choice]
        diameter_m = diameter_value * diameter_conversion  # Convert to meters
        
        # Length input with unit selection
        length_units = {
            '1': ('m', 'Meters (m)', 1.0),
            '2': ('ft', 'Feet (ft)', 0.3048),
            '3': ('km', 'Kilometers (km)', 1000.0),
            '4': ('mi', 'Miles (mi)', 1609.34)
        }
        
        print("\nSelect length unit:")
        for key, (unit, description, _) in length_units.items():
            print(f"{key}. {description}")
        
        length_choice = input("Enter choice (1-4): ").strip()
        if length_choice not in length_units:
            print("Invalid choice.")
            return
        
        length_value = float(input("Enter pipe length value: "))
        length_unit, length_desc, length_conversion = length_units[length_choice]
        length_m = length_value * length_conversion  # Convert to meters
        
        # Pipe roughness selection
        roughness_options = {
            '1': (0.045, 'Commercial steel (0.045 mm) - Default'),
            '2': (0.015, 'Drawn tubing (0.015 mm)'),
            '3': (0.26, 'Galvanized iron (0.26 mm)'),
            '4': (1.5, 'Cast iron (1.5 mm)'),
            '5': (0.0015, 'PVC/Plastic (0.0015 mm)'),
            '6': ('custom', 'Enter custom value')
        }
        
        print("\nSelect pipe roughness:")
        for key, (value, description) in roughness_options.items():
            print(f"{key}. {description}")
        
        roughness_choice = input("Enter choice (1-6, or press Enter for default): ").strip()
        
        if not roughness_choice or roughness_choice == '1':
            roughness = 0.045
            roughness_desc = "Commercial steel (0.045 mm)"
        elif roughness_choice in roughness_options and roughness_choice != '6':
            roughness = roughness_options[roughness_choice][0]
            roughness_desc = roughness_options[roughness_choice][1]
        elif roughness_choice == '6':
            roughness = float(input("Enter custom roughness value (mm): "))
            roughness_desc = f"Custom ({roughness} mm)"
        else:
            print("Invalid choice, using default.")
            roughness = 0.045
            roughness_desc = "Commercial steel (0.045 mm)"
        
        result = cli.pressure_drop_calculator(flow_rate_m3h, diameter_m, length_m, roughness)
        
        print("\nPressure Drop Calculation Results:")
        print(f"  Input Parameters:")
        print(f"    Flow Rate: {flow_value} {flow_unit} ({flow_rate_m3h:.2f} m³/h)")
        print(f"    Diameter: {diameter_value} {diameter_unit} ({diameter_m:.4f} m)")
        print(f"    Length: {length_value} {length_unit} ({length_m:.2f} m)")
        print(f"    Roughness: {roughness_desc}")
        print(f"  Results:")
        print(f"    Pressure Drop: {result['pressure_drop_pa']:.0f} Pa ({result['pressure_drop_psi']:.2f} psi, {result['pressure_drop_bar']:.4f} bar)")
        print(f"    Velocity: {result['velocity_ms']:.2f} m/s")
        print(f"    Reynolds Number: {result['reynolds_number']:.0f}")
        print(f"    Friction Factor: {result['friction_factor']:.6f}")
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"Error: {e}")

def interactive_aga8_calculator():
    """Interactive AGA8 gas report calculator"""
    print("\n--- AGA8 Gas Report Calculator ---")
    print("Enter gas composition in mol%, pressure in barg, and temperature in °C")
    
    try:
        calculator = AGA8DetailCalculator()
        composition = {}
        
        # Common gas components with user-friendly names
        component_options = {
            '1': ('methane', 'Methane (CH₄)'),
            '2': ('ethane', 'Ethane (C₂H₆)'),
            '3': ('propane', 'Propane (C₃H₈)'),
            '4': ('n-butane', 'n-Butane (C₄H₁₀)'),
            '5': ('i-butane', 'i-Butane (C₄H₁₀)'),
            '6': ('n-pentane', 'n-Pentane (C₅H₁₂)'),
            '7': ('i-pentane', 'i-Pentane (C₅H₁₂)'),
            '8': ('hexane', 'Hexane (C₆H₁₄)'),
            '9': ('nitrogen', 'Nitrogen (N₂)'),
            '10': ('carbon_dioxide', 'Carbon Dioxide (CO₂)'),
            '11': ('hydrogen_sulfide', 'Hydrogen Sulfide (H₂S)'),
            '12': ('water', 'Water (H₂O)'),
            '13': ('helium', 'Helium (He)'),
            '14': ('hydrogen', 'Hydrogen (H₂)'),
            '15': ('carbon_monoxide', 'Carbon Monoxide (CO)'),
            '16': ('oxygen', 'Oxygen (O₂)')
        }
        
        print("\nGas Composition Input:")
        print("Available components:")
        for key, (comp, display) in component_options.items():
            print(f"{key:>2}. {display}")
        
        print("\nEnter composition for each component (mol%). Press Enter to skip a component.")
        print("Enter 0 or leave blank for components not present in your gas.")
        
        total_entered = 0.0
        
        # Get composition for each component
        for key, (component, display_name) in component_options.items():
            while True:
                try:
                    user_input = input(f"{display_name}: ").strip()
                    if not user_input:
                        break  # Skip this component
                    
                    value = float(user_input)
                    if value < 0:
                        print("  Error: Composition cannot be negative. Please enter a positive value or 0.")
                        continue
                    elif value > 100:
                        print("  Error: Composition cannot exceed 100%. Please enter a valid percentage.")
                        continue
                    
                    if value > 0:
                        composition[component] = value
                        total_entered += value
                        
                        if total_entered > 100:
                            print(f"  Warning: Total composition ({total_entered:.2f}%) exceeds 100%.")
                            print("  The composition will be normalized automatically.")
                    break
                except ValueError:
                    print("  Error: Please enter a valid number.")
        
        if not composition:
            print("\nError: No gas composition entered. Please enter at least one component.")
            return
        
        print(f"\nTotal composition entered: {total_entered:.2f}%")
        if abs(total_entered - 100.0) > 0.01:
            print("Note: Composition will be normalized to 100%.")
        
        # Get pressure
        while True:
            try:
                pressure_input = input("\nEnter pressure (barg): ").strip()
                pressure_barg = float(pressure_input)
                if pressure_barg < 0:
                    print("Error: Pressure cannot be negative.")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid pressure value.")
        
        # Get temperature
        while True:
            try:
                temp_input = input("Enter temperature (°C): ").strip()
                temperature_degc = float(temp_input)
                if temperature_degc < -273.15:
                    print("Error: Temperature cannot be below absolute zero (-273.15°C).")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid temperature value.")
        
        # Generate and display report
        print("\nGenerating AGA8 Gas Report...")
        
        try:
            report = calculator.generate_detailed_report(composition, pressure_barg, temperature_degc)
            formatted_report = format_gas_report(report)
            print(formatted_report)
            
            # Ask if user wants to save the report
            save_choice = input("\nWould you like to save this report to a file? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                filename = input("Enter filename (without extension): ").strip()
                if not filename:
                    filename = f"aga8_report_{pressure_barg}barg_{temperature_degc}C"
                
                filename = f"{filename}.txt"
                try:
                    with open(filename, 'w') as f:
                        f.write(formatted_report)
                    print(f"Report saved to: {filename}")
                except Exception as e:
                    print(f"Error saving file: {e}")
                    
        except Exception as e:
            print(f"\nError generating AGA8 report: {e}")
            print("Please check your input values and try again.")
            
    except KeyboardInterrupt:
        print("\n\nAGA8 calculation cancelled.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

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