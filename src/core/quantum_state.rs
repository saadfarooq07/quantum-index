use std::simd::{f64x4, Simd};
use std::ops::{Add, Mul, Sub};

#[derive(Clone, Debug)]
pub struct QuantumState {
    // Store amplitudes as SIMD vectors for parallel processing
    amplitudes: Vec<f64x4>,
    num_qubits: usize,
}

impl QuantumState {
    pub fn new(num_qubits: usize) -> Self {
        let size = 1 << num_qubits;
        let vec_size = (size + 3) / 4;
        let mut amplitudes = Vec::with_capacity(vec_size);
        amplitudes.resize(vec_size, f64x4::splat(0.0));
        amplitudes[0] = f64x4::from_array([1.0, 0.0, 0.0, 0.0]);
        
        Self {
            amplitudes,
            num_qubits,
        }
    }

    pub fn apply_gate(&mut self, gate: &dyn Gate, target: usize) {
        // Apply gate using SIMD operations
        let size = 1 << self.num_qubits;
        let mask = 1 << target;
        
        for i in (0..size).step_by(4) {
            let idx = i / 4;
            let amp = self.amplitudes[idx];
            
            let mut new_amp = f64x4::splat(0.0);
            for j in 0..4 {
                let base_idx = i + j;
                if base_idx >= size { break; }
                
                let bit_set = (base_idx & mask) != 0;
                let pair_idx = if bit_set {
                    base_idx & !mask 
                } else {
                    base_idx | mask
                };
                
                // Apply gate matrix using SIMD ops
                if bit_set {
                    new_amp[j] = gate.apply(amp[j], self.get_amplitude(pair_idx));
                }
            }
            
            self.amplitudes[idx] = new_amp;
        }
    }

    #[inline]
    fn get_amplitude(&self, idx: usize) -> f64 {
        let vec_idx = idx / 4;
        let elem_idx = idx % 4;
        self.amplitudes[vec_idx][elem_idx]
    }
}

