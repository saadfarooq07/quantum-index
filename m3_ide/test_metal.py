import numpy as np
from metal_utils import MetalCompute
import os

def test_metal_compute():
    # Initialize Metal compute with shader path
    shader_path = os.path.join(os.path.dirname(__file__), 'Shaders.metal')
    metal = MetalCompute(shader_path)
    
    # Initialize Metal resources
    if not metal.initialize():
        print("Failed to initialize Metal resources")
        return
        
    # Create test data
    input_data = np.array([0.5, -1.0, 2.0, -0.3], dtype=np.float32)
    print("\nInput data:", input_data)
    
    # Test embedding pipeline
    print("\nTesting embedding pipeline...")
    embed_result = metal.process_batch('embed', input_data)
    if embed_result is not None:
        print("Embedding result:", embed_result)
    else:
        print("Embedding failed")
    
    # Test inference pipeline
    print("\nTesting inference pipeline...")
    infer_result = metal.process_batch('infer', input_data)
    if infer_result is not None:
        print("Inference result:", infer_result)
    else:
        print("Inference failed")

if __name__ == '__main__':
    test_metal_compute()
