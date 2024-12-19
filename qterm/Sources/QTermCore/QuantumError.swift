import Foundation

/// Quantum computation and reality-anchoring errors
public enum QuantumError: Error {
    // MARK: - Metal Errors
    case metalNotAvailable
    case metalLibraryNotFound
    case metalFunctionNotFound
    case metalBufferCreationFailed
    case metalEncodingFailed
    
    // MARK: - Reality Anchoring Errors
    case realityScoreTooLow(score: Double)
    case realityCheckFailed(reason: String)
    case coherenceLost(state: String)
    
    // MARK: - State Management Errors
    case invalidState
    case invalidStateTransition(from: String, to: String)
    case invalidRoleTransition
    case processingError
    case memoryLimitExceeded
    
    // MARK: - Neural Engine Errors
    case neuralEngineNotAvailable
    case neuralProcessingFailed(reason: String)
    
    public var description: String {
        switch self {
        // Metal Errors
        case .metalNotAvailable:
            return "Metal acceleration is not available on this device"
        case .metalLibraryNotFound:
            return "Metal shader library not found"
        case .metalFunctionNotFound:
            return "Metal shader function not found"
        case .metalBufferCreationFailed:
            return "Failed to create Metal buffers"
        case .metalEncodingFailed:
            return "Failed to encode Metal commands"
            
        // Reality Anchoring Errors    
        case .realityScoreTooLow(let score):
            return "Reality score (⚛️ \(String(format: "%.2f", score))) is below threshold"
        case .realityCheckFailed(let reason):
            return "Reality check failed: \(reason)"
        case .coherenceLost(let state):
            return "Quantum coherence lost in state: \(state)"
            
        // State Management Errors
        case .invalidState:
            return "Invalid quantum state"
        case .invalidStateTransition(let from, let to):
            return "Invalid state transition from \(from) to \(to)"
        case .invalidRoleTransition:
            return "Invalid role transition in current phase"
        case .processingError:
            return "Error processing quantum operation"
        case .memoryLimitExceeded:
            return "Memory limit exceeded for quantum operation"
            
        // Neural Engine Errors
        case .neuralEngineNotAvailable:
            return "Neural Engine is not available on this device"
        case .neuralProcessingFailed(let reason):
            return "Neural processing failed: \(reason)"
        }
    }
    
    /// Get user-friendly recovery suggestion
    public var recoverySuggestion: String {
        switch self {
        case .realityScoreTooLow:
            return "Try reducing quantum operations complexity or adding more reality anchors"
        case .coherenceLost:
            return "Re-initialize quantum state and add more coherence checks"
        case .invalidRoleTransition:
            return "Complete current phase before switching roles"
        case .memoryLimitExceeded:
            return "Try batching operations or reducing quantum state size"
        default:
            return "Check system requirements and try again"
        }
    }
}
