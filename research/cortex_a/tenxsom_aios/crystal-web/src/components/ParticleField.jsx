import { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function ParticleField({ coherence, phase }) {
  const particlesRef = useRef()
  const particleCount = 1000
  
  // Create particle positions and velocities
  const [positions, velocities] = useMemo(() => {
    const pos = new Float32Array(particleCount * 3)
    const vel = new Float32Array(particleCount * 3)
    
    for (let i = 0; i < particleCount; i++) {
      // Random position in sphere
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      const radius = 5 + Math.random() * 5
      
      pos[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      pos[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      pos[i * 3 + 2] = radius * Math.cos(phi)
      
      // Random velocity
      vel[i * 3] = (Math.random() - 0.5) * 0.02
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.02
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.02
    }
    
    return [pos, vel]
  }, [])
  
  // Particle shader
  const shaders = useMemo(() => ({
    vertexShader: `
      attribute float size;
      varying vec3 vColor;
      uniform float coherence;
      uniform vec3 phaseColor;
      
      void main() {
        vColor = phaseColor;
        
        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
        gl_PointSize = size * (300.0 / -mvPosition.z) * coherence;
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      uniform float coherence;
      
      void main() {
        // Circular particle shape
        vec2 center = gl_PointCoord - vec2(0.5);
        float dist = length(center);
        
        if (dist > 0.5) discard;
        
        // Soft edges
        float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
        alpha *= coherence;
        
        // Glow effect
        vec3 color = vColor * (1.0 + (1.0 - dist) * 2.0);
        
        gl_FragColor = vec4(color, alpha);
      }
    `
  }), [])
  
  // Animation
  useFrame((state) => {
    if (!particlesRef.current) return
    
    const positions = particlesRef.current.geometry.attributes.position
    const sizes = particlesRef.current.geometry.attributes.size
    
    for (let i = 0; i < particleCount; i++) {
      // Update positions
      positions.array[i * 3] += velocities[i * 3]
      positions.array[i * 3 + 1] += velocities[i * 3 + 1]
      positions.array[i * 3 + 2] += velocities[i * 3 + 2]
      
      // Attract to center based on coherence
      const x = positions.array[i * 3]
      const y = positions.array[i * 3 + 1]
      const z = positions.array[i * 3 + 2]
      const dist = Math.sqrt(x * x + y * y + z * z)
      
      if (dist > 1) {
        const force = coherence * 0.001
        positions.array[i * 3] -= (x / dist) * force
        positions.array[i * 3 + 1] -= (y / dist) * force
        positions.array[i * 3 + 2] -= (z / dist) * force
      }
      
      // Update size based on distance and coherence
      sizes.array[i] = (1.0 - dist / 10.0) * 2.0 + Math.sin(state.clock.elapsedTime * 2 + i) * 0.5
    }
    
    positions.needsUpdate = true
    sizes.needsUpdate = true
    
    // Update uniforms
    particlesRef.current.material.uniforms.coherence.value = coherence
  })
  
  const phaseColors = {
    chaos: new THREE.Color(0x440044),
    emergence: new THREE.Color(0x004444),
    structuring: new THREE.Color(0x444400),
    crystallized: new THREE.Color(0x00ff44)
  }
  
  // Create size attribute
  const sizes = useMemo(() => {
    const s = new Float32Array(particleCount)
    for (let i = 0; i < particleCount; i++) {
      s[i] = Math.random() * 2 + 1
    }
    return s
  }, [])
  
  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={positions}
          count={particleCount}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-size"
          array={sizes}
          count={particleCount}
          itemSize={1}
        />
      </bufferGeometry>
      <shaderMaterial
        vertexShader={shaders.vertexShader}
        fragmentShader={shaders.fragmentShader}
        uniforms={{
          coherence: { value: coherence },
          phaseColor: { value: phaseColors[phase] || phaseColors.chaos }
        }}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  )
}