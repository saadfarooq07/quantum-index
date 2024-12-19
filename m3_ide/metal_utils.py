import Metal
import os
import numpy as np
from typing import Dict, Any, Optional, Tuple

class MetalLibrary:
    def __init__(self, device: Any, shader_path: str):
        self.device = device
        self.shader_path = shader_path
        self.library = None
        
    def load(self) -> bool:
        try:
            # Load Metal library from file
            with open(self.shader_path, 'r') as f:
                source = f.read()
                
            # Create options for compilation
            options = Metal.MTLCompileOptions.alloc().init()
            
            # Compile the library
            self.library = self.device.newLibraryWithSource_options_error_(
                source, options, None
            )[0]
            
            return True if self.library else False
        except Exception as e:
            print(f"Error loading Metal library: {e}")
            return False
    
    def get_function(self, name: str) -> Optional[Any]:
        if not self.library:
            return None
        return self.library.newFunctionWithName_(name)

class MetalCompute:
    EMBEDDING_DIM = 256
    MAX_SEQ_LENGTH = 512
    
    def __init__(self, shader_path: str):
        self.device = Metal.MTLCreateSystemDefaultDevice()
        self.command_queue = self.device.newCommandQueue()
        self.library = MetalLibrary(self.device, shader_path)
        self.pipelines: Dict[str, Any] = {}
        self.shared_buffers: Dict[str, Any] = {}
        
        # Quantization parameters
        self.scale = 0.1  # Adjust based on embedding distribution
        self.zero_point = 128.0  # Center point for uint8
        
    def initialize(self) -> bool:
        if not self.library.load():
            return False
            
        # Create compute pipelines
        pipeline_functions = [
            'embed', 'attention', 'feedforward', 'infer',
            'quantize_embeddings', 'ip_search', 'topk_reduce'
        ]
        
        for function_name in pipeline_functions:
            function = self.library.get_function(function_name)
            if not function:
                print(f"Failed to get function: {function_name}")
                return False
                
            pipeline = self.device.newComputePipelineStateWithFunction_error_(
                function, None
            )[0]
            if not pipeline:
                print(f"Failed to create pipeline for: {function_name}")
                return False
                
            self.pipelines[function_name] = pipeline
            
        # Initialize shared buffers
        self._initialize_shared_buffers()
        return True
    
    def _initialize_shared_buffers(self):
        # Create positional encodings
        position_encodings = np.zeros((self.MAX_SEQ_LENGTH, self.EMBEDDING_DIM), dtype=np.float32)
        for pos in range(self.MAX_SEQ_LENGTH):
            for i in range(0, self.EMBEDDING_DIM, 2):
                position_encodings[pos, i] = np.sin(pos / (10000 ** (i / self.EMBEDDING_DIM)))
                if i + 1 < self.EMBEDDING_DIM:
                    position_encodings[pos, i + 1] = np.cos(pos / (10000 ** (i / self.EMBEDDING_DIM)))
        
        # Create Metal buffer for position encodings
        self.shared_buffers['position_encodings'] = self.device.newBufferWithBytes_length_options_(
            position_encodings.tobytes(),
            position_encodings.nbytes,
            Metal.MTLResourceStorageModeShared
        )
        
        # Initialize layer normalization parameters
        layer_norm_weights = np.ones(4, dtype=np.float32)
        layer_norm_bias = np.zeros(4, dtype=np.float32)
        
        self.shared_buffers['layer_norm_weights'] = self.device.newBufferWithBytes_length_options_(
            layer_norm_weights.tobytes(),
            layer_norm_weights.nbytes,
            Metal.MTLResourceStorageModeShared
        )
        
        self.shared_buffers['layer_norm_bias'] = self.device.newBufferWithBytes_length_options_(
            layer_norm_bias.tobytes(),
            layer_norm_bias.nbytes,
            Metal.MTLResourceStorageModeShared
        )
    
    def process_batch(self, 
                     pipeline_name: str,
                     input_data: np.ndarray,
                     seq_length: Optional[int] = None) -> Optional[np.ndarray]:
        """Process data batch using Metal pipeline"""
        pipeline = self.pipelines.get(pipeline_name)
        if not pipeline:
            print(f"Pipeline not found: {pipeline_name}")
            return None
            
        if seq_length is None:
            seq_length = min(len(input_data), self.MAX_SEQ_LENGTH)
        
        try:
            # Create input buffer
            input_buffer = self.device.newBufferWithBytes_length_options_(
                input_data.tobytes(),
                input_data.nbytes,
                Metal.MTLResourceStorageModeShared
            )
            
            # Create output buffer
            output_size = input_data.nbytes
            output_buffer = self.device.newBufferWithLength_options_(
                output_size,
                Metal.MTLResourceStorageModeShared
            )
            
            # Create command buffer and encoder
            command_buffer = self.command_queue.commandBuffer()
            compute_encoder = command_buffer.computeCommandEncoder()
            
            # Set pipeline and buffers
            compute_encoder.setComputePipelineState_(pipeline)
            compute_encoder.setBuffer_offset_atIndex_(input_buffer, 0, 0)
            compute_encoder.setBuffer_offset_atIndex_(output_buffer, 0, 1)
            
            # Set additional buffers based on pipeline type
            if pipeline_name == 'embed':
                compute_encoder.setBuffer_offset_atIndex_(
                    self.shared_buffers['position_encodings'], 0, 2
                )
                compute_encoder.setBytes_length_atIndex_(
                    seq_length.to_bytes(4, byteorder='little'), 4, 3
                )
            elif pipeline_name == 'infer':
                compute_encoder.setBuffer_offset_atIndex_(
                    self.shared_buffers['layer_norm_weights'], 0, 2
                )
                compute_encoder.setBuffer_offset_atIndex_(
                    self.shared_buffers['layer_norm_bias'], 0, 3
                )
                compute_encoder.setBytes_length_atIndex_(
                    seq_length.to_bytes(4, byteorder='little'), 4, 4
                )
            
            # Configure grid and threadgroup sizes
            if pipeline_name == 'attention':
                grid_size = (seq_length, seq_length, 1)
                threadgroup_size = (16, 16, 1)
            else:
                threads_per_group = min(pipeline.maxTotalThreadsPerThreadgroup(), input_data.size)
                threadgroups = (input_data.size + threads_per_group - 1) // threads_per_group
                grid_size = (threadgroups, 1, 1)
                threadgroup_size = (threads_per_group, 1, 1)
            
            compute_encoder.dispatchThreadgroups_threadsPerThreadgroup_(
                grid_size, threadgroup_size
            )
            
            # End encoding and commit
            compute_encoder.endEncoding()
            command_buffer.commit()
            command_buffer.waitUntilCompleted()
            
            # Get result
            result = np.frombuffer(
                output_buffer.contents().as_buffer(output_buffer.length()),
                dtype=input_data.dtype
            )
            
            return result.reshape(input_data.shape)
            
        except Exception as e:
            print(f"Error processing batch: {e}")
            return None
            
    def process_sequence(self, input_sequence: np.ndarray) -> Optional[np.ndarray]:
        """Process a complete sequence through the entire pipeline"""
        try:
            # 1. Embedding
            embedded = self.process_batch('embed', input_sequence)
            if embedded is None:
                return None
                
            # 2. Self-attention
            attended = self.process_batch('attention', embedded)
            if attended is None:
                return None
                
            # 3. Feed-forward
            feedforward = self.process_batch('feedforward', attended)
            if feedforward is None:
                return None
                
            # 4. Final inference
            result = self.process_batch('infer', feedforward)
            return result
            
        except Exception as e:
            print(f"Error processing sequence: {e}")
            return None
    
    def quantize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Quantize embeddings to uint8 using Metal"""
        try:
            # Create input buffer
            input_buffer = self.device.newBufferWithBytes_length_options_(
                embeddings.tobytes(),
                embeddings.nbytes,
                Metal.MTLResourceStorageModeShared
            )
            
            # Create output buffer
            output_size = embeddings.size
            output_buffer = self.device.newBufferWithLength_options_(
                output_size,
                Metal.MTLResourceStorageModeShared
            )
            
            # Create command buffer and encoder
            command_buffer = self.command_queue.commandBuffer()
            compute_encoder = command_buffer.computeCommandEncoder()
            
            # Set pipeline and buffers
            compute_encoder.setComputePipelineState_(self.pipelines['quantize_embeddings'])
            compute_encoder.setBuffer_offset_atIndex_(input_buffer, 0, 0)
            compute_encoder.setBuffer_offset_atIndex_(output_buffer, 0, 1)
            
            # Set quantization parameters
            compute_encoder.setBytes_length_atIndex_(
                np.array([self.scale], dtype=np.float32).tobytes(), 4, 2
            )
            compute_encoder.setBytes_length_atIndex_(
                np.array([self.zero_point], dtype=np.float32).tobytes(), 4, 3
            )
            
            # Configure grid
            threads_per_group = min(
                self.pipelines['quantize_embeddings'].maxTotalThreadsPerThreadgroup(),
                embeddings.size
            )
            threadgroups = (embeddings.size + threads_per_group - 1) // threads_per_group
            
            compute_encoder.dispatchThreadgroups_threadsPerThreadgroup_(
                (threadgroups, 1, 1),
                (threads_per_group, 1, 1)
            )
            
            # End encoding and commit
            compute_encoder.endEncoding()
            command_buffer.commit()
            command_buffer.waitUntilCompleted()
            
            # Get result
            result = np.frombuffer(
                output_buffer.contents().as_buffer(output_buffer.length()),
                dtype=np.uint8
            )
            
            return result.reshape(embeddings.shape)
            
        except Exception as e:
            print(f"Error quantizing embeddings: {e}")
            return None
    
    def ip_search(self, 
                 query: np.ndarray, 
                 database: np.ndarray, 
                 k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Perform IP search using quantized embeddings"""
        try:
            num_vectors = len(database)
            vector_dim = database.shape[1]
            
            # Create buffers
            query_buffer = self.device.newBufferWithBytes_length_options_(
                query.tobytes(),
                query.nbytes,
                Metal.MTLResourceStorageModeShared
            )
            
            database_buffer = self.device.newBufferWithBytes_length_options_(
                database.tobytes(),
                database.nbytes,
                Metal.MTLResourceStorageModeShared
            )
            
            scores_buffer = self.device.newBufferWithLength_options_(
                num_vectors * 4,  # float32 scores
                Metal.MTLResourceStorageModeShared
            )
            
            indices_buffer = self.device.newBufferWithLength_options_(
                k * 4,  # uint32 indices
                Metal.MTLResourceStorageModeShared
            )
            
            top_scores_buffer = self.device.newBufferWithLength_options_(
                k * 4,  # float32 scores
                Metal.MTLResourceStorageModeShared
            )
            
            # Create command buffer
            command_buffer = self.command_queue.commandBuffer()
            
            # IP search
            compute_encoder = command_buffer.computeCommandEncoder()
            compute_encoder.setComputePipelineState_(self.pipelines['ip_search'])
            compute_encoder.setBuffer_offset_atIndex_(query_buffer, 0, 0)
            compute_encoder.setBuffer_offset_atIndex_(database_buffer, 0, 1)
            compute_encoder.setBuffer_offset_atIndex_(scores_buffer, 0, 2)
            compute_encoder.setBytes_length_atIndex_(
                np.array([num_vectors], dtype=np.uint32).tobytes(), 4, 3
            )
            compute_encoder.setBytes_length_atIndex_(
                np.array([vector_dim], dtype=np.uint32).tobytes(), 4, 4
            )
            
            threads_per_group = min(
                self.pipelines['ip_search'].maxTotalThreadsPerThreadgroup(),
                num_vectors
            )
            threadgroups = (num_vectors + threads_per_group - 1) // threads_per_group
            
            compute_encoder.dispatchThreadgroups_threadsPerThreadgroup_(
                (threadgroups, 1, 1),
                (threads_per_group, 1, 1)
            )
            compute_encoder.endEncoding()
            
            # Top-k reduction
            compute_encoder = command_buffer.computeCommandEncoder()
            compute_encoder.setComputePipelineState_(self.pipelines['topk_reduce'])
            compute_encoder.setBuffer_offset_atIndex_(scores_buffer, 0, 0)
            compute_encoder.setBuffer_offset_atIndex_(indices_buffer, 0, 1)
            compute_encoder.setBuffer_offset_atIndex_(top_scores_buffer, 0, 2)
            compute_encoder.setBytes_length_atIndex_(
                np.array([num_vectors], dtype=np.uint32).tobytes(), 4, 3
            )
            compute_encoder.setBytes_length_atIndex_(
                np.array([k], dtype=np.uint32).tobytes(), 4, 4
            )
            
            compute_encoder.dispatchThreadgroups_threadsPerThreadgroup_(
                (1, 1, 1),
                (min(num_vectors, 256), 1, 1)
            )
            compute_encoder.endEncoding()
            
            # Commit and wait
            command_buffer.commit()
            command_buffer.waitUntilCompleted()
            
            # Get results
            indices = np.frombuffer(
                indices_buffer.contents().as_buffer(indices_buffer.length()),
                dtype=np.uint32
            )
            
            scores = np.frombuffer(
                top_scores_buffer.contents().as_buffer(top_scores_buffer.length()),
                dtype=np.float32
            )
            
            return indices[:k], scores[:k]
            
        except Exception as e:
            print(f"Error in IP search: {e}")
            return None, None
