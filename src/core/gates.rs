pub trait Gate {
    fn apply(&self, amplitude0: f64, amplitude1: f64) -> f64;
    fn matrix(&self) -> [[f64; 2]; 2];
}

pub struct Hadamard;
impl Gate for Hadamard {
    fn apply(&self, amplitude0: f64, amplitude1: f64) -> f64 {
        const SQRT_2: f64 = std::f64::consts::FRAC_1_SQRT_2;
        SQRT_2 * (amplitude0 + amplitude1)
    }

    fn matrix(&self) -> [[f64; 2]; 2] {
        const SQRT_2: f64 = std::f64::consts::FRAC_1_SQRT_2;
        [[SQRT_2, SQRT_2], [SQRT_2, -SQRT_2]]
    }
}

pub struct CNOT;
impl Gate for CNOT {
    fn apply(&self, amplitude0: f64, amplitude1: f64) -> f64 {
        amplitude1
    }

    fn matrix(&self) -> [[f64; 2]; 2] {
        [[0.0, 1.0], [1.0, 0.0]]
    }
}

