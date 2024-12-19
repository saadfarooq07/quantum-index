import Foundation

/// Namespace for quantum types
public enum QuantumNamespace {
    /// Mode for quantum processing
    public enum Mode {
        case cpu
        case gpu
        case hybrid
    }
    
    /// Performance metrics
    public struct Performance {
        let speed: Double
        let accuracy: Double
        let efficiency: Double
        
        public init(speed: Double, accuracy: Double, efficiency: Double) {
            self.speed = speed
            self.accuracy = accuracy
            self.efficiency = efficiency
        }
    }
    
    /// Neural state for quantum operations
    public struct NeuralState {
        let id: UUID
        let amplitude: Double
        let phase: Double
        let isEntangled: Bool
        let size: Int
        
        public init(
            id: UUID = UUID(),
            amplitude: Double,
            phase: Double,
            isEntangled: Bool = false,
            size: Int = 1024
        ) {
            self.id = id
            self.amplitude = amplitude
            self.phase = phase
            self.isEntangled = isEntangled
            self.size = size
        }
    }
    
    /// Error types
    public enum QError: Error {
        case metalDeviceNotFound
        case metalQueueCreationFailed
        case metalLibraryNotFound
        case metalFunctionNotFound
        case metalBufferCreationFailed
        case invalidState
        case measurementFailed
    }
    
    /// Gate operations
    public enum Gate {
        case hadamard
        case cnot
        case phase
        case custom(matrix: [[Complex]])
    }
    
    /// Complex number support
    public struct Complex {
        let real: Double
        let imaginary: Double
        
        public init(real: Double, imaginary: Double = 0) {
            self.real = real
            self.imaginary = imaginary
        }
    }
}

/// Type alias for easier access
public typealias QNeuralState = QuantumNamespace.NeuralState
public typealias QGate = QuantumNamespace.Gate
public typealias QError = QuantumNamespace.QError
public typealias QMode = QuantumNamespace.Mode
public typealias QPerformance = QuantumNamespace.Performance
public typealias QComplex = QuantumNamespace.Complex
