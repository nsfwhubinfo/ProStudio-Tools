import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function SpinningShadowBall({ thoughtData, coherence, phase }) {
  const sphereRef = useRef()
  const materialRef = useRef()
  
  // Create sphere geometry with higher resolution
  const geometry = useMemo(() => {
    return new THREE.SphereGeometry(3, 64, 64)
  }, [])
  
  // Convert thought data to spherical mapping
  const sphericalTexture = useMemo(() => {
    if (!thoughtData) return null
    
    const size = Math.sqrt(thoughtData.length)
    const sphereData = new Float32Array(size * size * 4)
    
    // Map 2D thought data to sphere surface
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        const idx = (i * size + j) * 4
        const value = thoughtData[i * size + j]
        
        // R: Base value
        sphereData[idx] = value
        // G: Gamma ray intensity (high values)
        sphereData[idx + 1] = value > 0.7 ? value : 0
        // B: Coherence modulation
        sphereData[idx + 2] = value * coherence
        // A: Alpha
        sphereData[idx + 3] = 1.0
      }
    }
    
    const texture = new THREE.DataTexture(
      sphereData,
      size,
      size,
      THREE.RGBAFormat,
      THREE.FloatType
    )
    texture.needsUpdate = true
    return texture
  }, [thoughtData, coherence])
  
  // Shader for shadow ball effect
  const shaders = useMemo(() => ({
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      void main() {
        vUv = uv;
        vNormal = normalize(normalMatrix * normal);
        vPosition = position;
        
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec2 vUv;
      varying vec3 vNormal;
      varying vec3 vPosition;
      
      uniform sampler2D thoughtTexture;
      uniform float coherence;
      uniform vec3 phaseColor;
      uniform float time;
      
      void main() {
        // Sample thought data
        vec4 thought = texture2D(thoughtTexture, vUv);
        
        // Shadow ball effect: darkness = low probability
        float probability = thought.r;
        float shadow = 1.0 - probability;
        
        // Gamma ray regions (high fitness)
        float gamma = thought.g;
        
        // Base shadow color
        vec3 shadowColor = vec3(0.0, 0.0, 0.0);
        
        // Phase-based inner glow
        vec3 glowColor = phaseColor * probability;
        
        // Gamma ray highlights
        if (gamma > 0.0) {
          glowColor += vec3(1.0, 1.0, 0.0) * gamma * 2.0;
          
          // Pulsing effect for high-energy regions
          float pulse = sin(time * 5.0 + vPosition.x * 10.0) * 0.5 + 0.5;
          glowColor += vec3(1.0, 0.8, 0.0) * gamma * pulse;
        }
        
        // Fresnel effect for ethereal appearance
        vec3 viewDirection = normalize(cameraPosition - vPosition);
        float fresnel = pow(1.0 - dot(viewDirection, vNormal), 2.0);
        
        // Combine shadow and glow
        vec3 finalColor = mix(shadowColor, glowColor, probability);
        finalColor += phaseColor * fresnel * 0.5;
        
        // Coherence affects overall brightness
        finalColor *= (0.5 + coherence * 0.5);
        
        gl_FragColor = vec4(finalColor, 0.9);
      }
    `
  }), [])
  
  // Animation
  useFrame((state) => {
    if (sphereRef.current) {
      // Continuous rotation
      sphereRef.current.rotation.y += 0.005
      sphereRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.5) * 0.1
      
      // Slight floating motion
      sphereRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.2
    }
    
    if (materialRef.current) {
      materialRef.current.uniforms.time.value = state.clock.elapsedTime
      materialRef.current.uniforms.coherence.value = coherence
    }
  })
  
  const phaseColors = {
    chaos: new THREE.Color(0x440044),
    emergence: new THREE.Color(0x004444), 
    structuring: new THREE.Color(0x444400),
    crystallized: new THREE.Color(0x00ff44)
  }
  
  return (
    <group>
      <mesh ref={sphereRef} geometry={geometry}>
        <shaderMaterial
          ref={materialRef}
          vertexShader={shaders.vertexShader}
          fragmentShader={shaders.fragmentShader}
          uniforms={{
            thoughtTexture: { value: sphericalTexture },
            time: { value: 0 },
            coherence: { value: coherence },
            phaseColor: { value: phaseColors[phase] || phaseColors.chaos }
          }}
          transparent
          side={THREE.DoubleSide}
        />
      </mesh>
      
      {/* Outer glow sphere */}
      <mesh scale={[1.1, 1.1, 1.1]}>
        <sphereGeometry args={[3, 32, 32]} />
        <meshBasicMaterial
          color={phaseColors[phase] || phaseColors.chaos}
          transparent
          opacity={0.1 + coherence * 0.1}
          side={THREE.BackSide}
        />
      </mesh>
    </group>
  )
}