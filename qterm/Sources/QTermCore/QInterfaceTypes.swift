import Foundation

public enum QuantumError: Error {
    case invalidCommand
    case stateTransitionFailed
    case measurementFailed
    case environmentError
}

public enum QuantumRole {
    case developer
    case reviewer
    case architect
    case tester
    
    var capabilities: Set<String> {
        switch self {
        case .developer:
            return ["code", "debug", "test"]
        case .reviewer:
            return ["review", "analyze", "suggest"]
        case .architect:
            return ["design", "optimize", "integrate"]
        case .tester:
            return ["test", "validate", "report"]
        }
    }
}

public struct ProcessManager {
    private let processQueue: DispatchQueue
    
    public init() {
        self.processQueue = DispatchQueue(label: "com.qterm.process", qos: .userInitiated)
    }
    
    public func run(_ command: String) async throws -> String {
        let process = Process()
        let pipe = Pipe()
        
        process.executableURL = URL(fileURLWithPath: "/bin/bash")
        process.arguments = ["-c", command]
        process.standardOutput = pipe
        
        try process.run()
        process.waitUntilExit()
        
        let data = try pipe.fileHandleForReading.readToEnd() ?? Data()
        return String(data: data, encoding: .utf8) ?? ""
    }
}

public enum QuantumState {
    case zero
    case one
    case plus
    case minus
    
    var amplitude: Double {
        switch self {
        case .zero, .one:
            return 1.0
        case .plus, .minus:
            return 1.0 / sqrt(2.0)
        }
    }
    
    var phase: Double {
        switch self {
        case .zero, .plus:
            return 0.0
        case .one:
            return .pi
        case .minus:
            return .pi / 2.0
        }
    }
}
