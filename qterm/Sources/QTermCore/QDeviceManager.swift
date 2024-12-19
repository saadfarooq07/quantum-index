import Foundation
import Metal
#if canImport(UIKit)
import UIKit
#else
import AppKit
#endif

/// QDeviceManager handles cross-device quantum computing capabilities
public class QDeviceManager {
    // MARK: - Device Properties
    public let deviceType: DeviceType
    public let metalCapabilities: MetalCapabilities
    public let neuralEngine: NeuralEngine
    
    // MARK: - Nested Types
    public enum DeviceType {
        case macM1
        case macM2
        case macM3
        case iPadM1
        case iPadM2
        case unknown
        
        public var hasNeuralEngine: Bool {
            switch self {
            case .unknown: return false
            default: return true
            }
        }
    }
    
    public struct MetalCapabilities {
        public let maxBufferLength: Int
        public let hasUnifiedMemory: Bool
        public let supportsFP16: Bool
        public let maxThreadgroupMemoryLength: Int
        
        init(device: MTLDevice) {
            self.maxBufferLength = device.maxBufferLength
            self.hasUnifiedMemory = device.hasUnifiedMemory
            self.supportsFP16 = device.supportsFamily(.apple3)
            self.maxThreadgroupMemoryLength = device.maxThreadgroupMemoryLength
        }
    }
    
    public class NeuralEngine {
        public let isAvailable: Bool
        public let performanceCores: Int
        public let efficiencyCores: Int
        
        init() {
            #if os(iOS)
            let device = UIDevice.current
            self.isAvailable = true  // All M1+ iPads have Neural Engine
            self.performanceCores = 8
            self.efficiencyCores = 2
            #else
            // On macOS, detect M-series chip
            let result = try? Process.run(URL(fileURLWithPath: "/usr/sbin/sysctl"), arguments: ["machdep.cpu.brand_string"])
            self.isAvailable = result?.terminationStatus == 0
            self.performanceCores = 8  // Default for M1/M2/M3
            self.efficiencyCores = 4
            #endif
        }
    }
    
    // MARK: - Initialization
    public init() throws {
        // Detect device type
        #if os(iOS)
        self.deviceType = QDeviceManager.getiPadType()
        #else
        self.deviceType = QDeviceManager.getMacType()
        #endif
        
        // Initialize Metal capabilities
        guard let metalDevice = MTLCreateSystemDefaultDevice() else {
            throw QuantumError.metalNotAvailable
        }
        self.metalCapabilities = MetalCapabilities(device: metalDevice)
        
        // Initialize Neural Engine
        self.neuralEngine = NeuralEngine()
    }
    
    // MARK: - Device Detection
    private static func getMacType() -> DeviceType {
        let result = try? Process.run(URL(fileURLWithPath: "/usr/sbin/sysctl"), arguments: ["machdep.cpu.brand_string"])
        guard let output = result?.standardOutput as? String else {
            return .unknown
        }
        
        if output.contains("M3") { return .macM3 }
        if output.contains("M2") { return .macM2 }
        if output.contains("M1") { return .macM1 }
        return .unknown
    }
    
    private static func getiPadType() -> DeviceType {
        #if os(iOS)
        let device = UIDevice.current
        // This is a simplified check - in production you'd want more robust detection
        if device.model.contains("iPad") {
            // You'd need to add more sophisticated iPad model detection here
            return .iPadM1
        }
        #endif
        return .unknown
    }
    
    // MARK: - Performance Optimization
    public func optimizeForDevice() -> [String: Any] {
        var config: [String: Any] = [:]
        
        switch deviceType {
        case .macM3:
            config["threadCount"] = 12
            config["useNeuralEngine"] = true
            config["memoryMode"] = "unified"
            config["metalPerformanceShaders"] = true
            
        case .macM2, .macM1:
            config["threadCount"] = 8
            config["useNeuralEngine"] = true
            config["memoryMode"] = "unified"
            config["metalPerformanceShaders"] = true
            
        case .iPadM1, .iPadM2:
            config["threadCount"] = 8
            config["useNeuralEngine"] = true
            config["memoryMode"] = "unified"
            config["metalPerformanceShaders"] = true
            
        case .unknown:
            config["threadCount"] = 4
            config["useNeuralEngine"] = false
            config["memoryMode"] = "discrete"
            config["metalPerformanceShaders"] = false
        }
        
        return config
    }
    
    // MARK: - Resource Management
    public func getOptimalThreadCount() -> Int {
        switch deviceType {
        case .macM3: return 12
        case .macM2, .macM1, .iPadM1, .iPadM2: return 8
        case .unknown: return 4
        }
    }
    
    public func getMemoryLimit() -> UInt64 {
        switch deviceType {
        case .macM3: return 32 * 1024 * 1024 * 1024  // 32GB
        case .macM2, .macM1: return 16 * 1024 * 1024 * 1024  // 16GB
        case .iPadM1, .iPadM2: return 8 * 1024 * 1024 * 1024  // 8GB
        case .unknown: return 4 * 1024 * 1024 * 1024  // 4GB
        }
    }
}
