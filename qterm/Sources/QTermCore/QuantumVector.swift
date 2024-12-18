import Foundation
import simd

/// Complex number representation
public struct Complex {
    public let real: Float
    public let imag: Float
    
    public init(real: Float, imag: Float = 0) {
        self.real = real
        self.imag = imag
    }
    
    public static func *(lhs: Complex, rhs: Complex) -> Complex {
        return Complex(
            real: lhs.real * rhs.real - lhs.imag * rhs.imag,
            imag: lhs.real * rhs.imag + lhs.imag * rhs.real
        )
    }
    
    public static func +(lhs: Complex, rhs: Complex) -> Complex {
        return Complex(
            real: lhs.real + rhs.real,
            imag: lhs.imag + rhs.imag
        )
    }
}

/// Quantum state basis
public enum QuantumState: CustomStringConvertible {
    case zero
    case one
    case plus
    case minus
    
    public var description: String {
        switch self {
        case .zero: return "|0⟩"
        case .one: return "|1⟩"
        case .plus: return "|+⟩"
        case .minus: return "|-⟩"
        }
    }
}

/// Common quantum gates optimized for M3
public enum QuantumGate: CustomStringConvertible {
    case hadamard
    case pauliX
    case pauliY
    case pauliZ
    case phase(Float)
    
    public var description: String {
        switch self {
        case .hadamard: return "H"
        case .pauliX: return "X"
        case .pauliY: return "Y"
        case .pauliZ: return "Z"
        case .phase(let phi): return "P(\(phi))"
        }
    }
    
    public var matrix: [[Complex]] {
        switch self {
        case .hadamard:
            let h = Float(1.0 / sqrt(2.0))
            return [
                [Complex(real: h), Complex(real: h)],
                [Complex(real: h), Complex(real: -h)]
            ]
        case .pauliX:
            return [
                [Complex(real: 0), Complex(real: 1)],
                [Complex(real: 1), Complex(real: 0)]
            ]
        case .pauliY:
            return [
                [Complex(real: 0), Complex(real: 0, imag: -1)],
                [Complex(real: 0, imag: 1), Complex(real: 0)]
            ]
        case .pauliZ:
            return [
                [Complex(real: 1), Complex(real: 0)],
                [Complex(real: 0), Complex(real: -1)]
            ]
        case .phase(let phi):
            return [
                [Complex(real: 1), Complex(real: 0)],
                [Complex(real: 0), Complex(real: cos(phi), imag: sin(phi))]
            ]
        }
    }
    
    public var metalBuffer: [Float] {
        let m = matrix
        return [
            m[0][0].real, m[0][0].imag, m[0][1].real, m[0][1].imag,
            m[1][0].real, m[1][0].imag, m[1][1].real, m[1][1].imag
        ]
    }
}

/// Represents a quantum state vector with optimized M3 operations
public struct QuantumVector {
    /// The underlying vector data using simd for M3 optimization
    private var data: simd_float4
    
    public init(components: [Float]) {
        precondition(components.count <= 4, "Currently supporting up to 2-qubit states")
        let padded = components + Array(repeating: 0.0, count: 4 - components.count)
        self.data = simd_float4(padded[0], padded[1], padded[2], padded[3])
    }
    
    /// Create a standard basis state
    public static func standardBasis(_ state: QuantumState) -> QuantumVector {
        switch state {
        case .zero:
            return QuantumVector(components: [1, 0])
        case .one:
            return QuantumVector(components: [0, 1])
        case .plus:
            let h = Float(1.0 / sqrt(2.0))
            return QuantumVector(components: [h, h])
        case .minus:
            let h = Float(1.0 / sqrt(2.0))
            return QuantumVector(components: [h, -h])
        }
    }
    
    /// Compute inner product with another vector
    public func innerProduct(with other: QuantumVector) -> Float {
        simd_dot(self.data, other.data)
    }
    
    /// Apply a quantum gate (represented as a 2x2 matrix)
    public func applyGate(_ gate: [[Float]]) -> QuantumVector {
        precondition(gate.count == 2 && gate[0].count == 2, "Gate must be 2x2")
        
        let result = simd_float4(
            gate[0][0] * data[0] + gate[0][1] * data[1],
            gate[1][0] * data[0] + gate[1][1] * data[1],
            0, 0
        )
        return QuantumVector(data: result)
    }
    
    /// Get the Metal-compatible buffer representation
    public var metalBuffer: [Float] {
        [data.x, data.y, data.z, data.w]
    }
    
    /// Initialize directly with simd_float4
    private init(data: simd_float4) {
        self.data = data
    }
    
    /// Get the components as Complex numbers
    public var components: [Complex] {
        [Complex(real: data.x), Complex(real: data.y)]
    }
    
    /// Memory footprint in bytes
    public var memoryFootprint: Int {
        MemoryLayout<simd_float4>.size
    }
    
    /// Measure the quantum state
    public func measure() -> Double {
        Double(data.x * data.x)
    }
    
    /// Get string representation
    public var description: String {
        let c = components
        return String(format: "%.3f|0⟩ + %.3f|1⟩", c[0].real, c[1].real)
    }
}
