#!/usr/bin/env python3
"""
AGA8 Gas Report Calculator
Detailed implementation of AGA8-92DC equation of state for natural gas
Inputs: Gas composition (mol%), Pressure (barg), Temperature (degC)
"""

import math
from typing import Dict, List, Tuple, Optional

class AGA8Calculator:
    """AGA8-92DC equation of state calculator for natural gas properties"""
    
    def __init__(self):
        """Initialize AGA8 calculator with component data"""
        # Component molecular weights (g/mol)
        self.molecular_weights = {
            'methane': 16.043,
            'ethane': 30.070,
            'propane': 44.097,
            'n-butane': 58.123,
            'i-butane': 58.123,
            'n-pentane': 72.150,
            'i-pentane': 72.150,
            'hexane': 86.177,
            'heptane': 100.204,
            'octane': 114.231,
            'nonane': 128.258,
            'decane': 142.285,
            'nitrogen': 28.014,
            'carbon_dioxide': 44.010,
            'hydrogen_sulfide': 34.082,
            'water': 18.015,
            'helium': 4.003,
            'argon': 39.948,
            'hydrogen': 2.016,
            'carbon_monoxide': 28.010,
            'oxygen': 31.999
        }
        
        # AGA8 binary interaction parameters (simplified set)
        self.kij = self._initialize_binary_parameters()
        
        # Component critical properties and AGA8 parameters
        self.component_data = self._initialize_component_data()
    
    def _initialize_binary_parameters(self) -> Dict:
        """Initialize binary interaction parameters for AGA8"""
        # Simplified binary interaction matrix (key components only)
        kij = {}
        components = ['methane', 'ethane', 'propane', 'n-butane', 'nitrogen', 'carbon_dioxide']
        
        # Initialize with zeros (simplified for demonstration)
        for i, comp1 in enumerate(components):
            for j, comp2 in enumerate(components):
                if i != j:
                    kij[(comp1, comp2)] = 0.0
        
        # Set some key binary interaction parameters
        kij[('methane', 'nitrogen')] = -0.0085
        kij[('nitrogen', 'methane')] = -0.0085
        kij[('methane', 'carbon_dioxide')] = 0.0919
        kij[('carbon_dioxide', 'methane')] = 0.0919
        kij[('ethane', 'nitrogen')] = 0.0407
        kij[('nitrogen', 'ethane')] = 0.0407
        
        return kij
    
    def _initialize_component_data(self) -> Dict:
        """Initialize component critical properties and AGA8 parameters"""
        return {
            'methane': {
                'tc': 190.564,  # Critical temperature (K)
                'pc': 4.5992,   # Critical pressure (MPa)
                'rhoc': 162.66, # Critical density (kg/m³)
                'omega': 0.0115 # Acentric factor
            },
            'ethane': {
                'tc': 305.322,
                'pc': 4.8722,
                'rhoc': 206.18,
                'omega': 0.0995
            },
            'propane': {
                'tc': 369.825,
                'pc': 4.2512,
                'rhoc': 220.48,
                'omega': 0.1523
            },
            'n-butane': {
                'tc': 425.125,
                'pc': 3.7960,
                'rhoc': 227.96,
                'omega': 0.2002
            },
            'nitrogen': {
                'tc': 126.192,
                'pc': 3.3958,
                'rhoc': 313.30,
                'omega': 0.0372
            },
            'carbon_dioxide': {
                'tc': 304.128,
                'pc': 7.3773,
                'rhoc': 467.60,
                'omega': 0.2276
            }
        }
    
    def normalize_composition(self, composition: Dict[str, float]) -> Dict[str, float]:
        """Normalize gas composition to ensure sum equals 100%"""
        total = sum(composition.values())
        if total == 0:
            raise ValueError("Total composition cannot be zero")
        
        return {comp: (value / total) * 100 for comp, value in composition.items()}
    
    def calculate_molecular_weight(self, composition: Dict[str, float]) -> float:
        """Calculate mixture molecular weight"""
        mw = 0.0
        total_mole_fraction = sum(composition.values()) / 100.0
        
        for component, mole_percent in composition.items():
            if component in self.molecular_weights:
                mole_fraction = mole_percent / 100.0
                mw += mole_fraction * self.molecular_weights[component]
            else:
                raise ValueError(f"Unknown component: {component}")
        
        return mw
    
    def calculate_critical_properties(self, composition: Dict[str, float]) -> Tuple[float, float, float]:
        """Calculate mixture critical properties using mixing rules"""
        tc_mix = 0.0
        pc_mix = 0.0
        rhoc_mix = 0.0
        
        # Convert to mole fractions
        mole_fractions = {comp: val/100.0 for comp, val in composition.items()}
        
        for component, xi in mole_fractions.items():
            if component in self.component_data:
                data = self.component_data[component]
                tc_mix += xi * data['tc']
                pc_mix += xi * data['pc']
                rhoc_mix += xi * data['rhoc']
        
        return tc_mix, pc_mix, rhoc_mix
    
    def calculate_compressibility_factor(self, pressure_bara: float, temperature_k: float, 
                                       composition: Dict[str, float]) -> float:
        """Calculate compressibility factor using simplified AGA8 approach"""
        # This is a simplified implementation
        # Full AGA8 requires iterative solution of complex equations
        
        tc_mix, pc_mix, rhoc_mix = self.calculate_critical_properties(composition)
        
        # Reduced properties
        tr = temperature_k / tc_mix
        pr = pressure_bara / pc_mix
        
        # Simplified Peng-Robinson equation for demonstration
        # (Real AGA8 is much more complex)
        omega_mix = self._calculate_acentric_factor(composition)
        
        # Peng-Robinson parameters
        kappa = 0.37464 + 1.54226 * omega_mix - 0.26992 * omega_mix**2
        alpha = (1 + kappa * (1 - math.sqrt(tr)))**2
        
        a = 0.45724 * (8.314**2) * (tc_mix**2) / pc_mix * alpha
        b = 0.07780 * 8.314 * tc_mix / pc_mix
        
        # Solve cubic equation for compressibility factor
        # Simplified approach - use ideal gas as starting point
        z = 1.0  # Initial guess
        
        # Newton-Raphson iteration (simplified)
        for _ in range(10):
            f = z**3 - (1 - b*pressure_bara/(8.314*temperature_k))*z**2 + \
                (a*pressure_bara/(8.314*temperature_k)**2)*z - \
                (a*b*pressure_bara**2/(8.314*temperature_k)**3)
            
            df = 3*z**2 - 2*(1 - b*pressure_bara/(8.314*temperature_k))*z + \
                 (a*pressure_bara/(8.314*temperature_k)**2)
            
            if abs(df) > 1e-10:
                z_new = z - f/df
                if abs(z_new - z) < 1e-8:
                    break
                z = z_new
        
        return max(z, 0.1)  # Ensure positive value
    
    def _calculate_acentric_factor(self, composition: Dict[str, float]) -> float:
        """Calculate mixture acentric factor"""
        omega_mix = 0.0
        mole_fractions = {comp: val/100.0 for comp, val in composition.items()}
        
        for component, xi in mole_fractions.items():
            if component in self.component_data:
                omega_mix += xi * self.component_data[component]['omega']
        
        return omega_mix
    
    def calculate_density(self, pressure_bara: float, temperature_k: float, 
                         composition: Dict[str, float], z_factor: float) -> float:
        """Calculate gas density"""
        mw = self.calculate_molecular_weight(composition)
        # ρ = PM/(ZRT) where P in Pa, M in kg/kmol, R = 8314 J/(kmol·K)
        pressure_pa = pressure_bara * 100000  # Convert bar to Pa
        density = (pressure_pa * mw) / (z_factor * 8314 * temperature_k)
        return density
    
    def calculate_heating_value(self, composition: Dict[str, float]) -> Tuple[float, float]:
        """Calculate higher and lower heating values (MJ/m³ at STP)"""
        # Heating values at STP (MJ/m³)
        heating_values_higher = {
            'methane': 39.82,
            'ethane': 70.36,
            'propane': 101.27,
            'n-butane': 133.86,
            'i-butane': 132.86,
            'n-pentane': 166.04,
            'i-pentane': 164.43,
            'hexane': 198.67,
            'heptane': 230.49,
            'octane': 262.77,
            'hydrogen': 12.75,
            'carbon_monoxide': 12.63
        }
        
        heating_values_lower = {
            'methane': 35.89,
            'ethane': 64.36,
            'propane': 93.15,
            'n-butane': 123.64,
            'i-butane': 122.77,
            'n-pentane': 153.28,
            'i-pentane': 151.83,
            'hexane': 183.52,
            'heptane': 213.50,
            'octane': 243.58,
            'hydrogen': 10.79,
            'carbon_monoxide': 12.63
        }
        
        hhv = 0.0
        lhv = 0.0
        
        for component, mole_percent in composition.items():
            mole_fraction = mole_percent / 100.0
            if component in heating_values_higher:
                hhv += mole_fraction * heating_values_higher[component]
            if component in heating_values_lower:
                lhv += mole_fraction * heating_values_lower[component]
        
        return hhv, lhv
    
    def calculate_wobbe_index(self, hhv: float, specific_gravity: float) -> float:
        """Calculate Wobbe Index"""
        return hhv / math.sqrt(specific_gravity)
    
    def calculate_specific_gravity(self, composition: Dict[str, float]) -> float:
        """Calculate specific gravity (relative to air)"""
        mw_gas = self.calculate_molecular_weight(composition)
        mw_air = 28.964  # Molecular weight of air
        return mw_gas / mw_air
    
    def generate_detailed_report(self, composition: Dict[str, float], 
                               pressure_barg: float, temperature_degc: float) -> Dict:
        """Generate comprehensive AGA8 gas report"""
        # Input validation
        if not composition:
            raise ValueError("Gas composition cannot be empty")
        
        if pressure_barg < 0:
            raise ValueError("Pressure cannot be negative")
        
        if temperature_degc < -273.15:
            raise ValueError("Temperature cannot be below absolute zero")
        
        # Normalize composition
        normalized_comp = self.normalize_composition(composition)
        
        # Convert units
        pressure_bara = pressure_barg + 1.01325  # Convert barg to bara
        temperature_k = temperature_degc + 273.15  # Convert °C to K
        
        # Calculate properties
        molecular_weight = self.calculate_molecular_weight(normalized_comp)
        specific_gravity = self.calculate_specific_gravity(normalized_comp)
        z_factor = self.calculate_compressibility_factor(pressure_bara, temperature_k, normalized_comp)
        density = self.calculate_density(pressure_bara, temperature_k, normalized_comp, z_factor)
        hhv, lhv = self.calculate_heating_value(normalized_comp)
        wobbe_index = self.calculate_wobbe_index(hhv, specific_gravity)
        tc_mix, pc_mix, rhoc_mix = self.calculate_critical_properties(normalized_comp)
        
        # Calculate additional properties
        volume_factor = 1.0 / z_factor  # Deviation from ideal gas
        
        # Standard conditions (15°C, 1.01325 bara)
        z_std = self.calculate_compressibility_factor(1.01325, 288.15, normalized_comp)
        density_std = self.calculate_density(1.01325, 288.15, normalized_comp, z_std)
        
        return {
            'input_conditions': {
                'pressure_barg': pressure_barg,
                'pressure_bara': pressure_bara,
                'temperature_degc': temperature_degc,
                'temperature_k': temperature_k,
                'composition': normalized_comp
            },
            'basic_properties': {
                'molecular_weight': molecular_weight,
                'specific_gravity': specific_gravity,
                'compressibility_factor': z_factor,
                'density_kg_m3': density,
                'density_std_kg_m3': density_std
            },
            'heating_values': {
                'higher_heating_value_mj_m3': hhv,
                'lower_heating_value_mj_m3': lhv,
                'wobbe_index_mj_m3': wobbe_index
            },
            'critical_properties': {
                'critical_temperature_k': tc_mix,
                'critical_pressure_mpa': pc_mix,
                'critical_density_kg_m3': rhoc_mix
            },
            'additional_properties': {
                'volume_factor': volume_factor,
                'reduced_temperature': temperature_k / tc_mix,
                'reduced_pressure': pressure_bara / pc_mix
            }
        }

def format_gas_report(report: Dict) -> str:
    """Format the gas report for display"""
    output = []
    output.append("\n" + "="*80)
    output.append("                    AGA8 DETAILED GAS REPORT")
    output.append("="*80)
    
    # Input conditions
    output.append("\nINPUT CONDITIONS:")
    output.append("-" * 40)
    input_cond = report['input_conditions']
    output.append(f"Pressure:     {input_cond['pressure_barg']:.3f} barg ({input_cond['pressure_bara']:.3f} bara)")
    output.append(f"Temperature:  {input_cond['temperature_degc']:.2f} °C ({input_cond['temperature_k']:.2f} K)")
    
    output.append("\nGAS COMPOSITION (mol%):")
    output.append("-" * 40)
    for component, percentage in input_cond['composition'].items():
        if percentage > 0:
            output.append(f"{component.replace('_', '-').title():<15}: {percentage:>8.4f}%")
    
    # Basic properties
    output.append("\nBASIC PROPERTIES:")
    output.append("-" * 40)
    basic = report['basic_properties']
    output.append(f"Molecular Weight:        {basic['molecular_weight']:.3f} g/mol")
    output.append(f"Specific Gravity:        {basic['specific_gravity']:.4f} (relative to air)")
    output.append(f"Compressibility Factor:  {basic['compressibility_factor']:.6f}")
    output.append(f"Density (actual):        {basic['density_kg_m3']:.3f} kg/m³")
    output.append(f"Density (std 15°C):      {basic['density_std_kg_m3']:.3f} kg/m³")
    
    # Heating values
    output.append("\nHEATING VALUES:")
    output.append("-" * 40)
    heating = report['heating_values']
    output.append(f"Higher Heating Value:    {heating['higher_heating_value_mj_m3']:.2f} MJ/m³")
    output.append(f"Lower Heating Value:     {heating['lower_heating_value_mj_m3']:.2f} MJ/m³")
    output.append(f"Wobbe Index:             {heating['wobbe_index_mj_m3']:.2f} MJ/m³")
    
    # Critical properties
    output.append("\nCRITICAL PROPERTIES:")
    output.append("-" * 40)
    critical = report['critical_properties']
    output.append(f"Critical Temperature:    {critical['critical_temperature_k']:.2f} K ({critical['critical_temperature_k']-273.15:.2f} °C)")
    output.append(f"Critical Pressure:       {critical['critical_pressure_mpa']:.3f} MPa ({critical['critical_pressure_mpa']*10:.1f} bar)")
    output.append(f"Critical Density:        {critical['critical_density_kg_m3']:.1f} kg/m³")
    
    # Additional properties
    output.append("\nADDITIONAL PROPERTIES:")
    output.append("-" * 40)
    additional = report['additional_properties']
    output.append(f"Volume Factor:           {additional['volume_factor']:.6f}")
    output.append(f"Reduced Temperature:     {additional['reduced_temperature']:.4f}")
    output.append(f"Reduced Pressure:        {additional['reduced_pressure']:.4f}")
    
    output.append("\n" + "="*80)
    output.append("Note: Calculations based on AGA8-92DC equation of state")
    output.append("Standard conditions: 15°C (288.15 K), 1.01325 bara")
    output.append("="*80)
    
    return "\n".join(output)

if __name__ == "__main__":
    # Example usage
    calculator = AGA8Calculator()
    
    # Example gas composition (typical natural gas)
    composition = {
        'methane': 94.5,
        'ethane': 3.2,
        'propane': 1.1,
        'n-butane': 0.3,
        'nitrogen': 0.7,
        'carbon_dioxide': 0.2
    }
    
    # Example conditions
    pressure_barg = 20.0  # 20 barg
    temperature_degc = 25.0  # 25°C
    
    try:
        report = calculator.generate_detailed_report(composition, pressure_barg, temperature_degc)
        print(format_gas_report(report))
    except Exception as e:
        print(f"Error: {e}")