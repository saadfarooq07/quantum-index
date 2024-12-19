import Foundation
import Metal

/// Metal-accelerated quantum computing
public class MetalCompute {
    // MARK: - Properties
    private let device: MTLDevice
    private let commandQueue: MTLCommandQueue
    private let library: MTLLibrary
    
    // MARK: - Initialization
    public init() throws {
        guard let device = MTLCreateSystemDefaultDevice() else {
            throw Q.QError.metalDeviceNotFound
        }
        self.device = device
        
        guard let queue = device.makeCommandQueue() else {
            throw Q.QError.metalQueueCreationFailed
        }
        self.commandQueue = queue
        
        guard let library = try? device.makeDefaultLibrary() else {
            throw Q.QError.metalLibraryNotFound
        }
        self.library = library
    }
    
    // MARK: - Public Methods
    /// Process quantum state with Metal acceleration
    public func process(_ state: Q.NeuralState, gate: Q.Gate) throws -> Q.NeuralState {
        // Create command buffer
        guard let commandBuffer = commandQueue.makeCommandBuffer() else {
            throw Q.QError.metalQueueCreationFailed
        }
        
        // Create Metal buffers
        let inputBuffer = try state.toMetalBuffer(device: device)
        guard let outputBuffer = device.makeBuffer(length: MemoryLayout<Double>.size * 4,
                                                 options: .storageModeShared) else {
            throw Q.QError.metalBufferCreationFailed
        }
        
        // Create compute command encoder
        guard let encoder = commandBuffer.makeComputeCommandEncoder() else {
            throw Q.QError.metalQueueCreationFailed
        }
        
        // Set compute pipeline state
        let function = try getMetalFunction(for: gate)
        let pipelineState = try device.makeComputePipelineState(function: function)
        
        encoder.setComputePipelineState(pipelineState)
        encoder.setBuffer(inputBuffer, offset: 0, index: 0)
        encoder.setBuffer(outputBuffer, offset: 0, index: 1)
        
        // Configure and dispatch threadgroups
        let gridSize = MTLSize(width: 1, height: 1, depth: 1)
        let threadGroupSize = MTLSize(width: 1, height: 1, depth: 1)
        
        encoder.dispatchThreadgroups(gridSize, threadsPerThreadgroup: threadGroupSize)
        encoder.endEncoding()
        
        // Execute command buffer
        commandBuffer.commit()
        commandBuffer.waitUntilCompleted()
        
        // Return processed state
        return Q.NeuralState.fromMetalBuffer(outputBuffer)
    }
    
    // MARK: - Private Methods
    private func getMetalFunction(for gate: Q.Gate) throws -> MTLFunction {
        let functionName: String
        
        switch gate {
        case .hadamard:
            functionName = "hadamard_gate"
        case .cnot:
            functionName = "cnot_gate"
        case .custom(let name):
            functionName = "\(name)_gate"
        }
        
        guard let function = library.makeFunction(name: functionName) else {
            throw Q.QError.metalLibraryNotFound
        }
        
        return function
    }
}
