import Foundation

public enum WriterError: Error {
    case fileNotTracked
    case invalidState
    case transformationFailed
}

public struct TextChange {
    public let range: NSRange
    public let text: String
    public let type: ChangeType
    
    public enum ChangeType {
        case insert
        case delete
        case replace
    }
    
    public init(range: NSRange, text: String, type: ChangeType) {
        self.range = range
        self.text = text
        self.type = type
    }
}

public struct CursorPosition {
    public let line: Int
    public let column: Int
    public let file: String
    
    public init(line: Int, column: Int, file: String) {
        self.line = line
        self.column = column
        self.file = file
    }
}

public struct Completion {
    public let text: String
    public let type: CompletionType
    public let confidence: Double
    
    public enum CompletionType {
        case code
        case documentation
        case quantum
    }
    
    public init(text: String, type: CompletionType, confidence: Double) {
        self.text = text
        self.type = type
        self.confidence = confidence
    }
}

public struct EnvironmentObservation {
    public let cpuUsage: Double
    public let memoryUsage: Double
    public let gpuUsage: Double
    public let timestamp: Date
    
    public init() {
        self.timestamp = Date()
        self.cpuUsage = ProcessInfo.processInfo.systemUptime
        self.memoryUsage = Double(ProcessInfo.processInfo.physicalMemory)
        self.gpuUsage = 0 // Would need Metal API to get actual GPU usage
    }
}

public struct QuantumVector {
    public let components: [Double]
    
    public init(components: [Double]) {
        self.components = components
    }
    
    public static func combine(_ vectors: [QuantumVector]) throws -> QuantumVector {
        guard !vectors.isEmpty else { return QuantumVector(components: []) }
        let size = vectors[0].components.count
        var combined = Array(repeating: 0.0, count: size)
        
        for vector in vectors {
            guard vector.components.count == size else {
                throw WriterError.transformationFailed
            }
            for i in 0..<size {
                combined[i] += vector.components[i]
            }
        }
        
        // Normalize
        let norm = sqrt(combined.reduce(0) { $0 + $1 * $1 })
        if norm > 0 {
            combined = combined.map { $0 / norm }
        }
        
        return QuantumVector(components: combined)
    }
    
    public static var identity: QuantumVector {
        QuantumVector(components: [1, 0])
    }
    
    public func overlap(with other: QuantumVector) throws -> Double {
        guard components.count == other.components.count else {
            throw WriterError.transformationFailed
        }
        
        var sum = 0.0
        for i in 0..<components.count {
            sum += components[i] * other.components[i]
        }
        return abs(sum)
    }
}
