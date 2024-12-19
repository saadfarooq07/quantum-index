import Foundation
import Metal

/// Manager for quantum states and operations
public class QuantumStateManager {
    // MARK: - Properties
    private let neuralCompute: QuantumNamespace.NeuralCompute
    private var currentState: QuantumNamespace.NeuralState
    
    // MARK: - Initialization
    public init(enableMetal: Bool = true) throws {
        self.neuralCompute = try QuantumNamespace.NeuralCompute()
        self.currentState = QuantumNamespace.NeuralState(amplitude: 1.0, phase: 0.0, isEntangled: false)
    }
    
    // MARK: - Public Methods
    /// Apply quantum gate operation
    public func applyGate(_ gate: QuantumNamespace.Gate, to state: QuantumNamespace.NeuralState) throws -> QuantumNamespace.NeuralState {
        return try neuralCompute.process(state, gate: gate)
    }
    
    /// Get current quantum state
    public func getCurrentState() -> QuantumNamespace.NeuralState {
        return currentState
    }
    
    /// Set quantum state
    public func setState(_ state: QuantumNamespace.NeuralState) {
        self.currentState = state
    }
    
    /// Measure quantum state
    public func measure() -> Double {
        return currentState.amplitude * currentState.amplitude
    }
    
    /// Check if state is in superposition
    public func isInSuperposition() -> Bool {
        return abs(currentState.amplitude) < 0.99
    }
    
    /// Check if state is entangled
    public func isEntangled() -> Bool {
        return currentState.isEntangled
    }
}
