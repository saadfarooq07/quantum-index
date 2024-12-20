use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyTuple};
use std::sync::Arc;

/// Bridge between Rust and Python quantum implementations
#[pyclass]
pub struct QuantumBridge {
    q0rtex_module: PyObject,
    quandex_module: PyObject,
    context: Option<PyObject>,
}

#[pymethods]
impl QuantumBridge {
    #[new]
    fn new() -> PyResult<Self> {
        Python::with_gil(|py| {
            let q0rtex = PyModule::import(py, "q0rtex")?;
            let quandex = PyModule::import(py, "quandex")?;
            
            Ok(Self {
                q0rtex_module: q0rtex.into(),
                quandex_module: quandex.into(),
                context: None,
            })
        })
    }

    fn initialize_context(&mut self, qubits: usize) -> PyResult<()> {
        Python::with_gil(|py| {
            let q0rtex = self.q0rtex_module.as_ref(py);
            let context = q0rtex.getattr("Context")?.call1((qubits,))?;
            self.context = Some(context.into());
            Ok(())
        })
    }
    
    fn apply_quantum_gate(&self, gate_type: &str, qubits: Vec<u32>, params: Option<Vec<f64>>) -> PyResult<()> {
        Python::with_gil(|py| {
            let context = match &self.context {
                Some(ctx) => ctx.as_ref(py),
                None => return Err(pyo3::exceptions::PyRuntimeError::new_err("Context not initialized")),
            };

            let args = match params {
                Some(p) => PyTuple::new(py, &[gate_type, qubits.as_slice(), p.as_slice()]),
                None => PyTuple::new(py, &[gate_type, qubits.as_slice()]),
            };

            context.getattr("apply_gate")?.call1(args)?;
            Ok(())
        })
    }

    fn measure(&self, qubit: u32) -> PyResult<bool> {
        Python::with_gil(|py| {
            let context = match &self.context {
                Some(ctx) => ctx.as_ref(py),
                None => return Err(pyo3::exceptions::PyRuntimeError::new_err("Context not initialized")),
            };

            let result = context.getattr("measure")?.call1((qubit,))?;
            result.extract()
        })
    }

    fn get_state(&self) -> PyResult<Vec<f64>> {
        Python::with_gil(|py| {
            let context = match &self.context {
                Some(ctx) => ctx.as_ref(py),
                None => return Err(pyo3::exceptions::PyRuntimeError::new_err("Context not initialized")),
            };

            let state = context.getattr("get_state")?.call0()?;
            state.extract()
        })
    }

    fn run_quandex_circuit(&self, circuit: &PyDict) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let quandex = self.quandex_module.as_ref(py);
            let result = quandex.getattr("run_circuit")?.call1((circuit,))?;
            Ok(result.into())
        })
    }
}

#[pymodule]
fn quantum_bridge(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<QuantumBridge>()?;
    Ok(())
}

