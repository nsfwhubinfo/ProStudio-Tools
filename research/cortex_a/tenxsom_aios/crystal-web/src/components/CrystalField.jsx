import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function CrystalField({ thoughtData, coherence, phase }) {
  const meshRef = useRef()
  const materialRef = useRef()
  
  // Convert thoughtData to texture
  const texture = useMemo(() => {
    if (!thoughtData) return null
    
    const size = Math.sqrt(thoughtData.length)
    const texture = new THREE.DataTexture(
      thoughtData,
      size,
      size,
      THREE.RedFormat,
      THREE.FloatType
    )
    texture.needsUpdate = true
    return texture
  }, [thoughtData])
  
  // Custom shaders for crystallographic visualization
  const shaders = useMemo(() => ({
    vertexShader: `
      varying vec2 vUv;
      varying float vElevation;
      uniform sampler2D thoughtTexture;
      uniform float time;
      uniform float coherence;
      
      void main() {
        vUv = uv;
        
        // Sample thought data
        vec4 thought = texture2D(thoughtTexture, uv);
        vElevation = thought.r;
        
        // Create crystal formation
        vec3 pos = position;
        float crystalHeight = thought.r * coherence * 2.0;
        
        // Add chaos for low coherence
        float chaos = sin(time + position.x * 5.0) * 0.1 * (1.0 - coherence);
        
        pos.y += crystalHeight + chaos;
        
        // Add subtle wave motion
        pos.x += sin(time * 0.5 + position.y * 2.0) * 0.02;
        pos.z += cos(time * 0.5 + position.x * 2.0) * 0.02;
        
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      varying vec2 vUv;
      varying float vElevation;
      uniform float coherence;
      uniform vec3 phaseColor;
      uniform float time;
      
      void main() {
        // Gamma ray visualization: brightness = fitness
        float gamma = pow(vElevation, 2.2);
        
        // Create energy field effect
        float energy = sin(vElevation * 20.0 + time) * 0.5 + 0.5;
        
        // Base color from phase
        vec3 color = mix(vec3(0.0), phaseColor, gamma);
        
        // Add gamma ray highlighting
        if (gamma > 0.7) {
          color = mix(color, vec3(1.0, 1.0, 0.0), (gamma - 0.7) * 3.0);
          // Add glow for high fitness
          color += vec3(1.0, 1.0, 0.5) * energy * (gamma - 0.7);
        }
        
        // Crystal clarity based on coherence
        float alpha = 0.8 + coherence * 0.2;
        
        gl_FragColor = vec4(color, alpha);
      }
    `
  }), [])
  
  // Animation
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002
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
    <mesh ref={meshRef} position={[0, 0, 0]}>
      <planeGeometry args={[10, 10, 64, 64]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={shaders.vertexShader}
        fragmentShader={shaders.fragmentShader}
        uniforms={{
          thoughtTexture: { value: texture },
          time: { value: 0 },
          coherence: { value: coherence },
          phaseColor: { value: phaseColors[phase] || phaseColors.chaos }
        }}
        transparent
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}