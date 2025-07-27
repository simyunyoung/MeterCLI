# Meter CLI - Metering Engineer Tool Suite

A comprehensive command-line tool suite designed for metering engineers, featuring unit conversions, flow calculations, pressure drop analysis, and more. Built with cross-platform compatibility in mind.

## Features

### Current Features (v1.0.0)
- **Unit Converter**: Convert between different units for flow, pressure, temperature, and length
- **Flow Calculator**: Calculate flow rate or velocity given pipe diameter
- **Pressure Drop Calculator**: Calculate pressure drop using Darcy-Weisbach equation

### Planned Features
- Orifice plate sizing calculator
- Venturi meter calculations
- Ultrasonic meter path optimization
- Coriolis meter density compensation
- Steam flow calculations
- Gas flow calculations with compressibility
- Meter uncertainty analysis
- Calibration certificate management
- Flow profile analysis
- Reynolds number calculations
- Pipe sizing recommendations

## Installation

### Prerequisites
- Python 3.7 or higher
- No additional dependencies required for basic functionality
- Virtual environment recommended (but not required)

### Installation Steps

#### Recommended: Using Virtual Environment

**On macOS (Development Environment):**
```bash
# Clone the repository
git clone https://github.com/yourusername/MeterCLI.git
cd MeterCLI

# Create and activate virtual environment
python3 -m venv meter_env
source meter_env/bin/activate

# Run setup script
python3 setup.py

# Test installation
meter-cli --version
```

**On Windows (Corporate Environment - User Level):**
```cmd
# Clone the repository
git clone https://github.com/yourusername/MeterCLI.git
cd MeterCLI

# Create and activate virtual environment
python -m venv meter_env
meter_env\Scripts\activate

# Run setup script
python setup.py

# Test installation
meter-cli --version
```

#### Alternative: System-Wide Installation

**On macOS:**
```bash
# Clone the repository
git clone https://github.com/yourusername/MeterCLI.git
cd MeterCLI

# Run setup script (installs to ~/.local/bin)
python3 setup.py

# Test installation
meter-cli --version
```

**On Windows:**
```cmd
# Clone the repository
git clone https://github.com/yourusername/MeterCLI.git
cd MeterCLI

# Run setup script
python setup.py

# Follow instructions to add to PATH or use direct path
```

#### Direct Usage (No Installation)
1. Download `meter_cli.py` from the repository
2. Place it in your desired directory
3. Run with `python meter_cli.py` or `python3 meter_cli.py`

## Usage

### Basic Usage
```bash
# Display help and available commands
python meter_cli.py

# Show version
python meter_cli.py --version
```

### Unit Conversion
```bash
# Convert flow rates
python meter_cli.py convert 100 gpm lpm flow
# Output: 100.0 gpm = 378.5410 lpm

# Convert pressure
python meter_cli.py convert 150 psi bar pressure
# Output: 150.0 psi = 10.3421 bar

# Convert temperature
python meter_cli.py convert 25 c f temperature
# Output: 25.0 c = 77.0000 f

# Convert length
python meter_cli.py convert 12 in mm length
# Output: 12.0 in = 304.8000 mm
```

### Flow Calculations
```bash
# Calculate flow rate from velocity
python meter_cli.py flow 6 --velocity 2.5
# Input: 6 inch diameter pipe, 2.5 m/s velocity

# Calculate velocity from flow rate
python meter_cli.py flow 150 --flow-rate 500
# Input: 150mm diameter pipe, 500 GPM flow rate
```

### Pressure Drop Calculations
```bash
# Calculate pressure drop
python meter_cli.py pressure 500 6 100
# Input: 500 GPM, 6 inch diameter, 100m length

# With custom roughness
python meter_cli.py pressure 500 6 100 --roughness 0.1
```

## Supported Units

### Flow Units
- `gpm` - Gallons per minute
- `lpm` - Liters per minute
- `cfm` - Cubic feet per minute
- `m3h` - Cubic meters per hour
- `bpd` - Barrels per day

### Pressure Units
- `psi` - Pounds per square inch
- `bar` - Bar
- `kpa` - Kilopascals
- `mpa` - Megapascals
- `mmhg` - Millimeters of mercury

### Temperature Units
- `c` - Celsius
- `f` - Fahrenheit
- `k` - Kelvin
- `r` - Rankine

### Length Units
- `ft` - Feet
- `m` - Meters
- `in` - Inches
- `cm` - Centimeters
- `mm` - Millimeters

## Cross-Platform Compatibility

This tool is designed to work seamlessly across different operating systems:

- **Windows**: Tested on Windows 10/11 with user-level Python installation
- **macOS**: Native support for macOS 10.14+
- **Linux**: Compatible with most Linux distributions

### Virtual Environment Benefits
- **Isolation**: Keeps dependencies separate from system Python
- **Portability**: Easy to replicate environment across machines
- **Corporate-Friendly**: No system-wide changes required
- **Version Control**: Can freeze exact dependency versions
- **Clean Uninstall**: Simply delete the virtual environment folder

### Windows-Specific Notes
- No admin privileges required
- Works with user-level Python installations
- Handles Windows path separators correctly
- Compatible with Command Prompt and PowerShell
- Virtual environment recommended for corporate environments

### Virtual Environment Management

**Activating the environment:**
```bash
# macOS/Linux
source meter_env/bin/activate

# Windows
meter_env\Scripts\activate
```

**Deactivating the environment:**
```bash
deactivate
```

**Removing the environment:**
```bash
# Simply delete the folder
rm -rf meter_env  # macOS/Linux
rmdir /s meter_env  # Windows
```

## Development

### Project Structure
```
MeterCLI/
├── meter_cli.py          # Main CLI application
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── tests/               # Unit tests (planned)
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on both Windows and macOS if possible
5. Submit a pull request

### Testing
```bash
# Run basic functionality tests
python meter_cli.py convert 100 gpm lpm flow
python meter_cli.py flow 6 --velocity 2.0
python meter_cli.py pressure 300 4 50
```

## License

MIT License - feel free to use and modify as needed.

## Changelog

### v1.0.0 (Current)
- Initial release
- Unit conversion for flow, pressure, temperature, length
- Flow rate and velocity calculations
- Pressure drop calculations using Darcy-Weisbach equation
- Cross-platform compatibility

## Support

For issues, feature requests, or questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed description
3. Include your operating system and Python version

## Roadmap

See the "Planned Features" section above for upcoming enhancements. Priority will be given to:
1. Orifice plate calculations
2. Enhanced unit support
3. Data export capabilities
4. Graphical output options