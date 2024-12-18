import Foundation

public enum QuantumError: Error {
    case metalNotAvailable
    case invalidState
    case processingError
    case memoryLimitExceeded
    case metalLibraryNotFound
    case metalFunctionNotFound
    case metalBufferCreationFailed
    
    public var description: String {
        switch self {
        case .metalNotAvailable:
            return "Metal acceleration is not available on this device"
        case .invalidState:
            return "Invalid quantum state"
        case .processingError:
            return "Error processing quantum operation"
        case .memoryLimitExceeded:
            return "Memory limit exceeded for quantum operation"
        case .metalLibraryNotFound:
            return "Metal shader library not found"
        case .metalFunctionNotFound:
            return "Metal shader function not found"
        case .metalBufferCreationFailed:
            return "Failed to create Metal buffers"
        }
    }
}
