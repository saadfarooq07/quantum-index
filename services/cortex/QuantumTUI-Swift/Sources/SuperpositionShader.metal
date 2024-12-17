#include <metal_stdlib>
#include <metal_matrix>
using namespace metal;

struct SuperpositionVertex {
    float4 position [[position]];
    float2 texCoord;
    half4  color;
};

struct SuperpositionUniforms {
    float4x4 modelMatrix;
    float4x4 viewMatrix;
    float time;
};

// Quantum state visualization
vertex SuperpositionVertex quantum_vertex(
    uint vertexID [[vertex_id]],
    constant SuperpositionUniforms& uniforms [[buffer(0)]]
) {
    SuperpositionVertex out;
    float4x4 mvp = uniforms.viewMatrix * uniforms.modelMatrix;
    
    // Generate quantum interference pattern
    float phase = uniforms.time * 0.1;
    float amplitude = sin(phase + float(vertexID) * 0.1);
    
    out.position = mvp * float4(amplitude, 0.0, 0.0, 1.0);
    out.texCoord = float2(amplitude * 0.5 + 0.5, 0.0);
    out.color = half4(amplitude * 0.5 + 0.5);
    
    return out;
}

// Quantum state fragment shader
fragment half4 quantum_fragment(
    SuperpositionVertex in [[stage_in]],
    texture2d<half> quantumTexture [[texture(0)]]
) {
    constexpr sampler textureSampler(
        filter::linear,
        address::repeat
    );
    
    half4 color = quantumTexture.sample(textureSampler, in.texCoord);
    return color * in.color;
}
