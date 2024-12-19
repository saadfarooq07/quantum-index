import Foundation
import Metal

public class QNeuralCompute {
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private let library: MTLLibrary
    
    public init() throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw QError.metalDeviceNotFound
        }
        self.device = device
        
        guard let queue = device.makeCommandQueue() else {
            throw QError.metalQueueCreationFailed
        }
        self.commandQueue = queue
        
        guard let library = device.makeDefaultLibrary() else {
            throw QError.metalLibraryNotFound
        }
        self.library = library
    }
    
    /// Process quantum state with Metal acceleration
    public func process(_ state: QNeuralState, gate: QGate) throws -> QNeuralState {
        // Create command buffer
        guard let commandBuffer = commandQueue.makeCommandBuffer() else {
            throw QError.metalBufferCreationFailed
        }
        
        // Get Metal function for gate
        let function = try getMetalFunction(for: gate)
        
        // Create compute pipeline state
        let pipelineState = try device.makeComputePipelineState(function: function)
        
        // Create encoder
        guard let encoder = commandBuffer.makeComputeCommandEncoder() else {
            throw QError.metalBufferCreationFailed
        }
        
        // Set pipeline state
        encoder.setComputePipelineState(pipelineState)
        
        // Create input buffer
        let inputData = [Float(state.amplitude), Float(state.phase)]
        let inputBuffer = device.makeBuffer(bytes: inputData,
                                          length: MemoryLayout<Float>.size * 2,
                                          options: .storageModeShared)
        encoder.setBuffer(inputBuffer, offset: 0, index: 0)
        
        // Create output buffer
        let outputBuffer = device.makeBuffer(length: MemoryLayout<Float>.size * 2,
                                           options: .storageModeShared)
        encoder.setBuffer(outputBuffer, offset: 0, index: 1)
        
        // Dispatch threads
        let gridSize = MTLSize(width: 1, height: 1, depth: 1)
        let threadGroupSize = MTLSize(width: 1, height: 1, depth: 1)
        encoder.dispatchThreadgroups(gridSize, threadsPerThreadgroup: threadGroupSize)
        
        // End encoding
        encoder.endEncoding()
        
        // Commit and wait
        commandBuffer.commit()
        commandBuffer.waitUntilCompleted()
        
        // Parse results
        return try parseMetalBuffer(outputBuffer!)
    }
    
    // MARK: - Private Methods
    
    private func getMetalFunction(for gate: QGate) throws -> MTLFunction {
        let functionName: String
        
        switch gate {
        case .hadamard:
            functionName = "hadamard_gate"
        case .cnot:
            functionName = "cnot_gate"
        case .phase:
            functionName = "phase_gate"
        case .custom:
            functionName = "custom_gate"
        }
        
        guard let function = library.makeFunction(name: functionName) else {
            throw QError.metalFunctionNotFound
        }
        return function
    }
    
    private func parseMetalBuffer(_ buffer: MTLBuffer) throws -> QNeuralState {
        let data = Data(bytesNoCopy: buffer.contents(),
                       count: buffer.length,
                       deallocator: .none)
        
        var amplitude: Float = 0
        var phase: Float = 0
        
        data.withUnsafeBytes { ptr in
            let floatPtr = ptr.bindMemory(to: Float.self)
            amplitude = floatPtr[0]
            phase = floatPtr[1]
        }
        
        return QNeuralState(
            amplitude: Double(amplitude),
            phase: Double(phase)
        )
    }
}

public enum QError: Error {
    case metalDeviceNotFound
    case metalQueueCreationFailed
    case metalLibraryNotFound
    case metalBufferCreationFailed
    case metalFunctionNotFound
}

public enum QGate {
    case hadamard
    case cnot
    case phase(Double)
    case custom(String)
}

public struct QNeuralState {
    let amplitude: Double
    let phase: Double
    
    init(amplitude: Double, phase: Double) {
        self.amplitude = amplitude
        self.phase = phase
    }
    
    func toMetalBuffer(device: MTLDevice) throws -> MTLBuffer {
        let inputData = [amplitude, phase]
        guard let buffer = device.makeBuffer(bytes: inputData,
                                            length: inputData.count * MemoryLayout<Double>.size,
                                            options: .storageModeShared) else {
            throw QError.metalBufferCreationFailed
        }
        return buffer
    }
    
    static func fromMetalBuffer(_ buffer: MTLBuffer) -> QNeuralState {
        let data = Data(bytesNoCopy: buffer.contents(),
                        count: buffer.length,
                        deallocator: .none)
        
        let outputArray = data.withUnsafeBytes { pointer in
            Array(UnsafeBufferPointer(start: pointer.bindMemory(to: Double.self).baseAddress,
                                    count: buffer.length / MemoryLayout<Double>.size))
        }
        
        return QNeuralState(
            amplitude: outputArray[0],
            phase: outputArray[1]
        )
    }
}
