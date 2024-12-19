import Foundation

public struct NetworkConfig {
    public let ports: [Port]
    public let volumes: [Volume]
    
    public init(ports: [Port] = [], volumes: [Volume] = []) {
        self.ports = ports
        self.volumes = volumes
    }
}

public struct StorageConfig {
    public let size: String
    public let type: StorageType
    public let mountPath: String
    
    public enum StorageType {
        case persistent
        case ephemeral
    }
    
    public init(size: String, type: StorageType, mountPath: String) {
        self.size = size
        self.type = type
        self.mountPath = mountPath
    }
}

public struct QuantumConfig {
    public let qubits: Int
    public let errorCorrection: Bool
    public let backend: String
    
    public init(qubits: Int = 1, errorCorrection: Bool = false, backend: String = "simulator") {
        self.qubits = qubits
        self.errorCorrection = errorCorrection
        self.backend = backend
    }
}

public struct Port {
    public let host: Int
    public let container: Int
    public let transportProtocol: PortProtocol
    
    public enum PortProtocol {
        case tcp
        case udp
    }
    
    public init(host: Int, container: Int, transportProtocol: PortProtocol) {
        self.host = host
        self.container = container
        self.transportProtocol = transportProtocol
    }
}

public struct Volume {
    public let source: String
    public let target: String
    public let type: VolumeType
    
    public enum VolumeType {
        case bind
        case volume
        case tmpfs
    }
    
    public init(source: String, target: String, type: VolumeType) {
        self.source = source
        self.target = target
        self.type = type
    }
}
