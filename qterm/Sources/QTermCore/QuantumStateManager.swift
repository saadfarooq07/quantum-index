import Foundation
import Metal

/// Manages quantum states and operations with Metal acceleration
public class QuantumStateManager {
    private let metalCompute: MetalCompute?
    private var currentState: QuantumVector
    private let deviceManager: QDeviceManager
    private var currentRole: QuantumRole = .productManager
    private var currentPhase: QuantumPhase = .requirements
    private var stateHistory: [(QuantumRole, QuantumPhase, QuantumVector)] = []
    
    // MARK: - Initialization
    
    public init(enableMetal: Bool = true) throws {
        self.deviceManager = try QDeviceManager()
        
        // Initialize Metal compute if enabled
        if enableMetal {
            do {
                self.metalCompute = try MetalCompute()
                if deviceManager.neuralEngine.isAvailable {
                    print("⚡️ Neural Engine active with \(deviceManager.neuralEngine.performanceCores) performance cores")
                }
            } catch {
                print("⚠️ Metal initialization failed: \(error)")
                self.metalCompute = nil
            }
        } else {
            self.metalCompute = nil
        }
        
        // Initialize to |0⟩ state
        self.currentState = QuantumVector.standardBasis(.zero)
    }
    
    // MARK: - State Management
    
    /// Check memory constraints
    private func checkMemoryConstraints() throws {
        let memLimit = deviceManager.getMemoryLimit()
        if currentState.memoryFootprint > memLimit {
            throw QuantumError.memoryLimitExceeded
        }
    }
    
    /// Set quantum state
    public func setState(_ state: QuantumState) throws -> String {
        try checkMemoryConstraints()
        currentState = QuantumVector.standardBasis(state)
        return "Set state to \(state)"
    }
    
    /// Apply a quantum gate
    public func applyGate(_ gate: QuantumGate) throws -> String {
        if let metalCompute = metalCompute {
            currentState = try metalCompute.processQuantumState(currentState, gate: gate)
            return "Applied \(gate) gate using Metal"
        } else {
            currentState = currentState.applyGate(gate.matrix.map { row in
                row.map { Float($0.real) }
            })
            return "Applied \(gate) gate"
        }
    }
    
    /// Measure the current state
    public func measure() -> String {
        let probability = currentState.measure()
        return String(format: "Measured state with probability: %.2f", probability)
    }
    
    /// Reset to |0⟩ state
    public func reset() -> String {
        currentState = QuantumVector.standardBasis(.zero)
        return "Reset to |0⟩"
    }
    
    /// Get device information
    public func deviceInfo() -> String {
        var info = ["Quantum Device Info:"]
        
        if metalCompute != nil {
            info.append("- Metal acceleration: Active")
            if deviceManager.neuralEngine.isAvailable {
                info.append("- Neural Engine: \(deviceManager.neuralEngine.performanceCores) cores")
            }
        } else {
            info.append("- Metal acceleration: Inactive")
        }
        
        info.append("- Memory limit: \(deviceManager.getMemoryLimit() / 1024 / 1024)MB")
        info.append("- Current state footprint: \(currentState.memoryFootprint) bytes")
        
        return info.joined(separator: "\n")
    }
    
    // MARK: - SDLC State Management
    
    /// Switch to a different role
    public func switchRole(_ role: QuantumRole) throws -> String {
        // Save current state
        stateHistory.append((currentRole, currentPhase, currentState))
        
        // Quantum transformation for role switch
        let roleGate = try generateRoleGate(role)
        try applyGate(roleGate)
        
        currentRole = role
        return "Switched to \(role.rawValue) role with quantum coherence"
    }
    
    /// Advance to next SDLC phase
    public func advancePhase() throws -> String {
        let nextPhase: QuantumPhase
        switch currentPhase {
        case .requirements: nextPhase = .design
        case .design: nextPhase = .implementation
        case .implementation: nextPhase = .testing
        case .testing: nextPhase = .deployment
        case .deployment: throw QuantumError.invalidPhaseTransition
        }
        
        // Quantum phase transition
        let phaseGate = try generatePhaseGate(nextPhase)
        try applyGate(phaseGate)
        
        currentPhase = nextPhase
        return "Advanced to \(nextPhase.rawValue) phase with quantum coherence"
    }
    
    /// Generate quantum gate for role transition
    private func generateRoleGate(_ targetRole: QuantumRole) throws -> QuantumGate {
        // Create superposition between current and target role states
        return try QuantumGate.hadamard.controlled(by: currentRole.rawValue)
    }
    
    /// Generate quantum gate for phase transition
    private func generatePhaseGate(_ targetPhase: QuantumPhase) throws -> QuantumGate {
        // Create phase rotation based on SDLC stage
        return try QuantumGate.phase(angle: Float.pi / Float(QuantumPhase.allCases.count))
    }
}

/// Quantum SDLC Role States
public enum QuantumRole: String {
    case productManager = "PM"
    case architect = "ARCH"
    case engineer = "ENG"
    case qaEngineer = "QA"
}

/// Quantum SDLC Phase States 
public enum QuantumPhase: String {
    case requirements = "REQ"
    case design = "DES" 
    case implementation = "IMP"
    case testing = "TEST"
    case deployment = "DEP"
}
